# Yunshu API

我自己的 GPT 账号有不少暂时用不完的额度，所以做了 yunshu API，也建了这个仓库。希望方便需要 GPT 模型的人，尤其是还没用过付费 GPT，或者想用 GPT 生图模型的朋友。

通过 yunshu API，你可以在 Agent 里聊天、写代码，也可以生成和修改图片。**yunshu Image Gen 是给 Agent 使用的 Skill。** 下面说明怎么领 Key、怎么接入、怎么安装和使用生图 Skill，以及怎么联系充值。

## 1. 先拿到 API Key

打开 [yunshu API 网站](https://api.zzyppz.cn)，登录自己的账号，进入「API 密钥」页面，创建或复制一把 Key。分组选 **`yunshuapi gpt 全部模型`**。

已经有 yunshu Key，就直接用现有的，不用再领一把。Key 是你的接口凭据，保存在自己的配置里，不要发到公开页面。

## 2. 接到你正在用的 Agent

### 用 Codex

1. 到 [CC Switch 官网](https://ccswitch.io/) 下载并安装；已经装好就跳过。
2. 在 CC Switch 中添加或导入 yunshu 的 Codex 配置，填入 API Key，再启用这份配置。
3. 打开 Codex，选择模型，就可以按平时的方式聊天或写代码。

如果你已经通过 CC Switch 配置好了 yunshu，生图时可以继续用这把 Key。Agent 可以从现有的 Codex `config.toml` 中读取，不用重新获取。具体字段见 [配置说明](references/authentication.md)。

### 用其他 Agent

yunshu Key 也能用于其他 Agent。在它的 API 设置中填入 Key 和下面的接口地址，再按本仓库的请求格式调用 GPT 生图模型：

```text
https://api.zzyppz.cn/v1
```

Agent 需要能请求外部 API，并能接收或保存返回的图片。能用哪些模型，以这把 Key 的权限为准。

## 3. 安装 Image Gen，开始生图

先按你所用 Agent 的方式，把本仓库作为 Skill 添加进去。在 Codex 中，安装后的调用名是 `$yunshu-imagegen`。

安装好 Skill、接好 yunshu API 后，直接告诉 Agent 你要什么图片。比如：

- 「用 Image 2 生成一张蓝色马克杯的产品图，白色背景。」
- 「把这张图片的背景改成暖米色，杯子保持不变。」

目前可以选择下面 **5 个图片模型**，每个都能根据文字生成图片，也能编辑已有图片或使用参考图。

| 模型 | 文生图 | 编辑图／参考图 |
| --- | --- | --- |
| `gpt-image-1` | 支持 | 支持 |
| `gpt-image-1.5` | 支持 | 支持 |
| `gpt-image-2` | 支持 | 支持 |
| `gpt-image-2.5-flare` | 支持 | 支持 |
| `gpt-image-2.5-sunburst` | 支持 | 支持 |

你指定哪个模型，就用哪个。没指定时，先用你配置的图片默认模型；没有这项配置，就在 Key 可用的情况下用 `gpt-image-2`。选定的模型不可用时，Agent 会让你重新选择。

这几个模型的质量、尺寸等参数有区别，具体见 [模型说明和请求示例](references/image-models.md)。

## 4. 联系主理人充值

扫描下面的微信二维码，联系 yunshu API 主理人充值 Token：

<img src="assets/wechat-qrcode.png" alt="yunshu API 主理人微信二维码" width="280" />

也可以直接拨打 **[+86 18664434400](tel:+8618664434400)**。

**Token 消耗按 0.18 倍率计算。**

## 配置和请求格式

需要配置字段或请求参数时，看下面这些文件：

- [API Key 与 Agent 接入](references/authentication.md)：Key 从哪里取，Codex 配置怎么读，其他 Agent 怎么接。
- [图片模型与完整示例](references/image-models.md)：5 个模型的参数区别，以及文生图、编辑图请求示例。
- [接口格式](references/yunshu-interface.md)：URL、请求头、JSON、图片上传和返回结果。
- [Image Gen 工作流](references/imagegen.md)：参考图、编辑要求和生成结果的检查规则。
- [提示词规则](references/prompting.md)与[提示词示例](references/sample-prompts.md)。

本仓库的 Skill 调用名是 `$yunshu-imagegen`，执行规则在 [SKILL.md](SKILL.md)。这些文件给 Agent 提供使用说明；Agent 仍需要具备请求接口的工具，安装 Skill 不会自动替换客户端的生图接口。

图片工作流和提示词规则参考 Codex 系统 `imagegen` Skill，按 Apache License 2.0 改造成 yunshu Agent 路由。
