# kid-a

Talk to the [organic-learning](https://github.com/harrisonford/organic-learning) brain, frozen at each level of schooling it has passed.

The brain learns without backpropagation:
- clusters of neurons grow when nothing has affinity to the problem;
- it hears raw bytes and sees through a moving eye;
- it speaks one sound unit at a time.

It is taught in order, as a child is: echo, first words, two words, preschool, kindergarten, first grade... It moves on only when it masters a stage and still holds the earlier ones. Every time it passes a stage, that brain is frozen and released here as a level.

| level | like a | what it does |
|---|---|---|
| see `levels/*.json` | | each card lists what it can and cannot do, and its held-out scores |

## Run

```
python server.py            # http://<tailscale ip>:8787; public via Tailscale Funnel on :10000
```

- `web/`: the chat app (Svelte 5 + Vite). `cd web && npm install && npm run build` writes `static/`, which the server serves. `npm run dev` proxies `/api` to a running server.
- `server.py`: standard-library HTTP server. `GET /api/levels`, `POST /api/chat {level, text, image}`. Answers come from the frozen brain (`learn=False`).
- `release.py <candidate>`: freezes a brain that passed a stage into `models/<level>.pkl` (not in git, large) and writes its card `levels/<level>.json`.
- `systemd/kid-a.service`: a user service.

There is no database: chats live in the browser (localStorage). Pictures are seen as the brain sees them: center-cropped to 64x64.

Public URL (Tailscale Funnel, port 10000; 443 and 8443 serve other apps): https://arch-server.tail2d89ff.ts.net:10000. There is no login.
