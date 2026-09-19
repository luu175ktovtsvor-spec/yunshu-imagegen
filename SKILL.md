---
name: "yunshu-imagegen"
description: "Generate or edit raster images through Yunshu when the task benefits from AI-created bitmap visuals such as photos, illustrations, textures, sprites, mockups, or transparent-background cutouts. Use when the current image-generation route should use Yunshu, and do not use it for SVG, vector, HTML/CSS, canvas, or other deterministic code-native output."
---

# Yunshu Image Generation Skill

Generates or edits images for the current project through the Yunshu ImageGen interface. Follow the same creative decisions, prompt structure, invariants, and quality checks as Codex's built-in ImageGen workflow. The only provider-specific change is how the final ImageGen request is routed and which Yunshu-exposed model is selected.

## Top-level mode and rules

This skill has one execution mode:

- **Yunshu ImageGen agent mode:** assemble and submit an ImageGen request through the Yunshu-compatible image interface. Do not create or invoke a local execution script for ordinary requests.

Rules:

- Use this skill only when the user explicitly asks for Yunshu or when the active image-generation route is Yunshu.
- Keep the built-in ImageGen intent and prompt semantics: distinguish `generate` from `edit`, preserve reference-image roles, and keep user constraints exact.
- Pass the ImageGen request parameters described in [Yunshu interface mapping](references/yunshu-interface.md) without silently dropping supported fields.
- Keep the Yunshu transport mapping exact: Images API generation/edit requests use an image model directly; Responses requests use a separate main model plus an `image_generation` tool model.
- Use the user-requested model when it is exposed by Yunshu; otherwise use the configured Yunshu default and report the selected client-facing model name.
- Do not claim an upstream model identity, quality, or capability unless the Yunshu response or current provider documentation confirms it.
- Never expose API keys, bearer tokens, provider credentials, or private request headers in prompts, filenames, logs, or user-facing output.
- Do not overwrite an existing project asset unless the user explicitly asks for replacement; create a versioned sibling when needed.

## When to use

- Generate a new image (concept art, product shot, cover, website hero)
- Generate a new image using one or more reference images for style, composition, or mood
- Edit an existing image (inpainting, lighting or weather transformations, background replacement, object removal, compositing, transparent background)
- Produce many assets or variants for one task

## When not to use

- The user has access to the native Codex `image_gen` route and has not asked to use Yunshu.
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
- If the user provides images only as references for style, composition, mood, or subject guidance, treat the request as **generate** and preserve each reference image's role in the request.
- If the user provides no images, treat the request as **generate**.

Yunshu reference semantics:

- Keep the semantic distinction between an edit target and a style/composition reference even when the provider uses a shared image input field.
- Label every input image by role (`edit target`, `style reference`, `supporting insert`, or `compositing source`) and preserve the requested image ordering.
- If the provider cannot represent a requested multi-image role directly, state the limitation and use the closest supported mapping; do not silently reinterpret a style reference as the edit target.
- For edits, preserve invariants aggressively and save non-destructively by default.

Execution strategy:

- For one asset, submit one ImageGen request.
- For many distinct assets, submit one request per distinct prompt and asset; do not substitute one repeated-count parameter for different prompts.
- For variants of one prompt, use the provider's supported `n`/variant behavior only when the user wants variants of the same request.

Assume the user wants a new image unless they clearly ask to change an existing one.

## Workflow

1. Decide the intent: `generate` or `edit`.
2. Decide whether the output is preview-only or meant to be consumed by the current project.
3. Decide the execution strategy: one asset, same-prompt variants, or multiple distinct assets.
4. Collect inputs up front: prompt(s), exact text (verbatim), constraints/avoid list, and every input image.
5. For every input image, label its role explicitly:
   - reference image
   - edit target
   - supporting insert/style/compositing input
6. If an input image is local and its visual content affects the prompt or required invariants, inspect it before writing the request.
7. If the user asked for a photo, illustration, sprite, product image, banner, or other explicitly raster-style asset, use Yunshu ImageGen rather than substituting SVG/HTML/CSS placeholders. If the request is for an icon, logo, or UI graphic that should match existing repo-native SVG/vector/code assets, prefer editing those directly instead.
8. Augment the prompt based on specificity:
   - If the user's prompt is already specific and detailed, normalize it into a clear spec without adding creative requirements.
   - If the user's prompt is generic, add tasteful augmentation only when it materially improves output quality.
