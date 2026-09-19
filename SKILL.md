---
name: "yunshu-imagegen"
description: "Generate or edit raster images through a Yunshu API key when the task benefits from AI-created bitmap visuals such as photos, illustrations, textures, sprites, mockups, or transparent-background cutouts. Use when Codex should create a brand-new image, transform an existing image, or derive visual variants from references through Yunshu, and the output should be a bitmap asset rather than repo-native code or vector. Do not use when the task is better handled by editing existing SVG/vector/code-native assets, extending an established icon or logo system, or building the visual directly in HTML/CSS/canvas."
---

<!-- Adapted from the OpenAI imagegen skill and modified for Yunshu API routing. -->

# Yunshu Image Generation Skill

Generates or edits images for the current project (for example website assets, game assets, UI mockups, product mockups, wireframes, logo design, photorealistic images, or infographics).

## Top-level modes and rules

This skill has one top-level mode:

- **Yunshu CLI mode:** `scripts/yunshu_imagegen.py` for image generation, editing, and transparent-image requests. It uses the user's Yunshu API key and does not require `OPENAI_API_KEY`.

The CLI exposes two subcommands:

- `generate`
- `edit`

Rules:
- Use the bundled `scripts/yunshu_imagegen.py` workflow for Yunshu image generation and editing. Do not create one-off SDK runners.
- For transparent images, pass `--background transparent` and preserve the generated alpha.
- Use `gpt-image-2` by default. Never silently switch to a different model unless the user explicitly requested it.
- If the user asks for many distinct assets or variants, issue one CLI call per requested asset or variant.
- Never modify `scripts/yunshu_imagegen.py` while completing an ordinary image request. If something is missing, ask the user before changing the skill.
- Never print, log, or place the Yunshu API key in a prompt, filename, or user-facing response.

Yunshu save-path policy:
- Use `--output` to save each generated image at a stable, explicit path.
- Save-path precedence:
  1. If the user names a destination, save the selected output there.
  2. If the image is meant for the current project, save the final selected image in the workspace before finishing.
  3. If the image is only for preview or brainstorming, save it under `output/imagegen/` and render it inline.
- Do not overwrite an existing asset unless the user explicitly asked for replacement; otherwise create a sibling versioned filename such as `hero-v2.png` or `item-icon-edited.png`.

Shared prompt guidance lives in `references/prompting.md` and `references/sample-prompts.md`.

Yunshu resources:
- `references/prompting.md`
- `references/sample-prompts.md`
- `scripts/yunshu_imagegen.py`

## When to use
- Generate a new image (concept art, product shot, cover, website hero)
- Generate a new image using a supplied reference image for style, composition, or mood
- Edit an existing image (inpainting, lighting or weather transformations, background replacement, object removal, compositing, transparent background)
- Produce many assets or variants for one task

## When not to use
- Extending or matching an existing SVG/vector icon set, logo system, or illustration library inside the repo
- Creating simple shapes, diagrams, wireframes, or icons that are better produced directly in SVG, HTML/CSS, or canvas
- Making a small project-local asset edit when the source file already exists in an editable native format
- Any task where the user clearly wants deterministic code-native output instead of a generated bitmap

## Decision tree

Think about two separate questions:

1. **Intent:** is this a new image or an edit of an existing image?
2. **Execution strategy:** is this one asset or many assets/variants?

Intent:
- If the user wants to modify an existing image while preserving parts of it, treat the request as **edit**.
- If the user provides a reference image for style, composition, mood, or subject guidance, use **edit** so the image can be sent through `--image`.
- If the user provides no images, treat the request as **generate**.

Yunshu edit semantics:
- Yunshu edit mode accepts a local image path through `--image`.
- The current CLI accepts one input image per edit request. Do not imply that multiple files were sent when only one was used.
- Inspect a local image with `view_image` before editing when its visual content affects the prompt or required invariants.
- Use `edit` when a supplied logo or reference image must appear in the output.
- For edits, preserve invariants aggressively and save non-destructively by default.

Execution strategy:
- Produce many assets or variants by issuing one Yunshu CLI call per requested asset or variant.
- For many distinct assets, use a distinct prompt and output path for each call.

Assume the user wants a new image unless they clearly ask to change an existing one.

## Workflow
1. Decide the intent: `generate` or `edit`.
2. Decide whether the output is preview-only or meant to be consumed by the current project.
3. Decide the execution strategy: single asset vs repeated Yunshu CLI calls.
4. Collect inputs up front: prompt(s), exact text (verbatim), constraints/avoid list, and any input image.
5. For the input image, label its role explicitly:
   - reference image
   - edit target
   - supporting insert/style/compositing input
