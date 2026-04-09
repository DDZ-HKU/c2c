# Claude Code LiteLLM Bridge

一个可公开分享的模板项目，用来把 Claude Code 的 Anthropic `/v1/messages` 请求转发到 OpenAI 兼容上游，并兼容 Claude 专属参数与模型名。

适用场景：

- 你想让 `claude` 走本地 LiteLLM 代理
- 你的上游是 OpenAI 官方，或任何 OpenAI-compatible API
- 你需要兼容 Claude Code 自带的 `thinking`、`context_management`、Claude 模型名

## 这个仓库是什么

这个仓库不是 LiteLLM 官方源码 fork。

它是一个很小的桥接模板仓库，只负责三类东西：

- LiteLLM 的配置模板
- Claude 请求兼容层
- 本地启动脚本

请求链路如下：

`Claude Code -> LiteLLM Proxy -> OpenAI-compatible upstream`

也就是说：

- Claude Code 继续按 Anthropic 风格发请求
- 本仓库里的兼容层把 Claude 风格字段清洗并重写
- LiteLLM Proxy 再把请求转发到 OpenAI 兼容上游

## 仓库里有哪些文件

- `README.md`
  - 使用说明
- `anthropic_compat.py`
  - Claude 请求兼容层
- `config.example.yaml`
  - LiteLLM Proxy 配置模板
- `start-litellm.sh`
  - 启动脚本
- `.env.example`
  - 环境变量示例
- `.gitignore`
  - 本地敏感文件和运行产物忽略规则

## 兼容层做了什么

`anthropic_compat.py` 主要做这几件事：

- 把 `claude-*`、`sonnet`、`opus`、`haiku` 等模型名映射到目标模型
- 删除 Anthropic 专属字段：
  - `thinking`
  - `context_management`
- 把 `thinking.budget_tokens` 保留到 `metadata`
- 在响应侧把返回模型名改回目标模型名

## LiteLLM Proxy 应该放在哪里

不需要把 LiteLLM 官方源码仓库克隆进这个项目。

正确方式是直接在这个仓库自己的虚拟环境里安装 LiteLLM Proxy：

```zsh
pip install "litellm[proxy]"
```

也就是说：

- 这个仓库保留配置和桥接逻辑
- LiteLLM Proxy 作为 Python 包安装到本仓库的虚拟环境里
- 不需要在仓库中再放一个 `litellm/` 官方源码目录

## 虚拟环境应该放在哪里

建议把虚拟环境直接放在仓库根目录下：

```text
./venv-litellm
```

原因：

- `start-litellm.sh` 默认就是从当前仓库的 `venv-litellm` 启动
- 仓库自包含，迁移更简单
- 不会污染别的项目环境

推荐目录结构：

```text
litellm-claude-bridge-template/
├── README.md
├── anthropic_compat.py
├── config.example.yaml
├── config.yaml
├── start-litellm.sh
└── venv-litellm/
```

## 安装步骤

以下命令都在仓库根目录执行。

### 1. 创建虚拟环境

```zsh
cd /path/to/this/repo
python3.11 -m venv venv-litellm
```

### 2. 激活虚拟环境并安装 LiteLLM Proxy

```zsh
source venv-litellm/bin/activate
pip install "litellm[proxy]"
cp config.example.yaml config.yaml
```

如果你的系统没有 `python3.11`，也可以改成你本机实际可用的 Python 版本，但需要保证 LiteLLM 可正常安装。

## 需要配置什么

至少需要配置以下环境变量：

```zsh
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="https://your-openai-compatible-host/v1"
export TARGET_MODEL="gpt-5.4"
```

含义：

- `OPENAI_API_KEY`
  - 你的上游 OpenAI-compatible API key
- `OPENAI_API_BASE`
  - 你的上游接口根地址，通常是 `.../v1`
- `TARGET_MODEL`
  - Claude 请求最终要映射到的目标模型，比如 `gpt-5.4`

