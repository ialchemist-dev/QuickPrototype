# Video prompt optimization research

Checked: 2026-10-19. Owner requested a research pause after rejecting the character's aesthetic direction. No further image, video, or TTS generation is authorized during this pause. No optimizer was installed or benchmarked; source inspection only. No paid calls made for this research.

## Recommendation

Separate casting from motion. First agree on the protagonist's visual direction, then approve a still reference; only afterward animate it with an image-to-video endpoint verified for the chosen model. Text rewriting can clarify intent, but cannot establish the owner's aesthetic preferences or guarantee a particular face. This is our production recommendation, not a measured Seedance benchmark result.

For initial adaptation, study Wan2.2's text/image-aware prompt routing and HunyuanVideo-1.5's conservative image-to-video rules. Wujidadi's CLI is a lightweight integration candidate. Avoid installing a full video-model stack solely for rewriting text. Treat a Seedance-specific community skill as a source of workflow ideas, not proof of supported API features.

## Shortlist

| Project | What is actually available | Fit and limitations |
|---|---|---|
| [Wan2.2](https://github.com/Wan-Video/Wan2.2), [prompt_extend.py](https://github.com/Wan-Video/Wan2.2/blob/main/wan/utils/prompt_extend.py) | Official source; DashScope and local Qwen expanders; task-aware text/image inputs and language selection. Repo declares Apache-2.0. | Best architecture reference. Local code loads Qwen models and moves them to a selected device; not verified on this Mac. Cloud rewriting costs extra. Improvements are not established for Seedance. |
| [HunyuanVideo-1.5](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5), [I2V rewrite rules](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5/blob/main/hyvideo/utils/rewrite/i2v_prompt.py) | Official T2V/I2V system prompts and rewrite integration. Source carries Tencent Hunyuan Community License, not MIT/Apache. | Useful guidance on preserving scene facts, specifying observable motion, and avoiding invented camera/light changes. The I2V template mandates Chinese; our English production workflow needs an independently written adaptation. Some examples are more expansive than the strict rules, so copying blindly would be unwise. |
| [LTX-Video](https://github.com/Lightricks/LTX-Video), [enhancement code](https://github.com/Lightricks/LTX-Video/blob/main/ltx_video/utils/prompt_enhance_utils.py) | Official optional prompt enhancement with an image-caption path; repo Apache-2.0. Separate model-weight terms still matter. | Useful image-caption-plus-motion architecture. Most relevant when adopting LTX; no evidence its native prompt format is optimal for Seedance. Installing the whole pipeline would be unnecessary for this task. |
| [Wujidadi/text-to-image-prompt-enhancer](https://github.com/Wujidadi/text-to-image-prompt-enhancer) | MIT CLI/library, Python 3.11+, configurable presets, local Ollama and remote provider support. Includes an LTX video preset. | Practical lightweight runner candidate. It is a single-pass rewrite tool, not a proven aesthetic optimizer. Custom English Seedance preset and human review would be needed. Local inference still requires a separately installed model/runtime. |
| [gutouy/seedance25-prompt-optimizer](https://github.com/gutouy/seedance25-prompt-optimizer) | MIT community skill and platform adapters. Explicitly unofficial. Describes constraints, task routing, continuity and reference roles. | Closest match to our agent workflow. Targets Seedance 2.5; our model is 1.0 Pro Fast. Use only model-compatible prose; do not assume native audio, video editing or multiple references. Not installed or executed. |
| [thu-coai/VPO](https://github.com/thu-coai/VPO) | Apache-2.0 repository, model/data links, SFT/DPO workflow. README identifies LLaMA3-8B-Instruct backbone and CogVideoX preference data. | Substantive research optimizer. Published examples concern CogVideoX, not our Seedance endpoint. GPU-oriented examples and training machinery are excessive for an initial local film test. |

## Candidates not prioritized

- [dariakryvosheieva/video-prompt-enhancer](https://github.com/dariakryvosheieva/video-prompt-enhancer): Qwen2.5-14B LoRA training and Sora/VisionReward loop. Local training checkpoints are marked not included; repository also contains an HF inference script. This is a research/training workflow, not a lightweight ready-made solution for this Mac. No claim that every trained weight is unavailable.
- [buildwithfur/seedance-prompt-optimizer](https://github.com/buildwithfur/seedance-prompt-optimizer): archival community mirror; README explicitly states no license was included. Publicly readable is not equivalent to permissively reusable. Prefer the MIT alternative for implementation.
- [WanPE](https://wan-pe.github.io/): recent cinematic planning research, 397B parameters. Official page currently says Models (Planned). Useful research direction, not a verified downloadable local optimizer. Reported results use other downstream setups and do not establish improvement on our endpoint.

## Local deployment reality

This Mac has 16 GiB RAM, Python 3.9.6 on the current python3 command, and uv available. Ollama is not on PATH. The lightweight CLI requires Python 3.11+, so an isolated runtime would be needed. No weights, runtimes or repositories were installed. CUDA-oriented upstream examples are not evidence of Apple Silicon compatibility. Prefer reviewing and adapting rules before selecting a local LLM or spending on remote rewriting.

## Diagnosis of the rejected shot (our assessment)

The prompt left casting to the generator with broad adjectives such as beautiful and natural. The ordinary-apartment and sleepwear direction was more explicit than the desired facial aesthetic. The sampled frames also showed a high off-camera eyeline and an unwanted partial second person, which required a crop. We did not establish an approved face reference before generating motion. The owner's rejection is sufficient to retire this candidate; automated beauty scores should not override it.

## Revised workflow, without generating yet

1. Present three written casting directions: warm romantic-film lead, polished contemporary lead, and fresh understated lead. Keep the protagonist an adult Asian woman. Do not infer a celebrity likeness.
2. Agree on face, hair, styling, expression and portrait lighting. Separate objective scene constraints from subjective preferences.
3. Once the owner resumes generation, create a small comparable set of still candidates using the same portrait framing and lighting. Let the owner select the face.
4. Lock the selected face, hairstyle and wardrobe; verify an appropriate I2V endpoint and its price before spending.
5. Rewrite only the action/camera instructions around that reference. Preserve character count, scene geometry and prop ownership. Keep speech and Foley in the edit plan when the endpoint does not support them.
6. Compare a concise baseline and a rewritten prompt with the same reference and generation settings, using multiple trials only within an approved budget. Score identity preservation, anatomy, action, extra entities and the owner's visual preference separately. One lucky sample is not proof of optimizer effectiveness.

## Proposed English rewrite contract

Input fields: approved subject reference, immutable subject count, wardrobe, location, action, duration, framing, camera motion, eyeline, lighting, allowed embellishments, exclusions, and provider capabilities.

Output: one executable shot paragraph; a separate edit/audio note; and an explicit list of assumptions. Do not invent a person at the off-camera eyeline. Do not add extra actions, change appearance, add cuts, or claim unsupported model features. If a reference defines appearance, preserve it and prioritize motion rather than redescribing a different face. Beauty remains a casting approval, not a synonym-expansion task.
