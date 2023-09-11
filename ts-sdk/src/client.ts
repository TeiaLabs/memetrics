import { EventData, EventDataPayload, Error } from "./schemas";
import { stripStart, stripEnd } from "./utils";
import axios, { AxiosError } from "axios";

export class Client {
    private static apiUrl: string;
    private static appName: string;

    static setup(
        appName: string,
        apiKey: string | undefined = process.env["MEMETRICS_API_KEY"],
        apiUrl: string | undefined = process.env["MEMETRICS_URL"]
    ) {
        if (apiKey === undefined) throw Error("API Key not found.");
        apiKey = `Bearer ${stripStart(apiKey, "Bearer ")}`;

        if (apiUrl === undefined) throw Error("MeMetrics URL not found.");
        this.apiUrl = `${stripEnd(apiUrl, "/")}/events`;

        this.appName = appName;

        axios.defaults.headers.common["Content-Type"] = "application/json";
        axios.defaults.headers.common["Authorization"] = apiKey;
    }

    static async saveEvent(event: EventData): Promise<void | Error> {
        let payload = event as any as EventDataPayload;
        payload.app = this.appName;

        try {
            await axios.post(this.apiUrl, payload, {
                headers: {
                    "X-User-Email": event["user"]["email"],
                },
            });
        } catch (e: any) {
            const error = e as AxiosError;
            let status, message, extra;
            if (error.response) {
                status = error.response.status;
                message = `MeMetrics API responded with ${error.response.status} ${error.response.statusText}`;
                extra = error.response.data;
            } else {
                status = 500;
                message = `MeMetrics API responded with ${error.message}`;
            }

            return { status, message, extra } as Error;
        }
    }

    static saveBatch(events: EventData[]): Promise<(void | Error)[]> {
        const promises = events.map((event) => {
            return this.saveEvent(event);
        });
        return Promise.all(promises);
    }
}
