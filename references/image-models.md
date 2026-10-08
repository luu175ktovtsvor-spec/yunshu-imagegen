# 图片模型：全部可选模型、能力与请求示例

Image Gen 板块开放当前 yunshu GPT 图片模型的全部选择，不限定为 `gpt-image-1.5`。以下 5 个模型均支持文生图和图片编辑；参考图生成、风格参考和多图合成也通过带图片输入的编辑接口处理，并在提示词中说明每张图片的用途。

## 模型与能力

| 图片模型 | 文生图 | 编辑图／参考图 | `quality` | `size` |
| --- | --- | --- | --- | --- |
| `gpt-image-1` | 支持 | 支持 | `auto`、`low`、`medium`、`high` | `auto`、`1024x1024`、`1536x1024`、`1024x1536` |
| `gpt-image-1.5` | 支持 | 支持 | `auto`、`low`、`medium`、`high` | `auto`、`1024x1024`、`1536x1024`、`1024x1536` |
| `gpt-image-2` | 支持 | 支持 | `auto`、`low`、`medium`、`high` | 常用尺寸或符合约束的自定义尺寸 |
| `gpt-image-2.5-flare` | 支持 | 支持 | `auto`、`low`、`medium`、`high`、`xhigh`、`max` | 常用尺寸或符合约束的自定义尺寸 |
| `gpt-image-2.5-sunburst` | 支持 | 支持 | `auto`、`low`、`medium`、`high`、`xhigh`、`max` | 常用尺寸或符合约束的自定义尺寸 |

“支持”说明模型能力和 yunshu 请求规则；具体 Key 是否有权限，以该 Key 的 `/models` 返回、分组图片权限及上游可用状态为准。模型出现在列表中不等于当前有额度，也不等于已完成真实生图测试。

## 模型选择

- 用户指定上述任意模型时，只要当前 Key 可用，就按指定名称请求，不替换成 `1.5`。
- 未指定时，优先使用明确配置的**图片默认模型**；没有该配置且当前 Key 提供 `gpt-image-2` 时，以它作为本 Skill 的默认图片模型。
- 默认模型不可用时，展示该 Key 实际可用的图片模型让用户选择，不静默降级。
- Codex `config.toml` 顶层的 `model` 是聊天／Responses 主模型，不是图片默认模型。
- 先通过当前 Provider 的 `base_url` 拼接 `/models` 查询实际可用模型。这里的 5 个模型是当前目录，不是固定白名单；服务以后开放的其他图片模型，也可在确认其参数与接口后使用。
- 图片模型名属于 Images 请求的顶层 `model`，或 Responses 请求的 `tools[].model`。Responses 顶层 `model` 仍是支持生图工具的主模型。

## 参数差异

- 文生图请求不带图片或遮罩；编辑／参考图请求必须带至少一张有效图片。
- `gpt-image-2` 不传 `input_fidelity`，它固定按高保真处理输入。其他模型也不要默认添加这个字段；仅在该模型与实际路由明确支持且用户有需求时使用。不同接口对这个字段的支持可能不同，不能仅凭请求被接受就认定它生效。
- `xhigh`、`max` 仅用于这里的两个 2.5 模型，不传给 Image 1、1.5 或 2。
- Image 2 和两个 2.5 模型的自定义尺寸：宽高为 16 的倍数，单边不超过 3840，长短边比不超过 3:1，总像素在 655360–8294400 之间。2.5 超过 `2560x1440` 的分辨率属于实验范围；返回后检查实际尺寸。
- 透明背景使用 `background: "transparent"`，输出用 `png` 或 `webp`，检查实际 alpha 通道。JPEG 不保存透明度。
- `output_compression` 只用于 JPEG／WebP，取 0–100 整数；PNG 不传。
- 默认只请求一张，`n: 1`。同一提示词多张才使用模型与上游支持的 `n`；不同提示词分别请求。不要假定每个模型都支持任意数量的图片。
- 图片格式、上传、遮罩和结果解析遵循 [接口映射](yunshu-interface.md)，不要把本地路径当成 `image_url`。

## 每个模型的文生图与编辑图示例

以下是 HTTP 请求 body，不是可直接运行的程序。所有请求都携带 `Authorization: Bearer <API Key>` 和 JSON 请求头；实际 URL 由当前 `base_url` 拼接一次接口后缀。Key、图片数据和提示词按真实任务填写。

编辑示例中的 `REPLACE_WITH_IMAGE_BASE64` 必须替换成有效 PNG 图片的 Base64。本地文件也可改用 multipart 上传；多张参考图在 `images` 数组中按顺序追加。

### gpt-image-1

