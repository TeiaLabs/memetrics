import os
import re
import pytz
import pandas as pd
import mysql.connector
import numpy as np

from datetime import datetime, timedelta
from decimal import *
from pandas.tseries.offsets import MonthEnd
from pydantic import BaseModel, EmailStr, Field, ValidationError
from pymongo import MongoClient
from tqdm import tqdm
from typing import Any, Dict, Literal


def pascal_to_snake(name):
    snake_case = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    return snake_case


class MongoDBDownloader:
    def __init__(self, key, period):
        self.client = MongoClient(key)
        self.period = period
        self.code_filters = None
        self.chat_filters = None
        self.jira_filters = None
        self.chrome_filters = None
        self.code_projection = None
        self.chat_projection = None
        self.jira_projection = None
        self.chrome_projection = None
        self.set_filters(period)
        self.set_projections()
        
    def __del__(self):
        self.client.close()
    
    def set_filters(self, period):
        self.code_filters = {
            "created_at": {'$gte': datetime.strptime(period, "%Y-%m-%d") - timedelta(days=1)},
            "$or":[
                {"type": "chat", "action": "display"},
                {"type": "completion", "action": "accept"},
                {"type": "explanation", "action": "display"},
                {"type": "bug_fix", "action": "request"},
                {"type": "docstring", "action": "display"},
                {"type": "optimization", "action": "display"},
                {"type": "unit_tests", "action": "display"}
            ]
        }

        self.chat_filters = {
            "created_at": {'$gte': datetime.strptime(period, "%Y-%m-%d")},
            "organization_name": {'$in': ['osf', 'OSF Digital', 'osfdigital']}
        }

        self.jira_filters = {
            "created_at": {'$gte': datetime.strptime(period, "%Y-%m-%d")},
            "type": {'$nin': [
                'teia.jira.description_stories', 
                'teia.jira.test_case_description', 
                'teia.jira.test_case_title',
                'teia.jira.generate_user_stories_description_v2',
                'teia.jira.description_portuguese_v2',
                'teia.jira.test_case_text_v2', 
                'teia.jira.test_case_title_v2',
                'teia.jira.test_case_description_v2',
                'teia.jira.description_summarize_v2'
            ]}
        }

        self.chrome_filters = {
            "created_at": {'$gte': datetime.strptime(period, "%Y-%m-%d") - timedelta(days=1)},
            "type": "chat.thread.message", 
            "action": "completion"
        }

    def set_projections(self):
        self.code_projection = {
            '_id': 0,
            'created_at': 1,
            'action': 1,
            'app': 1,
            'app_version': 1,
            'extra-value': 1,
            'user-email': 1,
            'type': 1,
        }

        self.chat_projection = {
            '_id': 0,
            'created_at': 1,
            'app_version': 1,
            'organization_name': 1,
            'user-email': 1,
            'app': 1
        }
        
        self.jira_projection = {
            '_id': 0,
            'created_at': 1,
            'app': 1,
            'app_version': 1,
            'extra-value': 1,
            'user-email': 1,
            'type': 1
        }
        
        self.chrome_projection = {
            '_id': 0,
            'action': 1,
            'app': 1,
            'app_version': 1,
            'created_at': 1,
            'type': 1,
            'user-email': 1,
        }
        
    def download_collection(self, db_name, collection_name):
        # Define the filters and projection according to the collection_name
        if collection_name == 'code-flat':
            filters = self.code_filters
            projection = self.code_projection
        elif collection_name == 'athena-flat':
            filters = self.chat_filters
            projection = self.chat_projection
        elif collection_name == 'jira-flat':
            filters = self.jira_filters
            projection = self.jira_projection
        elif collection_name == 'chrome-flat':
            filters = self.chrome_filters
            projection = self.chrome_projection
        else:
            raise ValueError("Invalid collection name")

        collection = self.client[db_name][collection_name]
        cursor = collection.find(filters, projection)
        df = pd.DataFrame([doc for doc in cursor])
        return df


