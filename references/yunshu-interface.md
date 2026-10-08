# Yunshu ImageGen interface mapping

Use this reference when constructing the provider request. Keep the creative prompt semantics identical to Codex ImageGen; only map the request to the Yunshu-compatible image interface.

Before constructing a request, resolve the endpoint and credentials using [connection and authentication](authentication.md), and read [all image models, capabilities, and generation/edit examples](image-models.md). This reference describes the OpenAI-compatible Yunshu image paths; other provider families need their own schemas.

## URL, headers, and body assembly

Resolve the active Provider's `base_url` and Key first. Remove trailing `/` from the base, then append the endpoint suffix once; do not replace the base path or add another `/v1` when it is already present. The standard yunshu configuration uses `https://api.zzyppz.cn/v1`:

| Operation | Method | Endpoint suffix | Final URL for the standard base |
| --- | --- | --- | --- |
| List available models | GET | `/models` | `https://api.zzyppz.cn/v1/models` |
| Generate an image | POST | `/images/generations` | `https://api.zzyppz.cn/v1/images/generations` |
| Edit or supply reference images | POST | `/images/edits` | `https://api.zzyppz.cn/v1/images/edits` |
| Responses with an image tool | POST | `/responses` | `https://api.zzyppz.cn/v1/responses` |

- Send `Authorization: Bearer <API Key>` and the configured additional headers. The Key never belongs in the URL or JSON body.
- JSON requests use `Content-Type: application/json`; encode the body as JSON rather than concatenating unescaped prompt text into a string.
- Multipart edits use a client-generated `Content-Type: multipart/form-data; boundary=...`. Include `model` and `prompt` as text parts, and real image bytes with filenames and matching MIME types as `image`/`image[]` file parts. Do not manually set a boundary that differs from the encoded body.
- For inline image inputs, use a complete `data:image/<format>;base64,<encoded bytes>` value with a MIME type matching the bytes. The example placeholders below must be replaced; they are not usable image data.
- Custom bases must expose the selected route. Use the current configured service address and confirm the selected endpoint is available; do not silently switch to another host.

## Logical request envelope (not an HTTP body)

The following fields describe agent intent. Translate them for the selected transport; do not send this table as one JSON object. `intent`, image role labels, and `output_destination` are agent-only metadata. Authentication belongs in the HTTP header.

The agent should construct one logical ImageGen request with these fields:

| Field | Meaning | Agent rule |
| --- | --- | --- |
| `intent` | `generate` or `edit` | Agent metadata; selects the creative workflow. Choose the transport endpoint/action according to the image inputs and route. |
| `prompt` | Final visual prompt | Preserve exact text, constraints, and edit invariants. |
| `model` | Yunshu-exposed image model | Follow the [model selection rules](image-models.md); honor the requested model, then an explicit image default, then `gpt-image-2` if available. |
| `n` | Same-prompt variant count | Use only for variants of one prompt; distinct assets need distinct requests. |
| `size` | Requested output dimensions | Preserve the user's aspect ratio and use a model-supported size. |
| `quality` | Model-specific quality enum | Image 1/1.5/2 use `auto`, `low`, `medium`, `high`; 2.5 Flare/Sunburst also support `xhigh`, `max`. “draft/final” are intent labels, not HTTP enum values. |
| `background` | `transparent`, `opaque`, or `auto` | This is transport transparency behavior, not the visual scene backdrop. |
| `output_format` | `png`, `jpeg`, or `webp` | Choose a format compatible with the requested transparency and intended use. |
| `output_compression` | JPEG/WebP compression, integer 0–100 | Pass only for a supported JPEG/WebP output; not PNG. |
| `moderation` | Provider moderation mode | For supported GPT Image routes: `auto` or `low`; omit unless requested/configured. |
| `response_format` | Images API result encoding | Route-specific `b64_json`/`url`; omit by default for GPT Image (base64 output). Not a Responses image tool field. |
| `image` | Logical input image(s) | Translate to multipart `image`/`image[]`, JSON edits `images[].image_url`, or Responses `input_image` items. Preserve order; describe roles in the prompt. |
| `mask` | Optional edit mask | Pass only when the user requests a localized edit and Yunshu exposes masks. |
| `input_fidelity` | Model-specific input preservation | `high`/`low` only where supported. Omit for `gpt-image-2`, which handles inputs at high fidelity automatically. |
| `output_destination` | Final local save location | Agent metadata; save the returned artifact here, never send it as an API parameter. |

## Yunshu transport mapping

Yunshu exposes two different image paths. Do not collapse their model roles:

### Images API

