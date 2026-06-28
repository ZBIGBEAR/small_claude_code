# small-claude-code

> 轻量级 Agent Harness 框架 - 从零构建你自己的 Coding Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)

## 简介

small-claude-code 是一个简洁但完整的 Agent Harness 框架，灵感来自 Claude Code。它教你如何围绕 AI 模型构建"载具"——工具、知识、上下文管理和权限，让 Agent 有效运作。

**Agent = Model + Harness**

模型提供智能，Harness 提供能力。本项目专注于构建 Harness。

## 核心哲学

> "智能——感知、推理和行动的能力——来自模型训练，而非外部代码编排。但一个可用的 Agent 产品需要模型和 Harness 两者。"

small-claude-code 剥离复杂性，只教授核心模式：
- 一个 Agent 循环
- 工具注册
- 权限边界
- 钩子扩展点
- 任务持久化
- 上下文管理
- 记忆存储
- Skill 加载
- 子代理协作

## 功能模块

| 模块 | 描述 |
|------|------|
| **core** | Agent 循环、消息处理、配置 |
| **tools** | Bash、文件操作、搜索、Web 获取 |
| **permission** | 允许/拒绝/审批规则 |
| **hooks** | 工具执行前后钩子 |
| **task** | 任务管理与依赖 |
| **context** | 长对话上下文压缩 |
| **memory** | 跨会话持久化记忆 |
| **skill** | 模块化 Skill 加载系统 |
| **subagent** | 并行子代理执行 |

## 快速开始

### 安装

```bash
# 创建虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
pip install pytest  # 可选，用于运行测试
```

### 环境配置

```bash
export ANTHROPIC_API_KEY="your-api-key"
export CLAUDE_MODEL="claude-sonnet-4-20250514"  # 可选
export CLAUDE_WORKDIR="/path/to/workdir"        # 可选
```

### 简单 Agent

```python
from small_claude_code import AgentLoop, Config, BashTool, ReadTool

# 创建配置
config = Config.from_env()
config.system_prompt = "你是一个有用的编程助手。"

# 创建 Agent
agent = AgentLoop(config)

# 注册工具（需要指定 workdir）
agent.register_tool("bash", BashTool(workdir=str(config.workdir)))
agent.register_tool("read", ReadTool(workdir=str(config.workdir)))

# 执行任务
result = agent.run("列出当前目录的文件")
print(result)
```

### 带权限守卫

```python
from small_claude_code import AgentLoop, Config, BashTool, ReadTool
from small_claude_code.permission import PermissionGuard, PermissionAction

# 创建权限守卫
guard = PermissionGuard()
guard.allow("read", "**/*")        # 允许所有读取
guard.approve("bash", "**/*")      # Bash 需要审批
guard.deny("bash", "rm -rf /**")  # 禁止危险命令

# 创建工具
bash_tool = BashTool(workdir=str(config.workdir))

# 包装工具
def safe_bash(**kwargs):
    result = guard.check("bash", kwargs)
    if result.action == PermissionAction.DENY:
        return f"拒绝: {result.reason}"
    return bash_tool.execute(**kwargs).content

# 注册工具
agent.register_tool("bash", safe_bash)
agent.register_tool("read", ReadTool(workdir=str(config.workdir)))
```

### 带任务管理

```python
from small_claude_code.task import TaskManager, TaskStatus

task_manager = TaskManager()

# 创建任务及依赖
task1 = task_manager.create_task(title="探索项目结构")
task2 = task_manager.create_task(
    title="分析代码",
    blocked_by=[task1.id]
)

# 执行就绪任务
for task in task_manager.get_ready_tasks():
    task_manager.update_task(task.id, TaskStatus.IN_PROGRESS)
    result = agent.run(task.description)
    task_manager.update_task(task.id, TaskStatus.COMPLETED, result=result)
```

## 项目结构

```
small-claude-code/
├── small_claude_code/       # 主包
│   ├── core/           # Agent 循环和消息处理
│   ├── tools/          # 工具实现
│   ├── permission/     # 权限守卫
│   ├── hooks/          # 钩子系统
│   ├── task/           # 任务管理
│   ├── context/        # 上下文压缩
│   ├── memory/         # 记忆存储
│   ├── skill/          # Skill 加载器
│   └── subagent/       # 子代理运行器
├── examples/           # 示例代码
└── tests/              # 单元测试
```

## 架构

```
                    THE AGENT PATTERN
                    =================

    User --> messages[] --> LLM --> response
                                      |
                            stop_reason == "tool_use"?
                           /                          \
                         yes                           no
                          |                             |
                    execute tools                  return text
                    append results
                    loop back -----------------> messages[]


    模型决定何时调用工具，何时停止。
    Harness 只执行模型的请求。
```

## 示例

| 示例 | 描述 |
|------|------|
| `simple_agent.py` | 基础 Agent + 工具 |
| `task_agent.py` | 任务管理与跟踪 |
| `permission_agent.py` | 权限守卫设置 |
| `memory_agent.py` | 持久化记忆 |
| `subagent_example.py` | 并行子代理 |

## 运行示例

```bash
# 配置环境变量
export ANTHROPIC_API_KEY="your-key"

# 运行简单 Agent
python examples/simple_agent.py

# 运行任务管理示例
python examples/task_agent.py
```

## 运行测试

```bash
pytest tests/ -v
```

## 与 learn-claude-code 对比

本项目是 [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) 的**简化商业版本**：

| 方面 | learn-claude-code | small-claude-code |
|------|------------------|-------------------|
| 目的 | 教育/教程 | 生产可用 |
| 课程 | 20 个渐进章节 | 核心模块 |
| 复杂度 | 面向学习 | 简洁清晰 |
| 文档 | 详尽 | 专注 API |
| 结构 | 教学模块 | 包结构 |

## 商业使用

small-claude-code 为商业使用设计：

- **MIT 许可证** - 可在商业项目中自由使用
- **最小依赖** - 仅需 `anthropic` SDK
- **模块化设计** - 按需使用
- **完整测试** - 核心模块单元测试
- **文档完善** - 清晰的文档字符串和示例

## 扩展 Harness

### 添加自定义工具

```python
from small_claude_code.tools.base import BaseTool, ToolResult

class MyTool(BaseTool):
    name = "my_tool"
    description = "做有用的事情"

    def execute(self, param: str) -> ToolResult:
        return ToolResult(success=True, content=f"结果: {param}")

agent.register_tool("my_tool", MyTool())
```

### 添加钩子

```python
from small_claude_code.hooks import HookManager, HookType

def log_pre_tool(tool_name, params):
    print(f"执行 {tool_name}")

def log_post_tool(tool_name, result):
    print(f"完成 {tool_name}")

hooks = HookManager()
hooks.pre_tool("logger", log_pre_tool)
hooks.post_tool("logger", log_post_tool)
```

## 贡献

欢迎贡献！请：

1. Fork 仓库
2. 创建功能分支
3. 添加新功能测试
4. 确保所有测试通过
5. 提交 Pull Request

## 许可证

MIT 许可证 - 见 [LICENSE](LICENSE)。

## 致谢

灵感来自 [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) - "Bash is all you need."

---

**把 Harness 构建好。模型会完成剩下的工作。**
