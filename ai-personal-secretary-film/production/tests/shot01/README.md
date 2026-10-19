# Shot 01 — approved low-cost motion test

This isolated test follows scene-01-breakfast-v2.md and the owner approval on 2026-10-18. It does not authorize the legacy full-film manifest.

Generate A and B separately at 1080p, 16:9, five seconds each; select approximately 2.5 seconds from each for the opening edit. Warm natural window light, cream cotton wardrobe, ordinary apartment, no face or virtual secretary in this shot.

Provider: fal. Model and exact payloads are in plan.json and A/B.request.json. Estimated first pass: $0.49; total authorized generation cap: $2. No paid call has been made. Account access and billing remain unverified because no credential was found. No automatic top-ups or account registration authorized.

Before submission, use a dedicated adapter for this model: the legacy pipeline.py is locked to a different model. Persist job intent and cost reservation before each POST, save returned request IDs privately, and resume known jobs instead of resubmitting. Keep uncertain submissions reserved and never retry blindly. Validate the current price before submitting. Keep raw provider responses and media out of Git.

Review anatomy, floor/utensil contact, object stability, texture, lighting and cinematic feel. Do not infer character consistency from these faceless inserts. Actual charges remain unknown until billing reconciliation.

Credential setup: store FAL_KEY in the process environment, macOS Keychain, or the ignored project .env.local file. Never put a key in chat, commits or command arguments. Load it without printing its value. This package contains preparation only; no API integration test or visual review has yet occurred.
