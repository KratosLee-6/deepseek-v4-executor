---
name: deepseek-v4-executor
description: DeepSeek V4 执行层 —— 直接调用 DeepSeek V4 API 的 Python 脚本技能。绕过悟空内置模型路由层，直接通过 HTTP 请求与 DeepSeek V4 对话，适用于联网搜索、函数调用等工具执行场景。当用户提到「DeepSeek V4」「用 V4 搜索」「V4 联网搜索」「调用 DeepSeek API」「V4帮我做」时触发。⚠️ 注意：悟空后台切换模型后无法正常返回工具调用结果时，使用本技能作为替代通道。
version: "1.0"
author: KratosLee
created_at: "2026-04-26"
tags: [deepseek, api, executor, web-search, 联网搜索, V4]
---

# DeepSeek V4 执行层技能

> **开发者**：KratosLee  
> **版本**：v1.0（2026-04-26）  
> **适用场景**：悟空内置 DeepSeek 模型工具调用失败时的替代执行通道

---

## 技能简介

本技能通过 Python 脚本直接向 DeepSeek V4 API 发起 HTTP 请求，绕过悟空内置的模型路由层，解决「切换 DeepSeek 模型后工具调用（搜索/函数执行）无法返回内容」的问题。

**核心优势**：
- 🔓 直连 DeepSeek API，绕过模型路由兼容性问题
- ⚡ 响应速度快（实测 V4 Flash < 3 秒完成联网搜索）
- 🔧 支持三种调用模式：对话 / 联网搜索 / 函数调用

---

## 触发条件

以下任一场景激活本技能：

| 触发关键词 | 示例 |
|-----------|------|
| DeepSeek V4 | 「用 DeepSeek V4 帮我搜索」 |
| V4 联网搜索 | 「V4 搜索今天珠海天气」 |
| API 调用失败 | 悟空出现 `llm_call_failed` 错误 |
| 工具执行 | 「V4 帮我分析这份数据」 |
| DeepSeek 执行 | 「DeepSeek 联网查一下」 |

---

## 三种调用模式

### 模式一：chat（基础对话）
```bash
python references/deepseek_call.py --task "任务描述" --mode chat --api_key "你的API_KEY"
```
适用于：问答、写作、翻译、解释等纯文本任务。

### 模式二：search（联网搜索）✅ 推荐
```bash
python references/deepseek_call.py --task "帮我搜索今天珠海天气" --mode search --api_key "你的API_KEY"
```
适用于：查询实时信息、新闻、数据、天气等需要联网的内容。

### 模式三：tools（函数调用）
```bash
python references/deepseek_call.py --task "任务描述" --mode tools --api_key "你的API_KEY"
```
适用于：需要模型调用外部工具（计算器、搜索等）的复杂任务。

---

## API Key 配置

**优先级**：传入参数 > 环境变量 `DEEPSEEK_API_KEY` > 脚本内硬编码

**获取地址**：https://platform.deepseek.com/api_keys

**API Key 格式**：`sk-xxxxxxxxxxxxxxxxxxxxxxxx`

> ⚠️ 安全提示：请勿在对话中明文输出完整 API Key。

---

## 使用示例

### 示例 1：联网搜索天气
**用户**：帮我搜一下今天珠海的天气

**执行**：
```
python references/deepseek_call.py \
  --task "帮我搜索今天珠海的天气" \
  --mode search \
  --api_key "sk-xxxx" \
  --model "deepseek-chat"
```

**返回**：
```
🔍 搜索结果:

根据搜索结果，今天珠海的天气情况如下：

| 项目 | 内容 |
|------|------|
| 天气 | 多云，局部有阵雨 |
| 气温 | 22°C ~ 27°C |
| 风力 | 东南风2~3级 |

✅ 请求成功！耗时: 2.94s
```

### 示例 2：纯文本对话
**用户**：用 V4 帮我写一段自我介绍

**执行**：
```
python references/deepseek_call.py \
  --task "帮我写一段200字的自我介绍" \
  --mode chat \
  --api_key "sk-xxxx"
```

---

## 文件结构

```
deepseek-v4-executor/
├── SKILL.md                      ← 技能说明（本文件）
└── references/
    ├── deepseek_call.py          ← 核心执行脚本
    ├── schema_tools.py            ← 函数调用工具定义
    ├── prompt_templates.py        ← 场景提示词模板
    └── last_result.json           ← 最近一次调用结果
```

---

## 错误处理

| 错误类型 | 原因 | 解决方案 |
|----------|------|----------|
| `401 Unauthorized` | API Key 无效或已过期 | 检查 Key 是否正确，或前往平台重新生成 |
| `429 Rate Limit` | 请求频率超限 | 稍后重试，或升级配额 |
| `500 Internal Error` | DeepSeek 服务器异常 | 等待后重试，关注 status.deepseek.com |
| `timeout` | 网络超时 | 检查网络，或增加 `--timeout` 参数 |
| 空响应 | 模型不支持当前工具 | 降级到 `chat` 模式 |

---

## 费用参考

| 模型 | 输入价格 | 输出价格 |
|------|----------|----------|
| deepseek-chat (V4 Flash) | $0.27 / M tokens | $0.28 / M tokens |
| deepseek-chat (V4) | $0.27 / M tokens | $0.55 / M tokens |

> 💡 推荐日常联网搜索使用 **deepseek-chat**（V4 Flash 级别），速度快且费用更低。

---

## 开发信息

- **开发者**：KratosLee
- **技能 ID**：由悟空自动分配
- **安装方式**：悟空技能中心 / 命令行 `dws skill install <folder>`
- **适用平台**：悟空 AI（DingTalk 工作台）