class DataProcessor:
    @staticmethod
    def process_code_flat(df):
        df['created_at'] = pd.to_datetime(df['created_at']) + timedelta(hours=3)
        df['dateMonth'] = df['created_at'].dt.strftime("%Y-%m-01")
        df['dateDay'] = df['created_at'].dt.strftime("%Y-%m-%d")
        df['user-email'] = df['user-email'].str.lower()
        df['user-email'] = df['user-email'].str.replace("james.bruce@osf.digital", "james-richard.bruce@osf.digital", regex=False)
        df['user-email'] = df['user-email'].str.replace("rhea.duggal@osf.digital", "pallavi.duggal@osf.digital", regex=False)
        df['user-email'] = df['user-email'].str.replace("aissa.aldridge@osf.digital", "aissa.gequillo@osf.digital", regex=False)
        df['product'] = 'code'
        return df
    
    @staticmethod
    def process_chat_flat(df):
        df['dateMonth'] = df['created_at'].dt.strftime("%Y-%m-01") 
        df['dateDay'] = df['created_at'].dt.strftime("%Y-%m-%d")

        df['user-email'] = df['user-email'].str.lower()
        df['user-email'] = df['user-email'].str.replace("james.bruce@osf.digital", "james-richard.bruce@osf.digital", regex=False)
        df['user-email'] = df['user-email'].str.replace("rhea.duggal@osf.digital", "pallavi.duggal@osf.digital", regex=False)
        df['user-email'] = df['user-email'].str.replace("aissa.aldridge@osf.digital", "aissa.gequillo@osf.digital", regex=False)
        df['product'] = 'chat'
        return df
    
    @staticmethod
    def process_jira_flat(df):
        df['dateMonth'] = df['created_at'].dt.strftime("%Y-%m-01")
        df['dateDay'] = df['created_at'].dt.strftime("%Y-%m-%d")
        df['user-email'] = df['user-email'].str.lower()
        df['product'] = 'jira'
        return df
    
    @staticmethod
    def process_chrome_flat(df, period):
        # Add 3 hours in the creat_at attribute
        df['created_at'] = pd.to_datetime(df['created_at']) + timedelta(hours=3)
        df['dateMonth'] = df['created_at'].dt.strftime("%Y-%m-01") 
        df['dateDay'] = df['created_at'].dt.strftime("%Y-%m-%d")
        df['user-email'] = df['user-email'].str.lower()
        df['product'] = 'chrome'
        # Only consider events after the period and 2024-04-01
        df = df[
            (df['dateDay'] >= period) & (df['dateDay'] >= "2024-04-01") 
        ]
        return df


class EmployeeDataProcessor:
    # TODO: Download data from Zoho or Mongo

    @staticmethod
    def load_employee_from_file(filepath, period):
        employees_df = pd.read_excel(filepath)
        employees_df['dateMonth'] = pd.to_datetime(employees_df[['Year', 'Month']].assign(day=1))
        employees_df = employees_df[
            (employees_df['dateMonth'] >= period) &
            (employees_df['EmployeeStatus'] == 'Active') &
            (~employees_df["EmailID"].isin([
                "moodle2zoho@osf-global.com",
                "zoho2jira@osf.digital",
                "zohotest-veronique@osf.digital",
                "zoho2jira@osf-global.com"
            ]))
        ]
        employees_df['upn'] = employees_df['EmailID'].str.lower()
        return employees_df[['EmployeeID', 'upn', 'BasicRole', 'Country', 'DateofJoining', 'Department', 'Division', 'Experience', 'dateMonth']]


class ZohoDataProcessor:
    @staticmethod
    def define_zoho_leaves(cursor):
        cursor.execute(f"""
            SELECT 
                LOWER(u.user_name) AS upn, 
                DATE_FORMAT(wl.STARTDATE, '%Y-%m-01') AS month, 
                SUM(wl.timeworked / 3600) AS logged_hours
            FROM jiraissue ji
                JOIN worklog wl ON ji.id = wl.issueid
                JOIN app_user au ON wl.author = au.user_key
                JOIN cwd_user u ON au.lower_user_name = u.lower_user_name
                JOIN project p ON ji.PROJECT = p.ID 
            WHERE 
                wl.STARTDATE >= '2023-07-01' AND wl.STARTDATE < '{datetime.today().strftime('%Y-%m-%d')}' AND p.pkey = 'ZLH'
            GROUP BY upn, month
            ORDER BY upn, month
        """)
        zoho_leaves_holidays = pd.DataFrame(cursor.fetchall(), columns=['upn', 'dateMonth', 'logged_hours'])
        zoho_leaves_holidays['logged_days'] = zoho_leaves_holidays['logged_hours'] / Decimal('8.0')
        return zoho_leaves_holidays


