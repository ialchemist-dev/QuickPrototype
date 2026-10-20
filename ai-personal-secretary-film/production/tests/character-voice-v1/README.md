# Character and voice test — preparation

Status: proposed; no new image, video or TTS call submitted.

Character: fictional adult East Asian woman, 28, attractive and approachable; shoulder-length dark hair, brown eyes, natural skin texture, understated makeup, cream cotton pajama set. The film remains AI-generated; this is a photorealistic character, not footage of a hired human actor. Lock an approved reference before producing the full scene.

Proposed picture: retain the five-second waking/breakfast inserts, add a five-second face-visible breakfast shot from video-prompt.txt. Begin dialogue only once she is seated and addressing the secretary. Put the spoken line over a breakfast cutaway as a J-cut/voice bridge; TTS does not animate lips. A front-facing speaking performance requires a separately scoped lip-sync workflow.

Audio: synthesize the English line using OpenAI /v1/audio/speech into WAV. Keep voice, room tone and Foley as separate files. Measure voice length before choosing the final edit; do not truncate the sentence to fit five seconds. Resample to 48 kHz for editing, place dialogue centrally, duck ambience under speech, and add only subtle room reverb. Export 1080p H.264/AAC and preserve a clean dialogue stem. Include AI-generated image/voice disclosure in the review description and final credits.

The current local synthesized Foley remains provisional. TTS creates speech; it does not replace footsteps, ceramic contact or room ambience.

Credential check: OPENAI_API_KEY was absent from the process environment and project .env.local on 2026-10-19. Existing fal key must be preserved when adding it. Proposed TTS provider/model requires a scoped budget approval under the owner's standing spending rule. Existing $2 approval was for the original Seedance opening test only; do not silently expand to other models or services.

Sources checked: https://developers.openai.com/api/docs/guides/text-to-speech and https://developers.openai.com/api/docs/models/gpt-4o-mini-tts . The guide supports the speech model and tone instructions; the model catalog also displays deprecation labeling, so recheck endpoint availability before any paid request and never silently substitute another model.
