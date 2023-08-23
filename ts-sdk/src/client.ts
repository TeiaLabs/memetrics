import { EventData } from "./schemas";
import { trimEnd } from "./utils";

export class Client {
    private apiKey: string;
    private apiUrl: string;

    constructor(
        apiKey: string | undefined = process.env["MEMETRICS_API_KEY"],
        apiUrl: string | undefined = process.env["MEMETRICS_URL"]
    ) {
        if (apiKey === undefined) throw Error("API Key not found.");
        this.apiKey = apiKey;

        if (apiUrl === undefined) throw Error("MeMetrics URL not found.");
        this.apiUrl = `${trimEnd(apiUrl, "/")}/events`;
    }

    saveEvent(event: EventData): Promise<void> {
        return fetch(this.apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authentication: this.apiKey,
                "X-User-Email": event["actor"]["email"],
            },
            body: JSON.stringify(event),
        }) as Promise<any> as Promise<void>;
    }

    saveBatch(events: EventData[]): Promise<void> {
        const promises = events.map((event) => {
            return this.saveEvent(event);
        });
        return Promise.all(promises) as Promise<any> as Promise<void>;
    }
}