class EmployeeMonthlyStatus(BaseModel):
    # keys
    employee_id: int
    employee_email: EmailStr = Field(alias="user_email")
    # dates
    date_of_joining: datetime
    date_month: datetime = Field(alias="dateMonth")
    # metadata
    basic_role: str
    country: str
    department: str
    division: str
    experience: str
    daily_events: Dict[str, Any] | float
    # apps
    chat: int
    chrome: int
    code: int
    jira: int
    # counts
    total_events: int
    working_days: int
    last_day: str
    logged_hours: float
    logged_days: float
    working_days_employee: float
    average_daily_usage: float | None = Field(alias="average daily usage")
    # computations
    status: (
        Literal[
            "N/A", "No AI Used", "Inactive user", "Casual user", "Active user", "Power user"
        ]
        | None
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(pytz.utc))

    def check_experience(cls, value, values):
        if value == 0.0:
            return ""
        return value

    @classmethod
    def collection_name(cls):
        return pascal_to_snake(cls.__name__)


def define_working_days(row):
    first_day = pd.to_datetime(row['dateMonth'])
    last_day = (pd.to_datetime(row['dateMonth']) + MonthEnd(0)).strftime('%Y-%m-%d')
    today = datetime.today()
    if first_day.year == today.year and first_day.month == today.month:
        last_day = pd.to_datetime(today - timedelta(days=1))

    if row['DateofJoining'].year == row['dateMonth'].year and row['DateofJoining'].month == row['dateMonth'].month:
        first_day = pd.to_datetime(row['DateofJoining']).strftime("%Y-%m-%d")

    working_days = pd.bdate_range(start=first_day, end=last_day).shape[0]
    return pd.Series([working_days, pd.to_datetime(last_day).strftime('%Y-%m-%d')])


def get_class(value):
    if value == 0:
        return 'No AI Used'
    elif 0 < value < 3:
        return 'Inactive user'
    elif 3 <= value < 8:
        return 'Casual user'
    elif 8 <= value < 15:
        return 'Active user'
    elif value >= 15:
        return 'Power user'
    else:
        return 'N/A'


def jira_connection():
    try: 
        conn = mysql.connector.connect(
            host="jiradb-reporting.ofactory.biz",
            database="jira",
            user=os.environ.get("JIRA_USER"),
            password=os.environ.get("JIRA_PASS"),
            port="3306"
        )
    except mysql.connector.Error as e:
        print(e)
        return
    
    return conn


def download_flats(period):
    downloader = MongoDBDownloader(os.environ["MONGODB_URI"], period)
    df_code = downloader.download_collection('memetrics', 'code-flat')
    df_code = DataProcessor.process_code_flat(df_code)
    df_code_grouped = df_code.groupby(['user-email', 'product', 'dateMonth', 'dateDay']).size().reset_index(name='events')
    print(f"Code data downloaded {df_code.shape[0]} events")

    df_chat = downloader.download_collection('memetrics', 'athena-flat')
    df_chat = DataProcessor.process_chat_flat(df_chat)
    df_chat_grouped = df_chat.groupby(['user-email', 'product', 'dateMonth', 'dateDay']).size().reset_index(name='events')
    print(f"Chat data downloaded {df_chat.shape[0]} events")

    df_jira = downloader.download_collection('memetrics', 'jira-flat')
    df_jira = DataProcessor.process_jira_flat(df_jira)
    df_jira_grouped = df_jira.groupby(['user-email', 'product', 'dateMonth', 'dateDay']).size().reset_index(name='events')
    print(f"Jira data downloaded {df_jira.shape[0]} events")

    df_chrome = downloader.download_collection('memetrics', 'chrome-flat')
    df_chrome = DataProcessor.process_chrome_flat(df_chrome, period)
    df_chrome_grouped = df_chrome.groupby(['user-email', 'product', 'dateMonth', 'dateDay']).size().reset_index(name='events')
    print(f"Chrome data downloaded {df_chrome.shape[0]} events")

    return pd.concat([
        df_code_grouped,
        df_chat_grouped,
        df_jira_grouped, 
        df_chrome_grouped
    ])


