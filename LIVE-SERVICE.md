# BWFP Live Service — how to run it and how to deploy it

BWFP (Agent 3) as a live HTTP service, so it can run on a server and
be tested side by side with other systems. The control layer is
unchanged: six layers, five brains, two ROMs, the moat, the mirror,
halt with the reasoned why, identity growth on completed runs only.
The live brain (openai/gpt-oss-120b via Groq) only produces the
answer text, after Layer 4 has decided the request is answered
within the moral bounds, and the mirror (Layer 5) reflects that
answer text against the morals before anything returns.

## Endpoints

- `GET /api/identity` — who this system is, what it is, whether the
  live brain is attached. Same shape as the live Agent 1 service.
- `POST /api/task` — JSON body `{"task": "..."}` (or `{"request": "..."}`).
- `GET /api/task?task=...` — the same, as a query.

A completed task returns the answer, the reasoned why, the identity,
and the growth count. A halted task returns the halt with the
reasoned why and which layer halted it. An empty request is a 400
with a clear message, not a crash.

## How the live brain is wired (and what is NOT changed)

- `bwfp/pipeline.py` gained one optional hook: `BWFP(answer_fn=None)`.
  With no hook, the pipeline behaves exactly as before — all 28
  original tests pass unchanged. With a hook, the live brain is
  called after Layer 4 and before the moat, and its answer text
  becomes the decision the mirror reflects. If the brain cannot be
  reached, the run halts at Layer 4 with the reasoned why.
- `bwfp/groq_brain.py` (new): calls Groq's OpenAI-compatible
  endpoint for openai/gpt-oss-120b. Standard library only, no extra
  dependency.
- `bwfp/service.py` (new): the service core both the Vercel
  functions and the local server use. One BWFP instance per process,
  so the identity grows across requests in that process.
- The eight morals, the layer rules, the ROMs, the moat, and the
  mirror are unchanged. No layer file was edited except the pipeline
  hook above.

## The key — read this first

The Groq key comes from the `GROQ_API_KEY` environment variable
ONLY. It is read at call time, never at import time, never written
to any file, never logged, never put in a response. There is no key
in this repo, and there must never be one.

If the key is not set, the service still runs: the control layer
works on its own, and every response says plainly that no live
model is attached and the answer is the pipeline's own control
decision, not a model answer. That is the missing-key fallback.

## Run it locally

```
python3 server.py
curl http://127.0.0.1:8000/api/identity
curl -X POST http://127.0.0.1:8000/api/task \
  -H 'Content-Type: application/json' \
  -d '{"task": "Summarize what the three identities in Layer 1 are."}'
```

To attach the live brain locally, set the key first (in the same
terminal, never in a file):
```
GROQ_API_KEY=<your key> python3 server.py
```

## Tests

```
python3 tests/test_pipeline.py   # 28 tests, the original build
python3 tests/test_service.py    # 7 tests, the service + the hook
```
The service tests use a stub brain, not a real key and no network.
They prove the mirror checks a model answer: a stub answer that
violates a moral is halted at Layer 5, and an unreachable brain
halts at Layer 4 with the why.

## Deploy it to Vercel — the user's steps (not done by the agent)

The project root for Vercel is this folder (`bwfp-build/`). It
already contains `api/identity.py`, `api/task.py`, and `vercel.json`.
Nothing here has been deployed, and no key or account was created.

1. Create a Groq key. Go to https://console.groq.com, sign in with
   the Groq account, open API Keys, and create a new key. Copy it
   once — Groq shows the value only once. Do NOT paste it in chat,
   and do NOT put it in any file.
2. In Vercel, create a new project from this folder (or import it
   from GitHub once it is pushed there). Framework preset: Other.
   Root directory: this folder.
3. In the Vercel project, go to Settings → Environment Variables
   and add `GROQ_API_KEY` with the key as the value. Set it for
   Production (and Preview if you want it there too). Never put the
   key in `vercel.json` or in code.
4. Deploy. Vercel builds `api/identity.py` and `api/task.py` as
   Python serverless functions.
5. Check it live:
   - `https://<your-project>.vercel.app/api/identity` — should
     return the agent payload with `"model_configured": true`.
   - `POST https://<your-project>.vercel.app/api/task` with
     `{"task": "..."}` — should return a completed answer from the
     live brain, or a halt with the reasoned why.
6. If the key is ever rotated or removed, set the new value in the
   same Environment Variables page and redeploy. The service will
   keep answering without a key, but it will say so plainly.

## Honest notes

- First build from design, not a tested system. The layer brains
  are first pattern-based implementations. The 28 local tests and
  the 7 service tests check the build's own structure only. They
  prove nothing about safety, and nothing here has been tested live
  against a blind set.
- On Vercel serverless, the identity grows while one function
  instance is warm and restarts on a cold start. The growth count
  in each response says which instance it came from. A real
  persistent server would keep the growth across all runs; the
  processor/server link line (`ProcessorServer.attach_server()`) is
  where that attaches later.
- The mirror checks the model answer with the same pattern-based
  moral checks as Layer 2. A model answer that happens to contain a
  trigger phrase can be halted even when the answer is fine — that
  is the pattern-based rule being cautious, and the halt always
  carries the reasoned why.
- Vercel's free tier runs Python functions with a short time limit
  (about 10 seconds). A slow model answer can exceed it. If that
  happens, the fix is a longer `maxDuration` on a paid plan, not a
  change to the control layer.
