# Provider research — checked 2026-10-18

## Recommendation and unresolved access

Prefer **fal / `bytedance/seedance-2.5/us/reference-to-video`**, native 1080p, explicit 16:9 and integer shot duration, images-only references, native audio disabled. This preserves the user's Seedance preference and provides a US-specific endpoint. Model version is an alias, not an immutable weight revision. No authenticated request, account signup, payment, or generation has been performed. Account eligibility, permitted fictional photoreal faces, any ACR requirement and billing must be confirmed before enabling paid jobs. Presence of a public API page is not proof this particular account can use it.

The US model's [current schema](https://fal.ai/models/bytedance/seedance-2.5/us/reference-to-video/api) supports 4–30 second output and 480p/720p/1080p. It allows up to 30 image, 10 video and 10 audio references, 50 total. Still references suit our short shots; video references add input-duration billing and are unnecessary here. Seeds aid repeatability but do not guarantee identical output. Our adapter uses the documented @Image references, not the older marketing-page syntax.

[US endpoint pricing](https://fal.ai/models/bytedance/seedance-2.5/us/reference-to-video) lists approximately $0.2205/s at 480p, $0.4730/s at 720p and $1.164/s at 1080p. Token rates are $0.0214/1,000 at lower resolutions and about $0.0234/1,000 at 1080p. The approximate formula is pixels × (input video seconds + output seconds) × 24 / 1,024. Video reference input applies a 0.6 multiplier to both input and output seconds. We budget $1.165/s, no video inputs, and reserve the higher advertised second-based figure rather than the slightly smaller exact 1920×1080 token calculation. Reconfirm the billed rate before G0 execution; reconciliation uses invoices, not guesses.

## Latest model / documentation discrepancies

[Seedance 2.5's landing page](https://fal.ai/seedance-2.5), last updated August 12, still describes output only through 720p. The current US endpoint schema explicitly includes 1080p; schema is the implementation source, but a pilot must verify actual output dimensions. Do not silently upscale a rejected 1080p request or substitute another endpoint.

[Seedance 2.0 standard reference endpoint](https://fal.ai/models/bytedance/seedance-2.0/reference-to-video) lists roughly $0.3034/s at 720p and $0.682/s at 1080p, with 4–15 second shots in its [schema](https://fal.ai/models/bytedance/seedance-2.0/reference-to-video/api). This is not a US price quote. [2.0 US hosting guidance](https://fal.ai/seedance-2.0-us-hosting) describes company-only onboarding, custom pricing, 480p/720p and separately approved face/IP permissions. It says US customers must transition to US hosting. Those 2.0 requirements cannot simply be presumed identical for 2.5; obtain account-specific confirmation. No geographic workaround is proposed.

[BytePlus's current creation documentation](https://docs.byteplus.com/en/docs/modelark/create-video-generation-task-api?redirect=1) lists Seedance 2.5 and the ap-southeast API, with activation funding requirements. Its [pricing page](https://docs.byteplus.com/en/docs/modelark/model-pricing?redirect=1) is dynamic and did not fully render in direct fetch. Direct US account eligibility and fictional-face rights were not established, so it is not selected. No need to switch model families before resolving the preferred provider's access. If access fails, compare a US-accessible alternative and request a new approval rather than auto-falling back.

## Supporting services

- [Seedream 4.5 text-to-image](https://fal.ai/models/fal-ai/bytedance/seedream/v4.5/text-to-image) and [edit](https://fal.ai/models/fal-ai/bytedance/seedream/v4.5/edit): $0.04 per output image. Plan five masters, derived crops and shot keyframes, allowing 60 generated/edit outputs total ($2.40). This is a budgeted plan, not generated references.
- [ElevenLabs Multilingual v2 through fal](https://fal.ai/models/fal-ai/elevenlabs/tts/multilingual-v2): $0.10/1,000 characters. Canonical spoken text currently totals 889 characters. Five full takes cost about $0.45; reserve $1 including voice auditions. Use distinct stock voices with appropriate commercial permission, not cloned personal/public-figure voices. Voice IDs await audition.
- Editing, local storyboard drawing, temporary speech and original synthesized temporary score: $0 API cost. No stock music subscription, cloud storage account, or separate upscaler required. Final music direction remains reviewable; no unlicensed commercial recording is used.
- No separate per-download charge was established on these model pages. Budget a contingency for taxes, provider minimum deposits, egress or price drift; do not claim those are zero or silently spend above the cap.

## Commercial and content rights

Model pages label commercial use through partner terms. [fal Terms of Service](https://fal.ai/legal/terms-of-service), retrieved today, require lawful, non-infringing inputs and use; outputs are not guaranteed original or exclusive, and the provider disclaims non-infringement warranties. Commercial-use labeling is not a blanket IP clearance or proof of copyright ownership. Use fictional consenting-adult-style characters, original prompts and score, no logos, no celebrity likeness/voice, and obtain the account's required human-face permissions. Keep provenance and license evidence. No distribution permission is inferred from production approval.

## Execution design

Use [fal asynchronous queue](https://fal.ai/docs/documentation/model-apis/inference/queue): persist intent and budget reservation first; submit once; save returned job ID/status/response URLs; reconcile rather than recreate. A local idempotency key is bookkeeping, NOT a claim of server-side deduplication. Ambiguous submissions remain reserved and block retries. Never log credentials, data URIs or raw provider errors. Actual costs remain unknown until billing reconciliation.
