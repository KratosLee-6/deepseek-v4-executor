#!/usr/bin/env python3
"""
DeepSeek V4 Function Calling 工具定义
预定义常用工具的 schema，便于 MCP 模式调用
"""

# Web 搜索工具
WEB_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "搜索互联网获取最新信息。当用户需要查找实时新闻、天气、股价、百科知识等最新信息时使用。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询关键词。建议简洁明确，包含时间、地点等关键信息效果更好。"
                },
                "max_results": {
                    "type": "integer",
                    "description": "最大返回结果数，默认5条",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}

# 文件读取工具
FILE_READ_SCHEMA = {
    "type": "function",
    "function": {
        "name": "file_read",
        "description": "读取沙盒内的文件内容",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径，如 D:/App/wukong/workspace/xxx.md"
                },
                "start_line": {
                    "type": "integer",
                    "description": "起始行号，默认从头开始",
                    "default": 1
                },
                "end_line": {
                    "type": "integer",
                    "description": "结束行号，默认读到末尾",
                    "default": None
                }
            },
            "required": ["path"]
        }
    }
}

# 文件搜索工具
FILE_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "file_search",
        "description": "在沙盒工作空间内搜索文件或目录",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "搜索路径，默认搜索整个工作空间"
                },
                "pattern": {
                    "type": "string",
                    "description": "文件名匹配模式，支持通配符，如 *.py, **/*.md"
                },
                "query": {
                    "type": "string",
                    "description": "文件内容搜索关键词（grep 模式）"
                }
            },
            "required": []
        }
    }
}

# 知识搜索工具
KNOWLEDGE_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "knowledge_search",
        "description": "搜索悟空 AI 的知识库和会话历史",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词"
                },
                "scope": {
                    "type": "string",
                    "description": "搜索范围：current(当前会话) 或 cross(所有会话)",
                    "default": "current"
                }
            },
            "required": ["query"]
        }
    }
}

# 钉钉操作工具（常用子集）
DINGTALK_BASE_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "dingtalk_search_contact",
            "description": "在钉钉通讯录中搜索同事信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "同事姓名"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "dingtalk_send_message",
            "description": "向钉钉同事发送消息",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "用户ID"},
                    "content": {"type": "string", "description": "消息内容"}
                },
                "required": ["user_id", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "dingtalk_create_meeting",
            "description": "创建钉钉视频会议",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "会议主题"},
                    "duration": {"type": "integer", "description": "会议时长（分钟）"},
                    "participants": {"type": "array", "items": {"type": "string"}, "description": "参会人手机号列表"}
                },
                "required": ["title"]
            }
        }
    }
]

# 所有可用工具列表
ALL_TOOLS = [
    WEB_SEARCH_SCHEMA,
    FILE_READ_SCHEMA,
    FILE_SEARCH_SCHEMA,
    KNOWLEDGE_SEARCH_SCHEMA,
]

# 根据类别获取工具
def get_tools_by_category(category: str):
    """根据类别获取工具列表"""
    categories = {
        "web": [WEB_SEARCH_SCHEMA],
        "file": [FILE_READ_SCHEMA, FILE_SEARCH_SCHEMA],
        "knowledge": [KNOWLEDGE_SEARCH_SCHEMA],
        "dingtalk": DINGTALK_BASE_SCHEMAS,
        "all": ALL_TOOLS + DINGTALK_BASE_SCHEMAS,
    }
    return categories.get(category, ALL_TOOLS)


if __name__ == "__main__":
    print("📋 DeepSeek V4 可用工具 Schema:")
    print("-" * 40)
    for i, tool in enumerate(ALL_TOOLS, 1):
        print(f"{i}. {tool['function']['name']} - {tool['function']['description'][:50]}...")
