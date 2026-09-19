# Sample prompts (copy/paste)

These prompt recipes follow Codex ImageGen and are intended for Yunshu ImageGen agent requests.

Use these as starting points. They are intentionally complete prompt recipes, not the default amount of augmentation to add to every user request.

When adapting a user's prompt:

- keep user-provided requirements
- only add detail according to the specificity policy in `SKILL.md`
- preserve exact text verbatim when text must appear in the image
- state edit invariants explicitly
- identify every input image by index and role

The labeled lines are prompt scaffolding. Transport fields such as model, size, quality, background, output format, image inputs, and output destination are handled through the request mapping in `yunshu-interface.md`.

For prompting principles (structure, specificity, invariants, iteration), see [prompting.md](prompting.md).

## Website hero / product image

```text
Use case: product-mockup
Asset type: website hero image
Primary request: a minimal hero image of a ceramic coffee mug
Scene/backdrop: a clean warm studio surface
Subject: one handmade ceramic coffee mug
Style/medium: clean product photography
Composition/framing: wide composition with usable negative space for page copy
Lighting/mood: soft studio lighting, calm and premium
Materials/textures: matte ceramic with subtle handmade variation
Constraints: no logos, no text, no watermark
Avoid: extra products, hands, clutter, decorative lettering
```

## Poster / ad creative

```text
Use case: ads-marketing
Asset type: vertical campaign poster
Primary request: create a polished seasonal campaign poster for the user's stated event
Scene/backdrop: a visually coherent seasonal environment
Subject: the subject named by the user, with no invented brand or event details
Style/medium: polished commercial key art
Composition/framing: portrait layout with safe margins and clear hierarchy for copy
Lighting/mood: lighting and mood consistent with the campaign brief
Text (verbatim): "<exact user-provided copy>"
Constraints: render the text verbatim; keep all important text away from the edges; no extra words; no watermark
Avoid: invented slogans, invented logos, unrelated props, illegible microtext
```

## Existing image background replacement

```text
Use case: precise-object-edit
Asset type: product photo background replacement
Primary request: replace only the background with a warm sunset gradient
Input images: Image 1: edit target; preserve the product exactly
Constraints: change only the background; keep the product, silhouette, edges, framing, and shadows unchanged; no text; no watermark
Avoid: restyling the product, changing its proportions, adding objects
```

## Style reference with a new subject

```text
Use case: style-transfer
Asset type: editorial illustration
Primary request: create a new scene using the supplied image only as a style and composition reference
Input images: Image 1: style reference, not an edit target
Subject: <new user-requested subject>
Style/medium: preserve the reference's visual language without copying its subject identity
Composition/framing: use the reference only for the requested composition cues
Constraints: create a new image; do not reproduce unrelated objects or text from the reference
Avoid: treating the style reference as the base image, invented logos, watermark
```

## Transparent cutout

```text
Use case: background-extraction
Asset type: transparent product cutout
Primary request: isolate the requested subject as a clean cutout
Input images: Image 1: edit target, preserve the subject identity and proportions
Constraints: genuinely transparent background; preserve fine edges, hair, thin parts, and label text; no restyling; no watermark
Avoid: white or checkerboard baked into the pixels, cropped edges, invented details
```

## Multi-image compositing

```text
Use case: compositing
Asset type: campaign composite
Primary request: place the subject from Image 2 into the base scene in Image 1
Input images: Image 1: base scene; Image 2: subject insert
Composition/framing: keep Image 1's framing unless the user requests a change
Lighting/mood: match lighting, shadows, perspective, and scale between inputs
Constraints: preserve the base scene; keep the inserted subject recognizable; no extra objects; no text unless provided verbatim
Avoid: changing the base camera angle, duplicated subjects, mismatched shadows, watermark
```