文生图：`POST /v1/images/generations`。

```json
{
  "model": "gpt-image-1",
  "prompt": "生成一张白色背景上的蓝色陶瓷马克杯产品照片，不要文字或水印。",
  "n": 1,
  "size": "1024x1024",
  "quality": "medium",
  "output_format": "png"
}
```

编辑图／参考图：`POST /v1/images/edits`。

```json
{
  "model": "gpt-image-1",
  "prompt": "只把背景改为暖米色，保持马克杯的形状、颜色、纹理和位置不变。",
  "images": [
    {
      "image_url": "data:image/png;base64,REPLACE_WITH_IMAGE_BASE64"
    }
  ],
  "n": 1,
  "size": "1024x1024",
  "quality": "medium",
  "output_format": "png"
}
```

### gpt-image-1.5

文生图：`POST /v1/images/generations`。

```json
{
  "model": "gpt-image-1.5",
  "prompt": "生成一张白色背景上的蓝色陶瓷马克杯产品照片，不要文字或水印。",
  "n": 1,
  "size": "1024x1024",
  "quality": "medium",
  "output_format": "png"
}
```

编辑图／参考图：`POST /v1/images/edits`。

```json
{
  "model": "gpt-image-1.5",
  "prompt": "只把背景改为暖米色，保持马克杯的形状、颜色、纹理和位置不变。",
  "images": [
    {
      "image_url": "data:image/png;base64,REPLACE_WITH_IMAGE_BASE64"
    }
  ],
  "n": 1,
  "size": "1024x1024",
  "quality": "medium",
  "output_format": "png"
}
```

### gpt-image-2

文生图：`POST /v1/images/generations`。

```json
{
  "model": "gpt-image-2",
  "prompt": "生成一张白色背景上的蓝色陶瓷马克杯产品照片，不要文字或水印。",
  "n": 1,
  "size": "1024x1024",
  "quality": "medium",
  "output_format": "png"
}
```

编辑图／参考图：`POST /v1/images/edits`。

```json
{
  "model": "gpt-image-2",
  "prompt": "只把背景改为暖米色，保持马克杯的形状、颜色、纹理和位置不变。",
  "images": [
    {
      "image_url": "data:image/png;base64,REPLACE_WITH_IMAGE_BASE64"
    }
  ],
  "n": 1,
  "size": "1024x1024",
  "quality": "medium",
  "output_format": "png"
}
```

### gpt-image-2.5-flare

文生图：`POST /v1/images/generations`。

```json
{
  "model": "gpt-image-2.5-flare",
  "prompt": "生成一张白色背景上的蓝色陶瓷马克杯产品照片，不要文字或水印。",
  "n": 1,
  "size": "1024x1024",
  "quality": "medium",
  "output_format": "png"
}
```

编辑图／参考图：`POST /v1/images/edits`。

```json
{
  "model": "gpt-image-2.5-flare",
  "prompt": "只把背景改为暖米色，保持马克杯的形状、颜色、纹理和位置不变。",
  "images": [
    {
      "image_url": "data:image/png;base64,REPLACE_WITH_IMAGE_BASE64"
    }
  ],
  "n": 1,
  "size": "1024x1024",
  "quality": "medium",
  "output_format": "png"
}
```

### gpt-image-2.5-sunburst

文生图：`POST /v1/images/generations`。

```json
{
  "model": "gpt-image-2.5-sunburst",
  "prompt": "生成一张白色背景上的蓝色陶瓷马克杯产品照片，不要文字或水印。",
  "n": 1,
  "size": "1024x1024",
  "quality": "medium",
  "output_format": "png"
}
```

编辑图／参考图：`POST /v1/images/edits`。

```json
{
  "model": "gpt-image-2.5-sunburst",
  "prompt": "只把背景改为暖米色，保持马克杯的形状、颜色、纹理和位置不变。",
  "images": [
    {
      "image_url": "data:image/png;base64,REPLACE_WITH_IMAGE_BASE64"
    }
  ],
  "n": 1,
  "size": "1024x1024",
  "quality": "medium",
  "output_format": "png"
}
```

## 参考

模型能力与参数参考 [OpenAI 图片生成指南](https://developers.openai.com/api/docs/guides/image-generation)、[Image 1](https://developers.openai.com/api/docs/models/gpt-image-1)、[Image 1.5](https://developers.openai.com/api/docs/models/gpt-image-1.5)、[Image 2](https://developers.openai.com/api/docs/models/gpt-image-2)、[2.5 Flare](https://developers.openai.com/api/docs/models/gpt-image-2.5-flare) 和 [2.5 Sunburst](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)。