6. If the edit target is on the local filesystem, inspect it with `view_image` before writing the edit prompt when visual details matter.
7. If the user asked for a photo, illustration, sprite, product image, banner, or other explicitly raster-style asset, use the Yunshu CLI rather than substituting SVG/HTML/CSS placeholders. If the request is for an icon, logo, or UI graphic that should match existing repo-native SVG/vector/code assets, prefer editing those directly instead.
8. Augment the prompt based on specificity:
   - If the user's prompt is already specific and detailed, normalize it into a clear spec without adding creative requirements.
   - If the user's prompt is generic, add tasteful augmentation only when it materially improves output quality.
9. Run `scripts/yunshu_imagegen.py generate` for a new image or `scripts/yunshu_imagegen.py edit` with `--image` for an edit or logo-based composition.
10. For transparent-output requests, pass `--background transparent` and preserve the generated alpha channel.
11. Inspect outputs and validate: subject, style, composition, text accuracy, and invariants/avoid items.
12. Iterate with a single targeted change, then re-check.
13. For preview-only work, render the image inline and keep the saved output under `output/imagegen/` unless the user named another destination.
14. For project-bound work, save the selected artifact into the workspace and update any consuming code or references.
15. For batches or multi-asset requests, persist every requested deliverable final in the workspace unless the user explicitly asked to keep outputs preview-only. Discarded variants do not need to be kept unless requested.
16. Always report the final saved path(s), the final prompt or prompt set, and whether the request used `generate` or `edit`.

## Transparent image requests

Pass `--background transparent` and preserve the generated alpha. Use the default opaque mode for ordinary images; the script removes an unexpected full-image alpha channel from opaque PNG responses.

## Prompt augmentation

Reformat user prompts into a structured, production-oriented spec. Make the user's goal clearer and more actionable, but do not blindly add detail.

Treat this as prompt-shaping guidance, not a closed schema. Use only the lines that help, and add a short extra labeled line when it materially improves clarity.

### Specificity policy

Use the user's prompt specificity to decide how much augmentation is appropriate:

- If the prompt is already specific and detailed, preserve that specificity and only normalize/structure it.
- If the prompt is generic, you may add tasteful augmentation when it will materially improve the result.

Allowed augmentations:
- composition or framing hints
- polish level or intended-use hints
- practical layout guidance
- reasonable scene concreteness that supports the stated request

Not allowed augmentations:
- extra characters or objects that are not implied by the request
- brand names, slogans, palettes, or narrative beats that are not implied
- arbitrary side-specific placement unless the surrounding layout supports it

## Use-case taxonomy (exact slugs)

Classify each request into one of these buckets and keep the slug consistent across prompts and references.

Generate:
- photorealistic-natural — candid/editorial lifestyle scenes with real texture and natural lighting.
- product-mockup — product/packaging shots, catalog imagery, merch concepts.
- ui-mockup — app/web interface mockups and wireframes; specify the desired fidelity.
- infographic-diagram — diagrams/infographics with structured layout and text.
- scientific-educational — classroom explainers, scientific diagrams, and learning visuals with required labels and accuracy constraints.
- ads-marketing — campaign concepts and ad creatives with audience, brand position, scene, and exact tagline/copy.
- productivity-visual — slide, chart, workflow, and data-heavy business visuals.
- logo-brand — logo/mark exploration, vector-friendly.
- illustration-story — comics, children’s book art, narrative scenes.
- stylized-concept — style-driven concept art, 3D/stylized renders.
- historical-scene — period-accurate/world-knowledge scenes.

Edit:
- text-localization — translate/replace in-image text, preserve layout.
- identity-preserve — try-on, person-in-scene; lock face/body/pose.
- precise-object-edit — remove/replace a specific element (including interior swaps).
- lighting-weather — time-of-day/season/atmosphere changes only.
- background-extraction — transparent background / clean cutout. Pass `--background transparent` for actual transparency.
- style-transfer — apply reference style while changing subject/scene.
- compositing — multi-image insert/merge with matched lighting/perspective.
- sketch-to-render — drawing/line art to photoreal render.

## Shared prompt schema

Use the following labeled spec as shared prompt scaffolding for both request types:

```text
Use case: <taxonomy slug>
Asset type: <where the asset will be used>
Primary request: <user's main prompt>
Input images: <Image 1: role; Image 2: role> (optional)
Scene/backdrop: <environment>
Subject: <main subject>
Style/medium: <photo/illustration/3D/etc>
Composition/framing: <wide/close/top-down; placement>
Lighting/mood: <lighting + mood>
Color palette: <palette notes>
Materials/textures: <surface details>
Text (verbatim): "<exact text>"
Constraints: <must keep/must avoid>
Avoid: <negative constraints>
```

