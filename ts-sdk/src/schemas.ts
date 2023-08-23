export interface Actor {
    email: string;
    extra?: { [key: string]: any };
    ip?: string
}

export interface EventData {
    action: string;
    actor: Actor;
    app: string;
    extra?: { [key: string]: any };
    type: string;
}
