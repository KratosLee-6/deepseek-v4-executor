#!/usr/bin/env python3
"""
DeepSeek V4 API 调用脚本
用法: python deepseek_call.py --task "任务描述" --mode [chat|search|tools] --api_key "YOUR_API_KEY"
"""

import argparse
import json
import sys
import os
import time
import re
from typing import Optional, List, Dict, Any

try:
    import requests
except ImportError:
    print("ERROR: requests 库未安装，正在安装...")
    os.system("pip install requests -q")
    import requests


# ===================== 配置区 =====================
DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TIMEOUT = 120  # 秒
MAX_RETRIES = 2
# =================================================


def parse_args():
    parser = argparse.ArgumentParser(description="DeepSeek V4 API 调用工具")
    parser.add_argument("--task", "-t", type=str, required=True, help="用户任务描述")
    parser.add_argument("--mode", "-m", type=str, default="chat",
                        choices=["chat", "search", "tools"],
                        help="调用模式: chat(基础对话), search(联网搜索), tools(函数调用)")
    parser.add_argument("--api_key", "-k", type=str, default=None, help="DeepSeek API Key")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="模型名称")
    parser.add_argument("--stream", action="store_true", help="启用流式输出")
    parser.add_argument("--system_prompt", type=str, default=None, help="自定义系统提示词")
    parser.add_argument("--max_tokens", type=int, default=4096, help="最大输出token数")
    return parser.parse_args()


def load_api_key(api_key: Optional[str]) -> str:
    """获取 API Key，优先级：参数 > 环境变量 > 用户输入"""
    if api_key:
        return api_key

    env_key = os.environ.get("DEEPSEEK_API_KEY")
    if env_key:
        return env_key

    # 尝试从配置文件读取
    config_path = os.path.join(os.path.dirname(__file__), "api_key.txt")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    # 提示用户输入
    print("⚠️ 未提供 API Key，请输入您的 DeepSeek API Key:")
    key = input().strip()
    if not key:
        raise ValueError("API Key 不能为空")
    return key


def build_messages(task: str, system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
    """构建对话消息列表"""
    system_default = """你是一个智能助手，可以帮助用户完成各种任务。
- 搜索任务时，请提供准确、简洁的信息
- 分析任务时，请结构化输出
- 编程任务时，请提供完整可运行的代码"""

    messages = [
        {"role": "system", "content": system_prompt or system_default},
        {"role": "user", "content": task}
    ]
    return messages


def build_headers(api_key: str) -> Dict[str, str]:
    """构建请求头"""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def build_payload(args: argparse.Namespace, messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """构建请求体"""
    payload = {
        "model": args.model,
        "messages": messages,
        "max_tokens": args.max_tokens,
        "stream": args.stream
    }

    # 根据模式添加额外参数
    if args.mode == "search":
        # 联网搜索模式：DeepSeek V3 及以后版本通过系统提示词启用搜索
        messages[0]["content"] += "\n\n请使用网络搜索功能获取最新信息。"
    elif args.mode == "tools":
        # 函数调用模式：添加工具定义
        payload["tools"] = [
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "搜索互联网获取最新信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "搜索关键词"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculator",
                    "description": "执行数学计算",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string", "description": "数学表达式"}
                        },
                        "required": ["expression"]
                    }
                }
            }
        ]
        # 修改系统提示词引导模型使用工具
        messages[0]["content"] += "\n\n你可以使用 web_search 工具进行联网搜索。"

    return payload


def parse_search_result(content: str) -> Dict[str, Any]:
    """解析搜索结果，提取关键信息"""
    result = {
        "answer": "",
        "sources": [],
        "raw": content
    }

    # 尝试提取结构化信息
    try:
        # 如果返回的是 JSON 格式
        if content.strip().startswith("{"):
            result = json.loads(content)
        else:
            # 纯文本处理
            result["answer"] = content

            # 提取可能存在的来源链接
            url_pattern = r'https?://[^\s\)）]+'
            urls = re.findall(url_pattern, content)
            result["sources"] = list(set(urls))[:5]  # 最多5个来源

    except json.JSONDecodeError:
        result["answer"] = content

    return result


