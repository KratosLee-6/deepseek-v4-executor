---
name: deepseek-v4-executor
description: DeepSeek V4 执行层 —— 直接调用 DeepSeek V4 API 的 Python 脚本技能。绕过悟空内置模型路由层，通过 HTTP 请求直连 DeepSeek V4，适用于需要联网搜索、函数调用等复杂工具调用场景。当用户提到「DeepSeek V4」「V4 搜索」「V4 帮我做XX」「联网搜索 DeepSeek」时触发。本技能需要使用者自行提供 DeepSeek API Key，不包含任何预置密钥。
version: "1.1"
author: KratosLee
created_at: "2026-04-26"
updated_at: "2026-04-26"
tags: [deepseek, api, executor, web-search, 联网搜索]
---

# DeepSeek V4 执行层技能

> **开发者**：KratosLee | **版本**：v1.1 | **最后更新**：2026-04-26
>
> ⚠️ **重要提示**：本技能不包含任何 API Key，使用前请先完成下方「API Key 配置」步骤。

---

## 一、API Key 配置（必须完成）

### 第一步：获取你自己的 DeepSeek API Key

1. **电脑端访问** DeepSeek 开放平台：👉 [https://platform.deepseek.com/](https://platform.deepseek.com/)
2. 登录后进入「**API Keys**」页面
3. 点击「**Create API Key**」创建一个新 Key
4. **立即复制保存**（只显示一次，关掉就没了！）

> 📖 如需详细文档参考：👉 [https://api-docs.deepseek.com/zh-cn/](https://api-docs.deepseek.com/zh-cn/)
> 💰 查看额度消耗：👉 [https://platform.deepseek.com/usage](https://platform.deepseek.com/usage)

### 第二步：将 Key 保存到本地文件

在技能目录的 `references/` 文件夹中，找到或新建一个文件 `api_key.txt`，将你的 API Key 粘贴进去（**不要加引号或空格**，直接是 Key 本身），保存即可。

文件路径示例：
```
references/api_key.txt
```
文件内容格式：
```
sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

### 第三步：验证 Key 是否生效

配置完成后，说一句话测试一下，例如「用 V4 搜索一下今天北京的天气」，如果正常回复则说明配置成功 ✅。

---

## 二、触发条件

本技能在以下场景自动激活：

- 用户请求联网搜索（需要获取最新信息）
- 悟空内置模型出现 `llm_call_failed` 错误，需要降级调用
- 用户明确说「用 DeepSeek V4 帮我做 XX」「V4 搜索 XX」
- 复杂多步骤任务，内置模型无法稳定执行时

---

## 三、模型选择指南

本技能支持三个模型，首次使用时会自动进入**交互式选择菜单**，之后可随时重新选择。

### 模型对比一览

| 模型ID | 模型名称 | 输入价格 | 输出价格 | 推荐场景 |
|--------|----------|----------|----------|----------|
| `deepseek-chat` | DeepSeek V3 | $0.27/M | $1.10/M | ✅ **性价比首选**，日常对话、搜索、写作、翻译 |
| `deepseek-v4-flash` | DeepSeek V4 Flash | $0.28/M | $2.19/M | 🔥 V4 新版，速度快，适合需要 V4 能力的复杂分析、联网搜索 |
| `deepseek-v4-pro` | DeepSeek V4 Pro | $0.55/M | $2.75/M | 💎 V4 旗舰版，效果最好但成本最高，适合高精度任务、重要文档生成 |

### 如何重新选择模型

以下任一方式均可触发模型选择菜单：

1. **通过技能说明触发**：在对话中告诉助手「帮我切换 DeepSeek 模型」或「换一个模型试试」，助手会帮你调用技能并自动进入模型选择菜单
2. **直接运行脚本**：在技能目录的 `references/` 文件夹下，直接双击运行 `deepseek_call.py`，按提示操作

> 💡 选择模型后会自动保存到 `references/model.txt`，后续调用默认使用上次选择的模型，无需重复选择。

### 交互式选择菜单示意

```
🔷 请选择要使用的 DeepSeek 模型
====================================================================================

▶ deepseek-chat
  DeepSeek V3（deepseek-chat）
  ✅ 性价比最高，日常对话和搜索推荐
  💰 输入: $0.27/M | 输出: $1.10/M
  💡 搜索、信息查询、写作、翻译等日常任务

▶ deepseek-v4-flash
  DeepSeek V4 Flash（deepseek-v4-flash）
  🔥 V4 新版，速度快，适合需要 V4 能力的任务
  💰 输入: $0.28/M | 输出: $2.19/M
  💡 需要 V4 能力的复杂分析、联网搜索

▶ deepseek-v4-pro
  DeepSeek V4 Pro（deepseek-v4-pro）
  💎 V4 旗舰版，效果最好但成本最高
  💰 输入: $0.55/M | 输出: $2.75/M
  💡 高精度任务、重要文档生成、复杂推理

====================================================================================
提示: 输入编号 (1/2/3) 或直接输入模型ID
设置默认后，之后调用无需再次选择
====================================================================================

请选择 (1/2/3，回车确认):
```

---

## 四、核心能力

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `chat` | 基础对话模式 | 问答、写作、翻译、分析 |
| `search` | 联网搜索模式 | 获取实时信息、新闻、数据查询 |
| `tools` | 函数调用模式 | 需要调用外部工具的复杂任务 |

**支持的模型**：
- `deepseek-chat`（DeepSeek V3，稳定性好）
- `deepseek-v4-flash`（DeepSeek V4 Flash，速度快）
- `deepseek-v4-pro`（DeepSeek V4 Pro，高精度）

---

## 五、费用参考

| 模型 | 输入价格 | 输出价格 | 推荐场景 |
|------|----------|----------|----------|
| DeepSeek V3 (`deepseek-chat`) | $0.27/M | $1.10/M | ✅ 性价比首选，日常对话和搜索 |
| DeepSeek V4 Flash (`deepseek-v4-flash`) | $0.28/M | $2.19/M | 🔥 V4 新版，复杂分析与联网搜索 |
| DeepSeek V4 Pro (`deepseek-v4-pro`) | $0.55/M | $2.75/M | 💎 旗舰版，高精度任务与重要文档 |

> 💡 日常对话和搜索任务消耗很小，普通使用每月费用通常在几元以内。

---

## 六、使用示例

### 示例一：联网搜索
**用户**：用 V4 搜索一下今天珠海的天气

**执行流程**：
1. 技能识别为联网搜索任务 → 激活 `search` 模式
2. 读取本地 `api_key.txt` 获取用户 Key
3. 调用 DeepSeek 搜索 API
4. 返回整理后的结果

### 示例二：深度分析
**用户**：用 V4 分析一下当前AI行业的发展趋势

**执行流程**：
1. 技能识别为分析任务 → 激活 `chat` 模式
2. 结合联网搜索获取最新数据
3. DeepSeek V4 返回结构化分析报告

### 示例三：降级备用
**用户**：帮我搜一下今天的热点新闻

**执行流程**：
1. 内置模型执行失败（llm_call_failed）
2. 技能自动接管 → 走 DeepSeek V4 直连
3. 正常返回结果

---

## 七、错误排查

| 错误信息 | 原因 | 解决方法 |
|----------|------|----------|
| `api_key is empty` | 未配置 Key | 按上方第一步~第二步配置 |
| `Incorrect API key provided` | Key 错误或已失效 | 去平台重新创建 Key |
| `quota exceeded` | 额度用完了 | 去 [platform.deepseek.com/usage](https://platform.deepseek.com/usage) 充值 |
| `connection timeout` | 网络超时 | 重试一次，或检查网络环境 |
| 没有任何反应 | Key 文件格式不对 | 确认文件内只有 Key，无空格无引号 |

---

## 八、技术说明

**工作原理**：
本技能不依赖悟空内置模型路由，而是直接通过 Python `requests` 库向 DeepSeek API 发送 HTTP 请求，绕过模型路由层的工具调用限制。

**API 端点**：`https://api.deepseek.com/chat/completions`

**请求方式**：POST + Bearer Token 认证

**Key 读取优先级**：
1. 命令行参数 `--api_key`
2. 环境变量 `DEEPSEEK_API_KEY`
3. 本地文件 `references/api_key.txt`
4. 运行时提示用户输入

---

## 八、安全提示

- **不要将 API Key 分享给他人**，任何人拿到你的 Key 都可以消耗你的额度
- **不要将包含 Key 的技能包直接分享**，分享前删除 `api_key.txt` 内容
- 建议定期去平台查看用量，发现异常及时重置 Key

---

## 九、输出合约

本技能完成后必须输出：
- ✅ 实际调用结果（成功 / 失败 / 部分成功）
- 📌 使用的模型名称和调用模式
- ⚠️ 如失败，给出原因和下一步建议
