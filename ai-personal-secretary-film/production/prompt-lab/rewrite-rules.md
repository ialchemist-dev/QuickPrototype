# Seedance prompt preparation rules — v1

Original project-specific rules informed by source inspection; not a copied upstream system prompt or a trained optimizer. No model inference is required by the local compiler.

Sources:
- https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-core/src/ltx_core/text_encoders/gemma/encoders/prompts/gemma3_i2v_system_prompt.txt
- https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-core/src/ltx_core/text_encoders/gemma/encoders/prompts/gemma3_t2v_system_prompt.txt
- https://github.com/Wan-Video/Wan2.2/blob/main/wan/utils/system_prompt.py

1. Keep casting, physical action, camera, and audio instructions separate in the brief.
2. Reference-guided motion prompts preserve appearance and describe changes, rather than recasting the face in text.
3. Use an observable action sequence with one primary action per short shot.
4. Do not invent camera moves, dialogue or additional people. Explicitly identify any proposed creative decisions as proposals.
5. Specify a concrete eyeline. An imagined conversation partner must not become an extra person at the frame edge.
6. Keep native-generation capabilities separate from postproduction. Our existing Seedance 1.0 Pro Fast T2V endpoint does not accept an image reference or dialogue track in its tested payload.
7. No automatic submission. A selected portrait and a verified I2V endpoint are prerequisites to a reference-guided video request.
8. Do not copy upstream automatic invention rules, language restrictions, or unrelated content substitutions. Preserve user intent and use English production text.
9. A textual constraint check is not evidence of improved video quality or beauty. Test output quality only after the owner resumes generation.
