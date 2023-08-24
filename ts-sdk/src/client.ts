import { EventData, EventDataPayload } from "./schemas";
import { trimEnd } from "./utils";
import fetch from "node-fetch";

export class Client {
    private static apiKey: string;
    private static apiUrl: string;
    private static appName: string;

    static setup(
        appName: string,
        apiKey: string | undefined = process.env["MEMETRICS_API_KEY"],
        apiUrl: string | undefined = process.env["MEMETRICS_URL"]
    ) {
        if (apiKey === undefined) throw Error("API Key not found.");
        this.apiKey = apiKey;

        if (apiUrl === undefined) throw Error("MeMetrics URL not found.");
        this.apiUrl = `${trimEnd(apiUrl, "/")}/events`;

        this.appName = appName;
    }

    static saveEvent(event: EventData): Promise<void> {
        let payload = event as any as EventDataPayload;
        payload.app = this.appName;

        return fetch(this.apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authentication: this.apiKey,
                "X-User-Email": event["actor"]["email"],
            },
            body: JSON.stringify(payload),
        }) as Promise<any> as Promise<void>;
    }

    static saveBatch(events: EventData[]): Promise<void> {
        const promises = events.map((event) => {
            return this.saveEvent(event);
        });
        return Promise.all(promises) as Promise<any> as Promise<void>;
    }
}