def call_deepseek_api(api_key: str, payload: Dict[str, Any], base_url: str = DEFAULT_BASE_URL) -> Dict[str, Any]:
    """发送请求到 DeepSeek API"""
    url = f"{base_url}/chat/completions"
    headers = build_headers(api_key)

    retry_count = 0
    last_error = None

    while retry_count <= MAX_RETRIES:
        try:
            print(f"\n📡 正在调用 DeepSeek API (尝试 {retry_count + 1}/{MAX_RETRIES + 1})...")
            print(f"📋 模型: {payload.get('model')}")

            start_time = time.time()

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=DEFAULT_TIMEOUT
            )

            elapsed = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                usage = result.get("usage", {})
                print(f"✅ 请求成功！耗时: {elapsed:.2f}s")
                print(f"📊 Token 使用: 输入 {usage.get('prompt_tokens', 0)}, 输出 {usage.get('completion_tokens', 0)}")
                return result
            else:
                error_info = response.json() if response.content else {}
                error_msg = error_info.get("error", {}).get("message", response.text)
                print(f"❌ API 返回错误 (状态码 {response.status_code}): {error_msg}")

                # 根据错误类型决定是否重试
                if response.status_code in [429, 500, 502, 503]:
                    retry_count += 1
                    wait_time = 2 ** retry_count
                    print(f"⏳ {wait_time}秒后重试...")
                    time.sleep(wait_time)
                    last_error = error_msg
                    continue
                else:
                    return {"error": error_msg, "status_code": response.status_code}

        except requests.exceptions.Timeout:
            print(f"❌ 请求超时（{DEFAULT_TIMEOUT}秒）")
            retry_count += 1
            if retry_count <= MAX_RETRIES:
                print("⏳ 正在重试...")
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求失败: {str(e)}")
            last_error = str(e)
            break

    return {"error": last_error or "多次重试后仍未成功"}


def format_output(result: Dict[str, Any], mode: str) -> str:
    """格式化输出"""
    if "error" in result:
        return f"❌ 调用失败: {result['error']}"

    try:
        choices = result.get("choices", [])
        if not choices:
            return "❌ 响应为空，未找到有效回复"

        message = choices[0].get("message", {})
        content = message.get("content", "")

        if mode == "search":
            parsed = parse_search_result(content)
            output = f"🔍 搜索结果:\n\n{parsed['answer']}"
            if parsed.get("sources"):
                output += "\n\n📎 参考来源:\n" + "\n".join([f"- {url}" for url in parsed["sources"]])
            return output
        else:
            return f"💬 DeepSeek V4 回答:\n\n{content}"

    except Exception as e:
        return f"❌ 解析响应失败: {str(e)}\n\n原始响应: {json.dumps(result, ensure_ascii=False, indent=2)}"


def main():
    args = parse_args()

    print("=" * 50)
    print("🔷 DeepSeek V4 执行层工具")
    print("=" * 50)
    print(f"📌 任务: {args.task}")
    print(f"📌 模式: {args.mode}")
    print(f"📌 模型: {args.model}")

    try:
        # 1. 获取 API Key
        api_key = load_api_key(args.api_key)
        masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
        print(f"🔑 API Key: {masked_key}")

        # 2. 构建消息
        messages = build_messages(args.task, args.system_prompt)

        # 3. 构建请求体
        payload = build_payload(args, messages)

        # 4. 发送请求
        result = call_deepseek_api(api_key, payload)

        # 5. 格式化输出
        output = format_output(result, args.mode)
        print("\n" + "=" * 50)
        print(output)

        # 保存结果到文件
        output_file = os.path.join(os.path.dirname(__file__), "last_result.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存到: {output_file}")

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
