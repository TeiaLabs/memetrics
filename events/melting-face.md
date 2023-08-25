# Melting face API events

## /text-generation/chat-completions

```js
{
    action: "create_one",
    app: "teia.melting-face.webservice",
    extra: {token_usage: {...}, id: "123"},
    type: "/text-generation/chat-completions/stream",
    user: {email: "user@org.com", extra: {"user-id"}},
}
{
    action: "read_one",
    app: "teia.melting-face.webservice",
    extra: {params: {...}},
    type: "/text-generation/chat-completions",
    user: {email: "user@org.com", extra: {"user-id"}},
}
```

```js
{
    action: ["create_one"],
    app: ["teia.melting-face.webservice"],
    extra: {token_usage: {...}},
    type: ["/text-generation/chat-completions/stream"],
    user: {email: "user@org.com", extra: {"user-id"}},
}
```

## /text-generation/text-completions

```js
{
    action: "create_one",
    app: "teia.melting-face.webservice",
    extra: {token_usage: {...}},
    type: "/text-generation/text-completions",
    user: {email: "user@org.com", extra: {"user-id"}},
}
{
    action: "read_one",
    app: "teia.melting-face.webservice",
    extra: {params: {...}},
    type: "/text-generation/text-completions",
    user: {email: "user@org.com", extra: {"user-id"}},
}
```