Notes:
- `Asset type` and `Input images` are prompt scaffolding, not dedicated CLI flags.
- `Scene/backdrop` refers to the visual setting. It is not the same as the Yunshu CLI `background` parameter, which controls output transparency behavior.
- Execution notes such as the model, size, background mode, and output path are CLI arguments. Do not put them in the image prompt unless they also describe the desired visual result.

Augmentation rules:
- Keep it short.
- Add only the details needed to improve the prompt materially.
- For edits, explicitly list invariants (`change only X; keep Y unchanged`).
- If any critical detail is missing and blocks success, ask a question; otherwise proceed.

## Examples

### Generation example (hero image)
```text
Use case: product-mockup
Asset type: landing page hero
Primary request: a minimal hero image of a ceramic coffee mug
Style/medium: clean product photography
Composition/framing: wide composition with usable negative space for page copy if needed
Lighting/mood: soft studio lighting
Constraints: no logos, no text, no watermark
```

### Edit example (invariants)
```text
Use case: precise-object-edit
Asset type: product photo background replacement
Primary request: replace only the background with a warm sunset gradient
Constraints: change only the background; keep the product and its edges unchanged; no text; no watermark
```

## Prompting best practices
- Structure prompt as scene/backdrop -> subject -> details -> constraints.
- Include intended use (ad, UI mock, infographic) to set the mode and polish level.
- Use camera/composition language for photorealism.
- Only use SVG/vector stand-ins when the user explicitly asked for vector output or a non-image placeholder.
- Quote exact text and specify typography + placement.
- For tricky words, spell them letter-by-letter and require verbatim rendering.
- For multi-image inputs, reference images by index and describe how they should be used.
- For edits, repeat invariants every iteration to reduce drift.
- Iterate with single-change follow-ups.
- If the prompt is generic, add only the extra detail that will materially help.
- If the prompt is already detailed, normalize it instead of expanding it.
- For transparent images, pass `--background transparent` and preserve its alpha.

More prompting principles: `references/prompting.md`.
Copy/paste prompt specs: `references/sample-prompts.md`.

## Guidance by asset type
Asset-type templates (website assets, game assets, wireframes, logo) are consolidated in `references/sample-prompts.md`.

## gpt-image-2 guidance

The Yunshu CLI defaults to `gpt-image-2`.

- Use `gpt-image-2` for new Yunshu workflows unless the user requests a different exposed model.
- Treat `gpt-image-2` as the client-requested model name. Do not claim which internal upstream model handled the request unless server evidence confirms it.
- Square images are typically fastest to generate. Use `1024x1024` for fast square drafts.
- Use `1536x1024` for landscape or `1024x1536` for portrait unless the user requests another supported size.
- The upstream may return dimensions that differ slightly from the requested size. Inspect and report the actual saved dimensions.

Popular `gpt-image-2` sizes:
- `1024x1024` square
- `1536x1024` landscape
- `1024x1536` portrait
- `auto`

## Yunshu CLI mode

### Commands

Generate a new image:

```bash
python3 scripts/yunshu_imagegen.py generate \
  --prompt "..." \
  --size 1024x1536 \
  --output /absolute/path/output.png
```

Edit or compose with a supplied image:

```bash
python3 scripts/yunshu_imagegen.py edit \
  --image /absolute/path/input.png \
  --prompt "..." \
  --size 1024x1536 \
  --output /absolute/path/output.png
```

### Temp and output conventions
- Use `tmp/imagegen/` for intermediate files; delete them when done.
- Write final artifacts under `output/imagegen/`.
- Use `--output` to control the output path; keep filenames stable and descriptive.

### Dependencies
The script uses the Python standard library and requires Python 3.11 or newer for `tomllib`.

### Environment
- The script first reads `YUNSHU_API_KEY`.
- If that variable is absent, it can read `experimental_bearer_token` and `base_url` from a Yunshu provider in `$CODEX_HOME/config.toml` when the host is `api.zzyppz.cn`.
- `YUNSHU_BASE_URL` may override the default `https://api.zzyppz.cn/v1` endpoint.
- Never ask the user to paste the full key in chat. Ask them to set it locally and confirm when ready.

If the key is missing, give the user these steps:
1. Get a Yunshu API key from the user's Yunshu account.
2. Set `YUNSHU_API_KEY` as an environment variable, or configure the Yunshu provider in Codex/CC Switch.
3. Offer to guide them through setting the environment variable for their OS/shell if needed.

## Reference map
- `references/prompting.md`: prompting principles copied from the system `imagegen` skill.
- `references/sample-prompts.md`: copy/paste prompt recipes copied from the system `imagegen` skill.
- `scripts/yunshu_imagegen.py`: Yunshu CLI implementation for generation and editing.
