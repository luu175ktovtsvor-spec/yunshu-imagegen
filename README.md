# Yunshu ImageGen

一个独立的 Codex skill，通过云枢 API 的 OpenAI 兼容 Images 接口生图或带 Logo 编辑图片。它适用于没有 ChatGPT 会员、但已经在 CC Switch/Codex 中配置 Yunshu API Key 的用户。

## 安装

将仓库目录复制到 Codex skills 目录：

```bash
cp -R yunshu-imagegen "$CODEX_HOME/skills/yunshu-imagegen"
```

如果没有设置 `CODEX_HOME`，默认目录是 `~/.codex/skills`。

脚本会优先读取 `YUNSHU_API_KEY`；如果没有设置，会从 `$CODEX_HOME/config.toml` 中寻找 `api.zzyppz.cn` Provider 的 `experimental_bearer_token`。也可以显式设置：

```bash
export YUNSHU_API_KEY='你的云枢 API Key'
export YUNSHU_BASE_URL='https://api.zzyppz.cn/v1'
```

## 用法

在 Codex 中调用 `$yunshu-imagegen`，或直接运行脚本：

```bash
python3 scripts/yunshu_imagegen.py generate \
  --prompt "一张中国风中秋海报" \
  --size 1024x1536 \
  --output ./output/mid-autumn.png

python3 scripts/yunshu_imagegen.py edit \
  --image ./logo.png \
  --prompt "将 Image 1 作为原始 Logo 放在海报顶部，保持 Logo 清晰可辨" \
  --size 1024x1536 \
  --output ./output/with-logo.png
```

默认模型是 `gpt-image-2`，默认背景是 `opaque`。部分 OpenAI 兼容上游会在 `opaque` 请求中错误返回带 Alpha 的 PNG；脚本会把这种 8-bit RGBA 图片转换为真正无 Alpha 的 RGB PNG，避免客户端合成出整张白边或暗边。只有传入 `--background transparent` 时才保留透明通道。脚本不会打印 API Key，也不会修改 Codex、CC Switch 或服务器配置。
