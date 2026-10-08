---
name: "yunshu-imagegen"
description: "Help users connect Yunshu API to Codex through CC Switch or to another Agent with HTTP/API tools, obtain or reuse an API Key, find recharge information, and generate or edit images through the Image Gen module. Use for Yunshu setup or tasks explicitly routed through Yunshu."
---

# Yunshu API

Agent 执行入口，调用名为 `$yunshu-imagegen`。用户介绍和上手流程见 [README](README.md)；本文件规定任务路由、认证、模型选择及执行边界。

## 1. 确定任务类型

- 接入、领取 Key 或读取现有配置：使用 [认证与接入规则](references/authentication.md)。
- 普通聊天、代码任务：按宿主 Agent 的正常流程处理，保留用户选择的模型，不进入图片工作流。
- 文生图、参考图生成、图片编辑或图片批次：进入 Image Gen 板块。
- 充值咨询：提供 [README 中的联系方式](README.md#4-联系主理人充值)，说明 Token 消耗按 0.18 倍率计算；不得代用户拨打电话或自动付款。

## 2. 解析认证和连接配置

- 已有 yunshu Key 时复用。没有 Key 时引导用户登录 `https://api.zzyppz.cn`，从「API 密钥」获取，选择可用的 `yunshuapi gpt 全部模型` 分组。
- Codex + CC Switch：解析生效的 `config.toml` 和 `model_provider`，从对应 Provider 读取 `base_url`、`experimental_bearer_token` 或 `env_key`，保留 `http_headers`。具体路径及覆盖规则见 [authentication.md](references/authentication.md)。
- 其他 Agent：使用其私有连接配置或密钥管理中提供的 yunshu Key 和服务地址。标准 API base 为 `https://api.zzyppz.cn/v1`，不要求读取 Codex 配置。
- 请求认证为 `Authorization: Bearer <API Key>`。不得输出真实 Key、将其提交到仓库或发送到其他 Provider。
- 确认宿主具备请求工具和图片结果处理能力，Key 具备对应模型权限和可用额度。缺少必需条件时，报告具体缺项。

## 3. 选择图片模型

当前模型目录为 `gpt-image-1`、`gpt-image-1.5`、`gpt-image-2`、`gpt-image-2.5-flare`、`gpt-image-2.5-sunburst`。实际可用性通过当前 Key 的 `/models` 及服务权限确定。

选择顺序：用户指定的可用图片模型 → 明确配置的图片默认模型 → 当前 Key 可用的 `gpt-image-2`。选定模型不可用时让用户重新选择，不静默替换。

Codex `config.toml` 顶层 `model` 是聊天／Responses 主模型，不是图片默认模型。参数差异和每个模型的生成、编辑示例见 [图片模型目录](references/image-models.md)。

## 4. 执行 Image Gen

1. 按 [Image Gen 工作流](references/imagegen.md) 区分生成和编辑，标记每张输入图的角色，保留用户指定的文字、参考图约束和编辑不变量。
2. 按 [接口格式](references/yunshu-interface.md) 选择 Images 或 Responses 路由，组装 URL、认证头和 body。请求字段必须符合选定模型和接口，Agent 元数据不得混入 HTTP body。
3. 使用宿主的请求工具执行请求，接收并保存返回图片。缺少工具时不得将文档示例当成已执行请求。
4. 检查实际文件、尺寸、透明度、图中文字和编辑约束；报告选定模型、保存路径及影响结果的限制。

提示词规则见 [prompting.md](references/prompting.md)，示例见 [sample-prompts.md](references/sample-prompts.md)。

## 执行边界

本仓库提供规则型 Skill，安装不会自动新增请求工具，也不会自动替换客户端的图片接口。模型列表、HTTP 200 或有效图片文件，均不能单独证明所有请求参数已生效；按接口说明核对返回结果和实际图片。