9. Assemble the request with the full parameter mapping in [Yunshu interface mapping](references/yunshu-interface.md). Keep creative prompt content separate from transport fields such as model, size, background, output format, and output path.
10. Submit the request through the Yunshu ImageGen interface.
11. Inspect outputs and validate: subject, style, composition, text accuracy, requested parameters, actual returned metadata, dimensions, transparency, and invariants/avoid items.
12. Iterate with a single targeted change, then re-check.
13. For preview-only work, render the image inline and keep the saved output in the task's preview/output area unless the user named another destination.
14. For project-bound work, save the selected artifact into the workspace and update any consuming code or references.
15. For batches or multi-asset requests, persist every requested deliverable final in the workspace unless the user explicitly asked to keep outputs preview-only. Discarded variants do not need to be kept unless requested.
16. Always report the final saved path(s), the final prompt or prompt set, the selected model, the request intent, and any provider limitation that affected the result.

## Transparent image requests

- Preserve the user's request for genuine transparency; do not replace it with a visually similar opaque background without disclosure.
- Pass the requested transparency behavior through the `background` parameter and use a transparent-capable output format when required by the selected Yunshu model.
- If the selected Yunshu model does not support transparent output, explain the limitation before choosing a fallback or a chroma-key workflow.
- Keep the distinction between the visual scene/backdrop in the prompt and the transport-level `background` field.

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

- extra characters, props, or objects that are not implied by the request
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
- background-extraction — transparent background / clean cutout.
- style-transfer — apply reference style while changing subject/scene.
- compositing — multi-image insert/merge with matched lighting/perspective.
- sketch-to-render — drawing/line art to photoreal render.

## Shared prompt schema

Use the following labeled spec as shared prompt scaffolding:

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

- `Asset type` and `Input images` are prompt scaffolding, not replacements for the structured request fields in the interface mapping.
- `Scene/backdrop` refers to the visual setting. It is not the transport-level `background` parameter, which controls output transparency behavior.
- Model, size, quality, background, output format, image inputs, masks, and output destination are request fields; do not bury them in the image prompt unless they also describe the desired visual result.

Augmentation rules:

- Keep it short.
- Add only the details needed to improve the prompt materially.
- For edits, explicitly list invariants (`change only X; keep Y unchanged`).
- For edits and compositing, repeat critical invariants on every iteration.
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
- For transparent images, preserve actual alpha and validate the output rather than trusting the request field alone.

More prompting principles: [references/prompting.md](references/prompting.md).
Copy/paste prompt specs: [references/sample-prompts.md](references/sample-prompts.md).
Request field mapping: [references/yunshu-interface.md](references/yunshu-interface.md).

## Guidance by asset type

Asset-type templates (website assets, game assets, wireframes, logo) are consolidated in [references/sample-prompts.md](references/sample-prompts.md).

## Yunshu model and size guidance

- Use the configured Yunshu ImageGen model by default; use a user-requested exposed model when specified.
- Treat the selected model name as the client-requested model name. Do not claim which internal upstream model handled the request unless the provider response confirms it.
- Use `1024x1024` for fast square drafts when supported.
- Use `1536x1024` for landscape or `1024x1536` for portrait when supported, unless the user requests another supported size.
- Respect the selected model's documented size, quality, transparency, input-image, and output-format constraints.
- Inspect and report actual returned dimensions rather than assuming the requested size was honored exactly.

## Interface boundary

- This skill describes agent behavior and request construction; it does not prescribe a local script, shell command, SDK runner, or UI automation path.
- Provider routing, authentication, and endpoint selection are handled by the active Yunshu integration.
- If the active Yunshu interface does not expose a requested ImageGen field, preserve the user's intent in the prompt and report the unsupported field instead of silently dropping it.

## Reference map

- [references/yunshu-interface.md](references/yunshu-interface.md): agent-facing request fields and provider mapping.
- [references/prompting.md](references/prompting.md): prompting principles.
- [references/sample-prompts.md](references/sample-prompts.md): copy/paste prompt recipes.