如果你要启动 Claude Code 并让它走本地 LiteLLM，还需要：

```zsh
export LITELLM_USE_CHAT_COMPLETIONS_URL_FOR_ANTHROPIC_MESSAGES="1"
export ANTHROPIC_BASE_URL="http://127.0.0.1:4000"
export ANTHROPIC_MODEL="gpt-5.4"
export ANTHROPIC_SMALL_FAST_MODEL="gpt-5.4"
export ANTHROPIC_AUTH_TOKEN="litellm-local"
```

含义：

- `LITELLM_USE_CHAT_COMPLETIONS_URL_FOR_ANTHROPIC_MESSAGES`
  - 让 Claude Code 通过 LiteLLM 的 chat completions 兼容链路工作
- `ANTHROPIC_BASE_URL`
  - 指向本地 LiteLLM Proxy 地址
- `ANTHROPIC_MODEL`
  - Claude 主模型名
- `ANTHROPIC_SMALL_FAST_MODEL`
  - Claude 小模型名
- `ANTHROPIC_AUTH_TOKEN`
  - 传给本地 LiteLLM 的占位 token

## `config.yaml` 应该怎么来

先从模板复制：

```zsh
cp config.example.yaml config.yaml
```

默认配置里已经包含：

- `drop_params: true`
- `callbacks: ["anthropic_compat.proxy_handler_instance"]`

这两个配置很关键：

- `drop_params: true`
  - 让 LiteLLM 丢弃上游不认识的额外参数
- `callbacks`
  - 注册本仓库里的 Claude 兼容层

如果你想改目标模型，通常要一起检查这几个地方：

- `TARGET_MODEL` 环境变量
- `config.yaml`
- Claude 启动时的 `ANTHROPIC_MODEL`
- Claude 启动时的 `ANTHROPIC_SMALL_FAST_MODEL`

## 怎么启动

### 1. 启动 LiteLLM Proxy

方式一：

```zsh
cd /path/to/this/repo
source venv-litellm/bin/activate
litellm -c config.yaml --detailed_debug
```

方式二：

```zsh
cd /path/to/this/repo
./start-litellm.sh
```

`start-litellm.sh` 会做两件事：

- 激活 `./venv-litellm`
- 使用 `config.yaml` 启动 LiteLLM

### 2. 启动 Claude Code

在另一个终端里设置好环境变量后运行：

```zsh
claude
```

这样 Claude Code 的请求就会打到本地 `http://127.0.0.1:4000`，再由 LiteLLM 转发到你的 OpenAI 兼容上游。

## 一次性最短启动示例

```zsh
cd /path/to/this/repo
python3.11 -m venv venv-litellm
source venv-litellm/bin/activate
pip install "litellm[proxy]"
cp config.example.yaml config.yaml

export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="https://your-openai-compatible-host/v1"
export TARGET_MODEL="gpt-5.4"

./start-litellm.sh
```

然后另开一个终端：

```zsh
export LITELLM_USE_CHAT_COMPLETIONS_URL_FOR_ANTHROPIC_MESSAGES="1"
export ANTHROPIC_BASE_URL="http://127.0.0.1:4000"
export ANTHROPIC_MODEL="gpt-5.4"
export ANTHROPIC_SMALL_FAST_MODEL="gpt-5.4"
export ANTHROPIC_AUTH_TOKEN="litellm-local"

claude
```

## 注意事项

- 不要把真实 API key 提交到 GitHub
- 不要把真实 `.env` 提交到 GitHub
- 不要把真实 `config.yaml` 里的私有地址和私有 token 提交到 GitHub
- 不要提交 `venv-litellm/`
- 如果上游不是标准 OpenAI，请确认它兼容 `/chat/completions`

## 建议发布前检查

发布到 GitHub 前至少确认：

- 没有提交真实 `config.yaml`
- 没有提交真实 `.env`
- 没有提交本地数据库、日志、虚拟环境
- 没有提交私有上游地址和私有 token
