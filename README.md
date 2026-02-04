# Chatbox

Web 端 AI 对话系统：多轮对话、文件上传与 RAG 问答、历史持久化。

## 技术栈

- 后端：Python + uv + FastAPI
- 数据库：SQLite
- 前端：原生 HTML + CSS + JavaScript
- LLM：可配置第三方 API（Gemini / DeepSeek 等），密钥通过环境变量配置

## 前置要求

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)（推荐）或 pip

## Run

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
# edit .env to set LLM_API_KEY
```

### 3. Start server

从项目根目录执行：

```bash
uv run uvicorn backend.app.main:app --reload
```

若提示找不到 `backend` 模块，可先设置 PYTHONPATH 再启动：

```bash
PYTHONPATH=. uv run uvicorn backend.app.main:app --reload
```

### 4. Open in browser

打开 http://127.0.0.1:8000

前端由 FastAPI 挂载静态文件提供；健康检查：http://127.0.0.1:8000/health

## 测试

```bash
uv run pytest tests/ -v
```

覆盖率（目标 >50%）：

```bash
uv run pytest tests/ --cov=backend --cov-report=term-missing
```

## 环境变量说明

| 变量 | 说明 | 默认 |
|------|------|------|
| LLM_PROVIDER | 模型提供商：gemini / deepseek / mock | gemini |
| LLM_API_KEY | API 密钥 | - |
| LLM_MODEL | 模型名 | gemini-2.0-flash |
| DATABASE_URL | SQLite 路径，如 sqlite:///data/chat.db | sqlite:///data/chat.db |
| DATA_DIR | 数据目录（上传、DB 等） | data |

## 项目结构

- `backend/app/`：FastAPI 应用（api / services / core / db / utils）
- `frontend/`：静态页面与脚本
- `tests/`：单元与 API 测试
- `data/`：SQLite、上传文件等（已 gitignore）

## API 概览

- `POST /api/sessions`：创建会话
- `GET /api/sessions`：会话列表
- `GET /api/history?session_id=...`：历史消息
- `POST /api/chat`：发送消息并获取回复（可选 use_rag、file_ids）
- `POST /api/files`：上传文件（multipart/form-data）

## License

MIT
