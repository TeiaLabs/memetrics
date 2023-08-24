export interface Actor {
    email: string;
    extra?: { [key: string]: any };
    ip?: string
}

export interface EventData {
    action: string;
    actor: Actor;
    extra?: { [key: string]: any };
    type: string;
}

export interface EventDataPayload extends EventData {
    app: string
}