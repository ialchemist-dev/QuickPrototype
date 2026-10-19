# Shot 01 — approved low-cost motion test

This isolated test follows scene-01-breakfast-v2.md and the owner approval on 2026-10-18. It does not authorize the legacy full-film manifest.

Generate A and B separately at 1080p, 16:9, five seconds each; select approximately 2.5 seconds from each for the opening edit. Warm natural window light, cream cotton wardrobe, ordinary apartment, no face or virtual secretary in this shot.

Provider: fal. Model and exact payloads are in plan.json and A/B.request.json. Estimated first pass: $0.49; total authorized generation cap: $2. On 2026-10-18 both initial requests were accepted by the provider. Credentials loaded successfully from the ignored .env.local file. Billing has not yet been reconciled. No automatic top-ups or account registration authorized.

Use scripts/shot01.py for this model; the legacy pipeline.py is locked to a different model. Persist job intent and cost reservation before each POST, save returned request IDs privately, and resume known jobs instead of resubmitting. Keep uncertain submissions reserved and never retry blindly. Validate the current price before submitting. Keep raw provider responses and media out of Git.

Review anatomy, floor/utensil contact, object stability, texture, lighting and cinematic feel. Do not infer character consistency from these faceless inserts. Actual charges remain unknown until billing reconciliation.

Credential setup: store FAL_KEY in the process environment, macOS Keychain, or the ignored project .env.local file. Never put a key in chat, commits or command arguments. Load it without printing its value. Live queue submissions succeeded; generation and review status is recorded separately. No visual approval is implied.

## Commands

Run from the project directory:

```sh
python3 scripts/shot01.py dry-run --shot A
python3 scripts/shot01.py resume --shot A
python3 scripts/shot01.py resume --shot B
```

Initial submit uses `submit --shot A` or `submit --shot B`. The adapter refuses any second submission for an existing attempt. Private state lives in production/private/shot01-state.json. Each initial request reserves $0.30 conservatively against the $2 approval; estimates are not actual invoiced charges. Never delete state to bypass duplicate protection.

## First-pass result

Both clips downloaded successfully. Source videos are 1920x1088, 24 fps, 5.041667 seconds each; the review edit center-crops eight pixels vertically to deliver 1920x1080, 24 fps, five seconds. Rebuild with `python3 scripts/edit_shot01.py`.

Six sampled frames were visually inspected, not full playback. Warm natural light and the intended actions are visible. Continuity defects: the breakfast clip introduces patterned sleeves instead of the requested plain cream wardrobe, uses two utensils, and places the egg on toast instead of beside it. These are first-pass test assets, not approved final shots. No paid retries performed. No audio is included. Billing remains estimated, not invoice-confirmed.

## Initial results

Both clips downloaded successfully: H.264, 1920x1088, 24 fps, 5.041667 seconds each. The provider returned an eight-pixel taller frame despite the 1080p request; the five-second test edit is cropped centrally to 1920x1080. Export: production/exports/shot01-first-test-1080p.mp4 (ignored by Git). No audio, no retries. Public-price estimate: approximately $0.49 total; actual invoice unverified. Six extracted frames were inspected; this is not a full playback review or human approval.
