# Claude Code LiteLLM Bridge

一个可公开分享的模板项目，用来把 Claude Code 的 Anthropic `/v1/messages` 请求转发到 OpenAI 兼容上游，并兼容 Claude 专属参数与模型名。

适用场景：

- 你想让 `claude` 走本地 LiteLLM 代理
- 你的上游是 OpenAI 官方，或任何 OpenAI-compatible API
- 你需要兼容 Claude Code 自带的 `thinking`、`context_management`、Claude 模型名

## 项目定位

适合你在以下场景直接复用：

- 想让 Claude Code 走本地 LiteLLM
- 想接入 OpenAI 官方或任意 OpenAI-compatible 上游
- 不想自己处理 `thinking`、`context_management`、Claude 模型别名兼容

## 请求链路

`Claude Code -> LiteLLM -> OpenAI-compatible upstream`

## 功能

- 把 `claude-*` / `sonnet` / `opus` / `haiku` 等模型名统一映射到目标模型
- 删除 Anthropic 专属字段：
  - `thinking`
  - `context_management`
- 保留 `thinking.budget_tokens` 到 metadata
- 使用 LiteLLM 转发到 OpenAI-compatible API

## 文件说明

- `config.example.yaml`
  - LiteLLM 示例配置
- `anthropic_compat.py`
  - Claude 请求兼容层
- `start-litellm.sh`
  - LiteLLM 启动脚本
- `.env.example`
  - 环境变量示例
- `.gitignore`
  - 建议忽略项

## 安装

### 1. 创建虚拟环境

```zsh
python3.11 -m venv venv-litellm
source venv-litellm/bin/activate
pip install "litellm[proxy]"
```

### 2. 配置环境变量

复制 `.env.example` 自行填写：

```zsh
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="https://your-openai-compatible-host/v1"
export TARGET_MODEL="gpt-5.4"
```

### 3. 复制配置文件

```zsh
cp config.example.yaml config.yaml
```

如果你想改默认模型，修改：

- `config.yaml`
- `anthropic_compat.py`
- Claude 启动环境变量

## 启动

### 1. 启动 LiteLLM

```zsh
source venv-litellm/bin/activate
litellm -c config.yaml --detailed_debug
```

或者：

```zsh
./start-litellm.sh
```

### 2. 启动 Claude Code

```zsh
export LITELLM_USE_CHAT_COMPLETIONS_URL_FOR_ANTHROPIC_MESSAGES="1"
export ANTHROPIC_BASE_URL="http://127.0.0.1:4000"
export ANTHROPIC_MODEL="gpt-5.4"
export ANTHROPIC_SMALL_FAST_MODEL="gpt-5.4"
export ANTHROPIC_AUTH_TOKEN="litellm-local"

claude
```

## LiteLLM 示例配置

见：

- `config.example.yaml`

重点配置项：

- `drop_params: true`
- `callbacks: ["anthropic_compat.proxy_handler_instance"]`

## 注意事项

- 不要把真实 API key 提交到 GitHub
- 推荐使用环境变量，而不是明文写进 `config.yaml`
- 如果你使用的上游不是标准 OpenAI，请确认它兼容 `/chat/completions`
- Claude Code 兼容模式建议保留：
  - `LITELLM_USE_CHAT_COMPLETIONS_URL_FOR_ANTHROPIC_MESSAGES=1`

## 建议发布方式

发布到 GitHub 前至少确认：

- 没有提交真实 `config.yaml`
- 没有提交真实 `.env`
- 没有提交本地数据库、日志、虚拟环境
- 没有提交私有上游地址和私有 token

## 推荐仓库名

- `claude-code-litellm-bridge`
- `claude-litellm-openai-bridge`
- `claude-code-openai-compatible-proxy`
