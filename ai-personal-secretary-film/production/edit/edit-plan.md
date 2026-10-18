# Edit and sound plan

143 seconds, 19 shots, 1920×1080, 24 fps. Changes from canonical 138 seconds: shot 05 +2s (purchase deferral), 07 +1s (coffee consent), 14 +2s (trade-off and human values). No other durations changed. 139 generated seconds; final 4-second card is local.

## Sound

Separate tracks: Alex dialogue, secretary dialogue, room/street/cafe/rain/dinner ambience, kettle/footstep/cup/bag/ring Foley, understated original score. Ring tap is a tiny physical touch, not a sci-fi activation chime. AI voice has light room presence but remains clear; not a corporate announcer. Dialogue precedes confirmed coffee pickup, while gift and work-message outcomes are not asserted prematurely.

Free animatic uses local macOS speech at 170 wpm, with leading/trailing near-silence removed, 0.22s between speakers and at least 0.5s shot margin. It does NOT accelerate or truncate speech. Timing output records actual scratch-line lengths. Final voices must be retimed, not assumed equal to scratch. SRT contains exactly the canonical spoken words; speakers remain in the timing metadata.

Original temporary score uses slow open fifths and a soft synthesized room texture. It is a timing aid, not finished Foley. In the final mix, hand-author or record natural ambience and use a two-pass FFmpeg loudnorm target around -16 LUFS stereo / true peak <= -1.5 dBTP, adjust by listening. Leave the last line intimate, not inaudible. Technical QC currently measures sample peak, not true peak; final loudness verification remains required.

## Picture

Cuts preserve scene order. J/L cuts can shift final dialogue over adjacent images without changing wording; reflect those shifts in final cue timing. Required local compositing: static handwritten reminder in 04; blank gift-option card art in 17 if generation is illegible; end card in 19. Do not export these required details as generative gibberish. Video submission may generate blank cards; compositing/tracking must be checked on actual footage.

`assemble.py` conforms only reviewed/approved clips, refuses missing/short footage and resolution downgrades, rejects absent licensed final audio, and never falls back to animatic footage. It fades the last live-action shot into the title. Current assembler is a scaffold: shot-04 tracking/compositing, final cue alignment, final Foley, and final loudness pass await generated assets. No final master or review film exists yet.
