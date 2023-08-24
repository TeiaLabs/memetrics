import { EventData } from "./schemas";
export declare class Client {
    private static apiKey;
    private static apiUrl;
    private static appName;
    static setup(appName: string, apiKey?: string | undefined, apiUrl?: string | undefined): void;
    static saveEvent(event: EventData): Promise<void>;
    static saveBatch(events: EventData[]): Promise<void>;
}
