export interface Attribute {
    name: string;
    type: "string" | "integer";
    value: string;
}
export interface User {
    id?: string;
    email?: string;
    extra?: Attribute[];
}
export interface EventData {
    action: string;
    app_version: string;
    user: User;
    extra?: Attribute[];
    type: string;
}
export interface EventDataPayload extends EventData {
    app: string;
}
export interface Error {
    status: number;
    message: string;
    extra?: any;
}
