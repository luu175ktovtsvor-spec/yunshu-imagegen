---
name: yunshu-imagegen
description: Generate or edit raster images with a Yunshu API key when the current client does not expose Codex's built-in image_gen tool, including posters, illustrations, product images, and edits that use a logo or other reference image.
---

# Yunshu Image Generation

Use this skill when the user asks to create or edit an image through their Yunshu API key, or when the current Codex client does not provide the built-in `image_gen` tool. It is the Yunshu route for the same kinds of image work handled by Codex's image generation workflow.

This skill uses the Yunshu Images API. It is separate from Codex's native `image_gen` tool and does not change CC Switch, Codex configuration, server groups, or upstream routing.

## When to use

- The user asks to use a Yunshu API key or a client connected to Yunshu.
- The current client does not expose Codex's built-in `image_gen` tool.
- The user wants a generated image, a poster, or an edit that includes a logo or other reference image.

## When not to use

- The user has access to the native `image_gen` tool and has not asked to use Yunshu.
- The request is better handled by editing an SVG, HTML/CSS, or another code-native asset.

## Modes

There are two request types:

- `generate`: create a new image from a prompt.
- `edit`: create or change an image while using a supplied logo, reference image, or other input image.

Use `edit` when the user wants a logo included in the result. Keep the supplied logo recognizable and do not redraw it as a new logo.
Assume `generate` when the user has not asked to change an existing image or include a supplied image.

## Rules

- Keep the user's requested subject, style, aspect ratio, and exact text. For posters, keep important text away from the edges.
- Run `scripts/yunshu_imagegen.py` from this skill directory. It defaults to `https://api.zzyppz.cn/v1` and the `gpt-image-2` Images API model.
- Read `YUNSHU_API_KEY` first. If it is not set, the script may read a Yunshu provider's `experimental_bearer_token` and `base_url` from `$CODEX_HOME/config.toml` when the provider points to `api.zzyppz.cn`.
- Never print or put the API key in a prompt, filename, log, or user-facing response.
- Use an opaque background by default. In this mode the script converts an upstream 8-bit RGBA PNG to RGB so clients do not composite the whole image against white or black. Pass `--background transparent` only when transparency is requested.
- Inspect every saved image and report its absolute path, dimensions, and whether the request used `generate` or `edit`.

## Commands

```bash
python3 scripts/yunshu_imagegen.py generate \
  --prompt "..." --size 1024x1536 --output /absolute/path/output.png

python3 scripts/yunshu_imagegen.py edit \
  --image /absolute/path/logo.png \
  --prompt "Use Image 1 as the exact logo reference; ..." \
  --size 1024x1536 --output /absolute/path/output.png
```

For a logo, describe it as a supporting insert/reference and require that it remain recognizable, with no redraw or invented replacement.

## API

The script calls `/images/generations` for `generate` and `/images/edits` for `edit`. This gives users an image workflow through their Yunshu API key; it does not make the native Codex `image_gen` tool appear in a client that does not expose it.
