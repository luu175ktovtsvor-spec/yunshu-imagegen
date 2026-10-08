# API Key 与 Agent 接入

先确认自己有没有 yunshu Key，再选择你要用的 Agent。下面的接入步骤是给用户看的；后面的配置字段和接口规则用于 Agent 执行请求。

## 1. 取得或复用 Key

没有 Key：打开 [yunshu API 网站](https://api.zzyppz.cn)，登录后进入「API 密钥」，创建一把 Key，选择可用的 `yunshuapi gpt 全部模型` 分组。

已经有 Key：继续用现有的。已经导入 CC Switch 的，可以从它写入的 Codex 配置中读取，方法见下方「读取现有 Codex 配置」。生图前确认这把 Key 有对应图片模型的权限和可用额度。

## 2. 选择接入方式

### Codex + CC Switch

从 [CC Switch 官网](https://ccswitch.io/) 下载并安装，在 CC Switch 中添加或导入 yunshu 的 Codex 配置，填入 Key 并启用。然后打开 Codex，选择模型，按正常流程使用。

### 其他 Agent

在 Agent 的 API 设置或密钥管理中填入 yunshu Key，接口地址为 `https://api.zzyppz.cn/v1`。Agent 需要支持外部 API 请求，并能接收、解码或保存图片结果。请求格式见 [接口说明](yunshu-interface.md)。

需要充值时，联系方法见 [README 的充值说明](../README.md#4-联系主理人充值)。

## 3. 读取现有 Codex 配置

以下是 Agent 读取配置时的执行规则。

1. 配置路径为 `$CODEX_HOME/config.toml`；未设置 `CODEX_HOME` 时，macOS/Linux 使用 `~/.codex/config.toml`，Windows 使用 `%USERPROFILE%\.codex\config.toml`。
2. 根据当前生效的 `model_provider` 定位 `[model_providers.<provider>]`。若有 profile 或启动参数覆盖，以最终生效配置为准。
3. 从同一 Provider 节读取 `base_url` 和 `experimental_bearer_token`。后者是 API Key，字段不叫 `apikey`。
4. 若 Provider 使用 `env_key`，从该字段指定名称的环境变量取得 Key。
5. 保留 Provider 中配置的 `http_headers`。其中 `x-openai-actor-authorization = "local-image-extension"` 是附加请求头，不是 API Key。
6. 确认 Provider 指向 yunshu。其他服务的 Key 不得发送给 yunshu；没有可用 yunshu Key 时回到第一步获取。不得使用 ChatGPT 登录 token 替代 yunshu API Key。

### 配置示例

模型、地址和 Key 按实际配置填写；示例中的占位符不是可用凭据。

```toml
model_provider = "OpenAI"
model = "YOUR_RESPONSES_MODEL"

[model_providers.OpenAI]
name = "OpenAI"
base_url = "https://your-yunshu-host.example/v1"
wire_api = "responses"
requires_openai_auth = false
experimental_bearer_token = "YOUR_YUNSHU_API_KEY"
http_headers = { "x-openai-actor-authorization" = "local-image-extension" }
```

`OpenAI` 是该配置的 Provider 名称，请求地址由 `base_url` 决定。顶层 `model` 是 Codex／Responses 主模型，不能作为 Images API 的图片默认模型。图片模型按 [模型选择规则](image-models.md) 确定。

## 4. 请求认证与地址

| 项目 | 规则 |
| --- | --- |
| API 认证 | `Authorization: Bearer <API Key>` |
| URL 拼接 | 去掉 `base_url` 末尾的 `/`，再拼接一次接口后缀；已含 `/v1` 时不重复添加 |
| 模型查询 | `GET /models` |
| 文生图 | `POST /images/generations` |
| 编辑／参考图 | `POST /images/edits` |
| Responses | `POST /responses` |
| JSON 请求 | `Content-Type: application/json` |
| Multipart 上传 | 请求工具生成 boundary，必须与实际 body 一致 |

例如，`https://api.zzyppz.cn/v1` + `/images/generations` 得到 `https://api.zzyppz.cn/v1/images/generations`。自定义服务地址必须提供目标接口；不得自行更换为其他服务。详细 body、上传字段和返回结果见 [接口格式](yunshu-interface.md)。

## 5. 登录后管理 Key

Agent 已获得用户授权，并且请求工具持有站点登录会话时，可以通过用户侧接口管理用户自己的 Key：

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| GET | `/api/v1/keys` | 列出自己的 Key |
| GET | `/api/v1/keys/{id}` | 查询 Key 详情 |
| POST | `/api/v1/keys` | 创建 Key；字段包括 `name` 和 `group_id`，其他限制按用户需求设置 |

这些管理接口需要站点登录认证，不是匿名接口，也不使用生图 API Key 代替登录会话。未登录时让用户完成登录，不索要账号密码。

## 凭据处理

Key 仅用于私有连接配置、密钥管理和请求工具。不得输出完整配置、真实 Key 或认证头，不得将凭据放入图片提示词、JSON body、URL 或公开仓库。缺少连接配置或请求工具时，说明缺项，不声称请求已经完成。
