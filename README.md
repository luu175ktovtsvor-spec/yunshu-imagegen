# Yunshu ImageGen

一个纯 Agent 版 Codex skill，通过 Yunshu ImageGen 接口生成或编辑图片。它沿用 Codex 内置 ImageGen 的决策树、提示词结构、参考图语义和质量检查，只替换 Yunshu 的接口参数映射。

Skill 的结构、提示词规范和示例基于 Codex 系统 `imagegen` Skill，并按 Apache License 2.0 改造成 Yunshu Agent 路由。

## 使用

在 Codex 中调用 `$yunshu-imagegen`，或在已绑定 Yunshu ImageGen 的代理流程中直接提出图片生成/编辑需求。代理会根据 [接口映射](references/yunshu-interface.md) 组装请求；不需要用户运行本地脚本。

纯文本请求、参考图生成、已有图片编辑、Logo 合成、透明背景、海报和多素材批量任务都遵循系统 ImageGen 的判断与提示词规则。

## 参考

- [Skill 主规则](SKILL.md)
- [Yunshu 接口映射](references/yunshu-interface.md)
- [Prompting 规则](references/prompting.md)
- [示例 Prompt](references/sample-prompts.md)
