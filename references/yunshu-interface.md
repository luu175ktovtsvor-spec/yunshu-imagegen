# Yunshu ImageGen interface mapping

Use this reference when constructing the provider request. Keep the creative prompt semantics identical to Codex ImageGen; only map the request to the Yunshu-compatible image interface.

## Request envelope

The agent should construct one logical ImageGen request with these fields:

| Field | Meaning | Agent rule |
| --- | --- | --- |
| `intent` | `generate` or `edit` | Decide from the user's intent, not merely from whether an image exists. |
| `prompt` | Final visual prompt | Preserve exact text, constraints, and edit invariants. |
| `model` | Yunshu-exposed image model | Use the requested model when available; otherwise use the active Yunshu default. |
| `n` | Same-prompt variant count | Use only for variants of one prompt; distinct assets need distinct requests. |
| `size` | Requested output dimensions | Preserve the user's aspect ratio and use a model-supported size. |
| `quality` | Draft/final quality level | Keep the user's requested quality when the model exposes it. |
| `background` | `transparent`, `opaque`, or `auto` | This is transport transparency behavior, not the visual scene backdrop. |
| `output_format` | `png`, `jpeg`, or `webp` | Choose a format compatible with the requested transparency and intended use. |
| `output_compression` | JPEG/WebP compression | Pass only when supported and requested or useful for delivery. |
| `moderation` | Provider moderation mode | Preserve an explicit user/provider setting; do not invent one. |
| `response_format` | Provider result encoding | Keep as an interface concern; prefer the provider's structured image result and do not expose credentials or raw transport details to the user. |
| `image` | Input image(s) | Preserve image order and role labels. Use for edit targets, references, inserts, or compositing as supported. |
| `mask` | Optional edit mask | Pass only when the user requests a localized edit and Yunshu exposes masks. |
| `input_fidelity` | Input preservation level | Use only for models that support it; never silently claim support. |
| `output_destination` | Final save location | Follow the user's destination; otherwise use the current project's output convention. |

## Intent mapping

- `generate` with no input images: create from the prompt.
- `generate` with style, mood, or composition references: preserve those images as references, not edit targets.
- `edit` with an existing image: preserve the requested invariants and change only the named elements.
- `edit` with a logo or supporting insert: label the image's role and require recognizability without redrawing or inventing a replacement.
- `compositing`: identify the base image and each inserted image by index; specify scale, perspective, lighting, and what must remain unchanged.

## Provider boundary

- Use the active Yunshu ImageGen interface rather than inventing a second execution path.
- Pass supported fields through unchanged where the interface exposes them.
- If Yunshu does not expose a field, preserve the intent in the prompt, report the limitation, and do not silently substitute a different meaning.
- Treat response model names and returned dimensions as evidence; do not infer hidden upstream behavior.

## Result acceptance

After each request, inspect the returned artifact for:

- requested subject, style, composition, and exact text
- actual dimensions and aspect ratio
- transparency and edge quality when requested
- identity/reference invariants for edits and composites
- absence of unwanted text, objects, logos, or watermarks
