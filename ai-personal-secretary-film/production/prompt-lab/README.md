# Offline casting and prompt trial

Run `python3 scripts/compile_prompt_lab.py` from the film project folder. It compiles reviewed structured briefs into English casting prompts and a motion draft. This is deterministic preparation, not an installed LTX/Wan optimizer, an LLM evaluation or a video-quality benchmark. No network requests or paid generation occur.

See prompt-pack.md for three written casting directions. Common portrait framing, expression, light, wardrobe and background are held constant; facial features, hair and makeup vary deliberately. These are proposed aesthetic directions, not approved identities. No claim that one is objectively more beautiful.

Compared with the rejected video prompt:
- Replace an unspecified beauty adjective with reviewable face, hair and makeup descriptions.
- Separate casting from the motion prompt; no further face lottery inside a video request.
- Replace the high off-camera gaze with a point just beside the lens at eye level.
- Use a single planned static camera instead of automatically adding movement.
- Keep one visible person; do not imply another physical person nearby.
- Keep speech and sound effects in the edit plan, separate from silent model input.

Next gate: owner selects/adjusts a casting direction. Still generation requires a concrete provider and price within an explicitly approved scope. No image-generation provider is currently authorized by this trial. After a portrait is approved, verify a suitable I2V endpoint and its pricing before motion generation. The existing text-to-video endpoint cannot bind this proposed reference.

Quality evaluation remains pending. Text-only compilation cannot validate face consistency, anatomy, beauty, or video quality. No paid calls were made.

## Selected direction

On 2026-10-20 the owner selected A — Warm romantic lead. Use the adult 28-year-old character, long dark loose waves, soft oval features, peach-toned makeup and relaxed smile. The face reference remains unselected. No new generation or spending occurred when recording this choice.

## Approved portrait — 2026-10-26

Owner selected A1, the left portrait in production/references/casting/warm-romantic-a1-a3-v1.png. Treat only that panel as the identity reference. The casting board supersedes the earlier no-image/no-selection status. Do not feed the full three-person board to a motion model as if all three were cast. Preserve the selected face, dark wavy hair and warm natural styling. No additional generation was performed when recording this selection.