- Text-only creation: `POST /v1/images/generations`, JSON body.
- Image inputs (edit, compositing, or reference-guided generation): `POST /v1/images/edits`. Using this endpoint to carry references does not change the user's creative intent; describe each input's role in the prompt. The editing endpoint supplies image inputs; preserve the distinction between a creative reference and an edit target in the prompt.
- `model` is the **image model** exposed for the Key's group.
- Send `prompt` and supported image settings: `n`, `size`, `quality`, `background`, `output_format`, `output_compression`, `moderation`, and edit-only `input_fidelity` where supported. Do not copy all optional settings into every request.
- `prompt` must be non-empty. `n` is a positive integer, bounded by the model/provider; use `1` by default. `size` is a supported string such as `1024x1024`, `1536x1024`, `1024x1536`, or `auto`, not a universal list for every model.
- Generation requests do not accept an edit target or mask. Do not add `image` to `/images/generations` to obtain reference conditioning.
- For edits with local files, use `multipart/form-data`: `image` or repeated `image[]` file parts and optional `mask` file part; let the client generate the boundary. A local path is not an image URL.
- For JSON edits, yunshu requires **`images: [{"image_url": "..."}]`**, with optional **`mask: {"image_url": "..."}`**. Use an accessible URL or a supported `data:image/...;base64,...` value. It rejects `images[].file_id` and `mask.file_id`; singular JSON `image` is not a substitute.
- `response_format` is route-specific: GPT Image normally returns base64, so omit it unless the integration explicitly supports a different encoding. Only use `url` when the selected model and interface explicitly support it.

Text-only request body using Image 2 (all five models have complete generation/edit examples in [image-models.md](image-models.md)):

```json
{
  "model": "gpt-image-2",
  "prompt": "A ceramic coffee mug on a clean studio background. No text.",
  "n": 1,
  "size": "1024x1024",
  "quality": "medium",
  "output_format": "png"
}
```

Image 2 JSON edit body (the data URL below is illustrative, not valid image bytes):

```json
{
  "model": "gpt-image-2",
  "prompt": "Change only the background to warm beige. Keep the product unchanged.",
  "images": [{"image_url": "data:image/png;base64,REPLACE_WITH_IMAGE_BASE64"}],
  "size": "1024x1024",
  "output_format": "png"
}
```

### Responses image tool

- Endpoint: `POST /v1/responses`, JSON body.
- Top-level `model` is the **Responses/main model**, not the image model.
- Put prompt text and reference/edit images in `input` (text and `input_image` content items). Do not send top-level `prompt`, `image`, or `mask` copied from the Images API.
- `tools[]` contains `{"type": "image_generation", ...}`; its `model` is the image model when the active gateway supports explicit selection.
- Image options belong inside that tool: `action` (`auto`, `generate`, `edit`), `size`, `quality`, `background`, `output_format`, `output_compression`, `moderation`, and other fields confirmed for the selected model and route.
- Map a supported mask to **`tools[].input_image_mask.image_url`**. Mask file IDs require a compatible file service and cannot be assumed from Images API support.
- Do not blindly copy Images API `n`, `response_format`, or `input_fidelity` into the Responses image tool: support differs. Omit these fields unless the selected tool model and interface explicitly support them. For same-prompt variants, use separate calls unless tool-level count support is confirmed.
- `tool_choice: {"type": "image_generation"}` selects the image tool; a completed text-only response is not an image result.
- A gateway may supply the tool's omitted image model. Do not guess which default it selected.

Responses request body (replace both model names with ones exposed by the service):

```json
{
  "model": "YOUR_RESPONSES_MODEL",
  "input": [{
    "role": "user",
    "content": [{"type": "input_text", "text": "A ceramic coffee mug on a clean studio background. No text."}]
  }],
  "tools": [{
    "type": "image_generation",
    "model": "gpt-image-2",
    "action": "generate",
    "size": "1024x1024",
    "quality": "medium",
    "output_format": "png"
  }],
  "tool_choice": {"type": "image_generation"}
}
```

For editing, add an `input_image` item to the message content and set tool `action` to `edit`; retain role labels and invariants in the text:

```json
{"type": "input_image", "image_url": "data:image/png;base64,REPLACE_WITH_IMAGE_BASE64"}
```

When exact image model, size, or quality matters, prefer the Images API when available, then verify the returned artifact. The selected model and interface may normalize settings; inspect the result to confirm the requested options were honored.

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

## Three-layer result verification

For non-streaming Images results, decode `data[].b64_json` or retrieve a supported `data[].url`. For non-streaming Responses results, select `output[]` items with `type: "image_generation_call"` and decode their `result`. Do not assume these response schemas are interchangeable. Streaming integrations must assemble the final completed result, not save an arbitrary partial frame as the final image.

Compare these layers before reporting success:

1. **Requested:** model, size, quality, background, output format, input images, and intent.
2. **Effective response:** returned model/tool metadata, quality, size, format, and route/executor when available.
3. **Artifact:** actual file type, dimensions, transparency, and edit/reference invariants.

If the effective response or artifact differs from the request, report the downgrade or provider normalization explicitly. HTTP 200 plus a valid image is not proof that every requested option was honored.

## Result acceptance

After each request, inspect the returned artifact for:

- requested subject, style, composition, and exact text
- actual dimensions and aspect ratio
- transparency when requested
- identity/reference invariants for edits and composites
- absence of unwanted text, objects, logos, or watermarks