def calculate_avg_usage(df):
    df['code'] = df['code'].fillna(0)
    df['chat'] = df['chat'].fillna(0)
    df['jira'] = df['jira'].fillna(0)
    df['chrome'] = df['chrome'].fillna(0)
    df['total_events'] = df['total_events'].fillna(0)
    df['logged_days'] = df['logged_days'].fillna(0)
    df['logged_hours'] = df['logged_hours'].fillna(0)
    df['logged_days'] = df['logged_days'].astype(float)
    df['logged_hours'] = df['logged_hours'].astype(float)
    df['logged_days'] = df['logged_days'].apply(np.ceil)

    df['working_days_employee'] = df['working_days'] - df['logged_days']
    df['average daily usage'] = df['total_events'] / df['working_days_employee']
    df.loc[df['working_days_employee'] <= 0, 'average daily usage'] = np.nan
    
    df['status'] = df['average daily usage'].apply(get_class)
    df.loc[df['working_days_employee'] <= 0, 'status'] = np.nan
    df.loc[
        (df['working_days_employee'] <= 0), 'average daily usage'
    ] = 0.0
    df.loc[
        (df['working_days_employee'] <= 0), 'status'
    ] = "N/A"
    df.loc[
        (df['working_days_employee'] <= 0),
        'working_days_employee'
    ] = 0
    df.loc[
        (df['Experience'] == 0.0),
        'Experience'
    ] = ''
    df.loc[
        (df['Department'].isna()),
        'Department'
    ] = ''
    df.loc[
        (df['Division'].isna()),
        'Division'
    ] = ''
    df.rename(columns={
        'EmployeeID': 'employee_id',
        'upn': 'user_email',
        'BasicRole': 'basic_role', 
        'Country': 'country', 
        'DateofJoining': 'date_of_joining', 
        'Department': 'department', 
        'Division': 'division', 
        'Experience': 'experience'
    }, inplace=True)
    return df


def compute_allai_status(period):
    df = download_flats(period)
    df_daily = df.groupby(['user-email', 'dateMonth', 'dateDay'])['events'].sum().fillna(0).reset_index()
    df_daily['dateDay'] = pd.to_datetime(df_daily['dateDay'])
    df_daily['dateMonth'] = pd.to_datetime(df_daily['dateMonth'])
    daily_grouped = df_daily.groupby(['user-email', 'dateMonth']).apply(
        lambda x: dict(zip(x['dateDay'].dt.strftime('%Y-%m-%d'), x['events']))
    ).reset_index(name='daily_events')
    
    df_grouped = df.groupby(['user-email', 'dateMonth', 'product'])['events'].sum().unstack(2).fillna(0).reset_index()
    df_grouped['total_events'] = df_grouped[df['product'].unique()].sum(axis=1)
    df_grouped['dateMonth'] = pd.to_datetime(df_grouped['dateMonth'])
    df_grouped = df_grouped.merge(daily_grouped, on=['user-email', 'dateMonth'], how='left')
    df_grouped['daily_events'] = df_grouped['daily_events'].fillna(0)

    df_grouped.rename(columns={'user-email':'upn'}, inplace=True)

    employees_df = EmployeeDataProcessor.load_employee_from_file("../resources/osf_employees.xlsx", period)
    allai_report = employees_df.merge(
        df_grouped,
        on=['upn', 'dateMonth'],
        how='left'
    )
    allai_report[['working_days', 'last_day']] = allai_report.apply(define_working_days, axis=1)

    conn = jira_connection()
    zoho_leaves_holidays = ZohoDataProcessor.define_zoho_leaves(conn.cursor())
    zoho_leaves_holidays['dateMonth'] = pd.to_datetime(zoho_leaves_holidays['dateMonth'])
    allai_report = allai_report.merge(zoho_leaves_holidays, on=['upn', 'dateMonth'], how='left')
    return calculate_avg_usage(allai_report)


def main():
    if datetime.today().day == 1:
        period = (datetime.today() - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")
    else:
        period = datetime.today().replace(day=1).strftime("%Y-%m-%d")

    print(f"Start: {period}  End: {(datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')}\n")
    
    allai_report = compute_allai_status(period)
    client = MongoClient(os.environ["MONGODB_URI"])
    db = client["memetrics"]
    collection = db[EmployeeMonthlyStatus.collection_name()]

    for document in tqdm(allai_report.to_dict(orient='records')):
        try:
            obj = EmployeeMonthlyStatus(**document)
        except ValidationError as e:
            print(f"Error: {e}")
            print(document)
            break
        filter_query = {
            "employee_email": obj.employee_email,
            "date_month": obj.date_month
        }
        update_data = {"$set": obj.model_dump()}
        try:
            result = collection.update_one(filter_query, update_data, upsert=True)
        except Exception as e:
            print(f"Error updating document: {e}")
            print(document)
            break
    client.close()


if __name__ == "__main__":
    main()