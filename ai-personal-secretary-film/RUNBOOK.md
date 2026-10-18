# Production operator runbook

The project README remains the creative and approval source of truth. This file documents the implemented milestone, not an authorization to spend.

## Current state

- Local schematic animatic, 143s, 1920×1080/24 fps, H.264/AAC; 23 scratch spoken lines, original temp score, SRT.
- 19 prompt files and five reference briefs; photoreal references and pilot footage NOT generated.
- 28 additional jobs planned (5 reference masters + 23 voice lines); all jobs unsubmitted.
- Proposed fal Seedance 2.5 US 1080p. Access and face permissions unverified; no API key discovered in scoped checks.
- G0/G1/G2/G3 are unapproved. Spend is $0.00. No signup, provider message, external order, or publication performed.

## Reproduce free preparation

Use existing Python 3, Pillow, numpy, FFmpeg, ffprobe and macOS `say`. Exact detected versions are in `production/environment.json`. `requirements.txt` lists needed packages; no install was necessary on this Mac. The scratch voice renderer is macOS-specific; another OS needs explicit replacement voice recordings.

```sh
cd ai-personal-secretary-film
python3 -m unittest discover -s tests -v
python3 scripts/pipeline.py validate
python3 scripts/budget.py
python3 scripts/animatic.py
python3 scripts/qc.py production/exports/animatic_1080p_24fps.mp4
python3 scripts/serve.py
```

Open http://127.0.0.1:8766/review.html. Media stays local and Git-ignored. The renderer caches local speech by text/voice/rate hash and final animatic by script/storyboard fingerprint. `prepare.py` is a one-time bootstrap and refuses to overwrite an existing manifest. `plan_assets.py` is idempotent and only registers plans. Update creative changes deliberately, renew hashes and approvals; never reset a live manifest to work around a guard.

## Paid phase (only after owner authorization)

1. Confirm account can access the exact US model, native 1080p and fictional photoreal faces. Resolve any onboarding/ACR/terms directly with owner approval; do not register accounts or send a sales inquiry autonomously. Recheck price within seven days of a request. If access fails, stop and request a provider change; no regional bypass.
2. Set `FAL_KEY` locally in the process environment; never paste it into a chat, command argument, README or commit. Scripts do not load `.env` automatically and never print it.
3. Copy `production/approvals.example.json` to ignored `production/approvals.local.json` and fill it only from actual owner decisions and provider verification. G0 proposal: $600 total ceiling and $110 pilot ceiling (including reference/voice costs); this does not authorize remaining video before G2.
4. Submit R01 first, then R02/R03/R04; review and lock R01/R02 before R05 edit. Approved reference map shape: `{"R01":{"approved":true,"path":"production/references/file.png","sha256":"...","evidence":"owner approval"}}`. Do not use schematic boards as face references. Seedream is a proposed paid reference service; no generated images exist yet.
5. Lock approved reference hashes on every shot, review a photoreal-still animatic, and record the owner's G1 reference/animatic sign-off plus the value of `creative-hash`. The current schematic animatic supports direction/timing review; it cannot substitute for approval of an unseen face sheet.
6. Submit exactly 02, 07, 14, 18 for the pilot. The pipeline blocks all other video until G2 and approved pilot statuses. Owner watches/listens to pilot and confirms remaining budget before those statuses or G2 are set.

```sh
python3 scripts/pipeline.py dry-run --shot 02     # always offline
python3 scripts/pipeline.py submit --shot 02      # gated; sends one paid request
python3 scripts/pipeline.py resume --shot 02      # poll/download existing job only
python3 scripts/pipeline.py cost
python3 scripts/pipeline.py record-cost --shot 02 --usd 8.15 --invoice YOUR_BILLING_REFERENCE
```

`record-cost` uses the actual billed amount, not this example. Never mark costs actual based on a list-price estimate. Unknown costs remain reserved. No automatic POST retries exist. On timeout, an intent remains `uncertain`; recover its job ID/status URLs from the provider dashboard and reconcile. A local idempotency key does not promise server deduplication. Preserve every attempt and its output. To deliberately retry a rejected/failed completed attempt after billing is known:

```sh
python3 scripts/pipeline.py prepare-retry --shot 02 --reason 'Reviewed hand anatomy failure; billing reconciled'
```

Then `submit` rechecks caps/approvals. No retry is allowed for unknown/submitting/submitted outcomes or an approved final shot. Atomic writes and a process lock prevent concurrent double-submission. Any actual unexpected overspend requires an immediate pause and revised approval; configure provider-side spend limits too where available.

## Final phase

Generated clips download as `rendered`, never `approved`. Record actual viewing findings in shot QC notes and the pilot review template. Audition proposed original stock voices (Rachel secretary / Aria Alex), verify licenses and retime canonical lines. Voice ID choices are provisional. Store final music/ambience/voice provenance in `credits_and_licenses.md`. Final sound mixing, shot-04 reminder compositing and final clip-specific edits remain asset-dependent.

`assemble.py` requires approved footage and an approved licensed `production/audio/final_mix.wav`, plus `final_audio_approval.local.json` containing `approved`, `license_evidence`, and `caption_timing_verified`. It refuses scratch substitution and low-resolution clips. `qc.py` checks the export; actual full viewing/listening and final true-peak/loudness verification remain mandatory. No upload/publishing function exists.

## Honest verification scope

Tests cover timeline/hash invariants, missing approval/access/reference guards, spend caps, stale approval, full-render gate, write-before-submit, ambiguous timeout duplicate prevention, job-ID persistence, cost reservations, local title exemption and credential host restriction. Network calls are mocked. No live provider round trip is claimed. The local animatic was rendered and technically probed; full audiovisual human review is pending.
