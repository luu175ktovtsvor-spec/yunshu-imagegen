---
name: yunshu-imagegen
description: Generate or edit images through a Yunshu/Sub2API OpenAI-compatible Images API when Codex's native image_gen tool is unavailable, especially for users connected with a Yunshu API key instead of a ChatGPT membership.
---

# Yunshu ImageGen

Use this skill when the user explicitly asks for `$yunshu-imagegen`, wants image generation through a Yunshu API key, or cannot access Codex's native `image_gen` tool because the client is using a custom provider without a membership login.

This is an API-backed compatibility skill. It is separate from Codex's native `image_gen` tool and does not change CC Switch, Codex configuration, server groups, or upstream routing.

## Workflow

1. Decide whether the request is a new image (`generate`) or an edit/composite with a reference image (`edit`). Use `edit` when the user supplies a logo or other image that must be included.
2. Preserve exact requested text. For posters, explicitly state the target aspect ratio and size in the prompt and keep text away from the edges.
3. Run `scripts/yunshu_imagegen.py` from this skill directory. The script defaults to `https://api.zzyppz.cn/v1` and `gpt-image-2`.
4. The script first checks `YUNSHU_API_KEY`. If it is absent, it reads a Yunshu provider's `experimental_bearer_token` and `base_url` from `$CODEX_HOME/config.toml` when the host is `api.zzyppz.cn`. Never print the key.
5. Use an opaque background by default. The script converts an upstream RGBA response to RGB in this mode, which prevents a full-image alpha channel from becoming a white or dark composite in clients. Only pass `--background transparent` when the user explicitly asks for transparency.
6. Inspect the saved PNG after generation and report its absolute path, dimensions, and whether the request used `generate` or `edit`.

## Commands

```bash
python3 scripts/yunshu_imagegen.py generate \
  --prompt "..." --size 1024x1536 --output /absolute/path/output.png

python3 scripts/yunshu_imagegen.py edit \
  --image /absolute/path/logo.png \
  --prompt "Use Image 1 as the exact logo reference; ..." \
  --size 1024x1536 --output /absolute/path/output.png
```

For a logo, describe it as a supporting insert/reference and require that it remain recognizable, with no redraw or invented replacement. Do not use the API key in prompts, filenames, logs, or user-facing output.

## API boundary

The script calls `/images/generations` for `generate` and `/images/edits` for `edit`. This gives users a usable image workflow without ChatGPT membership, but it does not make the native Codex `image_gen` tool appear in a client that does not expose that tool.
