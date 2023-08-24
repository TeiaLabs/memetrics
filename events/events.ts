
// user clicks on new chat
// user writes message (no event needed)
// user clicks on send
// chat-athena POST /ask on athena-api
// athena-api POST /chat-completions on melting-face
// melting-face calls openai.ChatComplete.create on openai-sdk
// response is streamed back through each hop

const b = [
    { // chat-athena {client_name: "/teialabs/athena/web", token_name: "chat-athena.prod"}
        action: "new-chat.button.click",
        actor: {email: "user@org.com"},
        app: "web.osf.chat-wingman",
        extra: {user_agent: "firefox-116"},
        type: "chat.landing-page.sidebar",
    },
    { // chat-athena {client_name: "/teialabs/athena/web", token_name: "chat-athena.prod"}
        action: "send-message.button.click",
        actor: {email: "user@org.com"},
        app: "web.osf.chat-wingman",
        extra: {user_agent: "firefox-116"},
        type: "chat.thread",
    },
    { // chat-athena {client_name: "/teialabs/athena/web", token_name: "chat-athena.prod"}
        action: "chatbot.request",
        actor: {email: "user@org.com"},
        app: "web.osf.chat-wingman",
        extra: {user_agent: "firefox-116"},
        type: "chat.thread",
    },
    { // athena-api {client_name: "/teialabs/athena", token_name: "athena.prod"}
        action: "create_one",
        actor: {
            email: "user@org.com", extras: {
                creator: {client_name: "/teialabs/athena/web", token_name: "chat-athena.prod"}
            }
        },
        app: "webservice.teia.athena",
        type: "threads.ask",
    },
    { // melting-face {client_name: "/teialabs/melt", token_name: "meltingface.prod"}
        action: "stream_one",
        actor: {email: "user@org.com", extras: {creator: {client_name: "/teialabs/athena", token_name: "athena.prod"}}},
        app: "webservice.teia.melting-face",
        type: "chat-completions",
    }
]
