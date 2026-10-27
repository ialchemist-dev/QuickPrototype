# A1 breakfast — first reference-guided motion test

Date: 2026-10-26. Owner selected A1 and instructed continuation after previously approving the revised character test under a combined USD 2 ceiling, including prior USD 0.45 reported video spend and up to USD 0.05 OpenAI TTS.

The starting image was created with the built-in image tool using the left A1 panel of the approved casting board. Request: preserve A1's facial identity and dark wavy hair; place her alone at an oak breakfast table with a ceramic mug, eggs and toast; ivory blouse; eye-level medium close-up; soft morning window light; no extra people or labels. Output copied to production/references/casting/a1-breakfast-v1.png, retained outside Git. Image-tool billing is not exposed here; do not report it as verified free or include it as a known fal charge.

Uses the same fal provider and Seedance 1.0 Pro Fast model as the approved test, now with its image-to-video endpoint. Price checked at the source in plan.json: approximately USD 0.243 for five seconds at 1080p. Private state reserves USD 0.30; prior character render reserves USD 0.30 pending billing; prior owner-reported spend USD 0.45; TTS reserve USD 0.05. Total video/TTS committed or reserved: USD 1.10, not a finalized invoice.

Commands:

```sh
python3 scripts/a1_breakfast.py dry-run
python3 scripts/a1_breakfast.py resume
```

Submission has already occurred. The script refuses duplicate submissions. Private job state: production/private/a1-breakfast-v1-state.json. Reference is sent as an inline image, not published via a public gallery. No OpenAI speech was generated: key remains absent. This test deliberately isolates face stability with a blink, small gaze shift and fixed camera.

The source portrait remains the identity authority. A generated starting frame and any sampled video frames require visual review; do not imply exact identity preservation or full human approval.
