# small-claude-code

一个轻量级的 Agent Harness 框架，受 Claude Code 启发。从零开始构建，包含所有核心模块，适用于商业场景。

## 特性

- **核心模块**: Agent 循环、消息处理、配置管理
- **工具集**: Bash、文件操作、搜索、Web 请求
- **权限控制**: 基于 Allow/Deny/Approve 规则的权限守卫
- **钩子系统**: 工具执行前后的扩展点
- **任务管理**: 持久化任务管理
- **上下文压缩**: 长对话的上下文管理
- **记忆系统**: 持久化内存存储
- **技能系统**: 从目录加载技能
- **子代理**: 并行子代理执行

## 快速开始

```bash
# 创建虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS

# 安装依赖
pip install -r requirements.txt
pip install pytest  # 可选，用于运行测试

# 运行示例
python examples/simple_agent.py        # 基础 agent 示例
python examples/task_agent.py          # 任务管理示例
python examples/permission_agent.py    # 权限守卫示例
python examples/memory_agent.py        # 记忆系统示例
python examples/subagent_example.py    # 子代理示例

# 运行测试
pytest

# 运行特定测试文件
pytest tests/test_core.py -v
```

## 环境变量

| 变量 | 描述 | 默认值 |
|------|------|--------|
| `ANTHROPIC_API_KEY` | Anthropic API 密钥（必填） | - |
| `ANTHROPIC_API_BASE` | API 基础 URL | `https://api.anthropic.com/v1` |
| `CLAUDE_MODEL` | 模型名称 | `claude-sonnet-4-20250514` |
| `CLAUDE_WORKDIR` | 文件操作的工作目录 | 当前目录 |
| `CLAUDE_TASKS_DIR` | 任务持久化目录 | `.tasks` |
| `CLAUDE_MEMORY_DIR` | 内存存储目录 | `.memory` |
| `CLAUDE_SKILLS_DIR` | 技能目录 | `.skills` |

## 使用示例

### 创建 Agent

```python
from small_claude_code import AgentLoop, Config
from small_claude_code.tools import BashTool, ReadTool

config = Config.from_env()
agent = AgentLoop(config)
agent.register_tool("bash", BashTool(workdir=str(config.workdir)))
agent.register_tool("read", ReadTool(workdir=str(config.workdir)))

result = agent.run("读取 README 文件")
print(result)
```

### 使用权限守卫

```python
from small_claude_code.permission import PermissionGuard, PermissionAction

guard = PermissionGuard()
guard.allow("bash", "ls *")           # 允许特定模式
guard.deny("bash", "rm -rf *")        # 拒绝危险命令
guard.deny("write", "*.env")          # 拒绝编辑 env 文件

# 包装单个工具
bash_tool = BashTool(workdir=str(config.workdir))

def safe_bash(**kwargs):
    result = guard.check("bash", kwargs)
    if result.action == PermissionAction.DENY:
        return f"Permission denied: {result.reason}"
    return bash_tool.execute(**kwargs).content

agent.register_tool("bash", safe_bash)
```

## 项目结构

```
small_claude_code/
├── core/           # 核心模块：Agent 循环、配置、消息
├── tools/          # 工具：bash、文件操作、搜索、web
├── permission/     # 权限守卫
├── hooks/          # 钩子系统
├── task/           # 任务管理
├── context/        # 上下文压缩
├── memory/         # 内存存储
├── skill/          # 技能加载
├── subagent/       # 子代理执行
├── examples/       # 示例代码
└── tests/          # 测试
```

## 许可证

MIT License