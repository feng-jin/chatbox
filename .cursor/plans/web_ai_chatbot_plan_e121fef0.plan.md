---
name: Web AI Chatbot Plan
overview: 为基于 FastAPI+SQLite+原生前端的 Web AI Chatbot 提供可执行的端到端实现方案，覆盖架构、模块分层、API 设计、RAG 流程、测试与启动配置。
todos: []
isProject: false
---

# Web 端 AI Chatbot 项目方案

## 1. 总体系统架构设计

- 结构：Browser 前端 + FastAPI 后端 + SQLite 持久化 + 外部 LLM API + 本地向量检索模块。
- 交互流程：前端通过 `fetch` 调用后端 API；后端处理会话/消息/文件上传/检索；RAG 拼接 Prompt 后调用 LLM；结果写入 SQLite 并返回。
- 模块关系：API 层负责路由与校验；Service 层承载会话、对话、RAG 协调；Core 层提供 LLM/向量化/切分等核心能力；DB 层封装 SQLite CRUD 与迁移；Utils 提供通用工具。

## 2. 推荐的项目目录结构（目录树）

```
chatbox/
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routes_chat.py
│       │   ├── routes_session.py
│       │   └── routes_files.py
│       ├── services/
│       │   ├── chat_service.py
│       │   ├── rag_service.py
│       │   └── session_service.py
│       ├── core/
│       │   ├── llm_client.py
│       │   ├── embeddings.py
│       │   ├── chunker.py
│       │   ├── prompt_builder.py
│       │   └── config.py
│       ├── db/
│       │   ├── database.py
│       │   ├── models.py
│       │   └── repo.py
│       └── utils/
│           └── file_parser.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── tests/
│   ├── api/
│   ├── services/
│   └── core/
├── data/              # gitignore
│   ├── chat.db
│   ├── uploads/
│   └── faiss/
├── docs/
│   └── plan.md
├── screenshots/
├── pyproject.toml
├── .env.example
└── README.md
```

## 3. 后端模块分层设计（职责划分）

- API 层（`[chatbox/backend/app/api/*](chatbox/backend/app/api/)`）：定义路由、参数校验、错误响应规范、调用 Service。
- Service 层（`[chatbox/backend/app/services/*](chatbox/backend/app/services/)`）：实现业务流程编排（会话创建、消息存储、RAG 管线执行）。
- Core 层（`[chatbox/backend/app/core/*](chatbox/backend/app/core/)`）：封装 LLM/Embedding/切分/Prompt 构造与配置，做到可替换、可测试。
- DB 层（`[chatbox/backend/app/db/*](chatbox/backend/app/db/)`）：统一 SQLite 连接、表结构、CRUD、事务与迁移。

## 4. 核心 API 设计（示例请求/响应）

- 会话管理
  - `POST /api/sessions`
    - 请求：`{ "title": "可选标题" }`
    - 响应：`{ "session_id": "uuid", "title": "...", "created_at": "..." }`
  - `GET /api/sessions`
    - 响应：`{ "items": [{ "session_id": "uuid", "title": "...", "updated_at": "..." }] }`
- 聊天接口
  - `POST /api/chat`
    - 请求：`{ "session_id": "uuid", "message": "用户输入", "use_rag": true, "file_ids": ["file_id1"] }`
    - 响应：`{ "assistant_message": "...", "citations": [{"file_id":"...","chunk_id":"..."}], "token_usage": {"prompt":123,"completion":45} }`
- 文件上传接口
  - `POST /api/files`
    - 请求：`multipart/form-data`，字段 `file`
    - 响应：`{ "file_id": "uuid", "filename": "...", "status": "indexed" }`
- 历史加载接口
  - `GET /api/history?session_id=uuid&limit=50&before=timestamp`
    - 响应：`{ "items": [{"role":"user","content":"...","created_at":"..."}] }`

## 5. 对话历史持久化方案（SQLite 表结构）

- 表：`sessions`
  - 字段：`id (PK)`, `title`, `created_at`, `updated_at`
- 表：`messages`
  - 字段：`id (PK)`, `session_id (FK)`, `role`, `content`, `created_at`
- 表：`files`
  - 字段：`id (PK)`, `session_id (FK 可空)`, `filename`, `mime_type`, `path`, `created_at`
- 表：`chunks`
  - 字段：`id (PK)`, `file_id (FK)`, `chunk_index`, `content`, `embedding (BLOB/JSON)`, `created_at`
- 索引建议：`messages(session_id, created_at)`，`chunks(file_id, chunk_index)`，`sessions(updated_at)`

## 6. 文件问答（RAG）完整流程

- 上传：`/api/files` 接收文件并落盘/内存缓存，写 `files` 表。
- 解析：支持 txt/pdf/docx（最小可行先 txt/pdf）；解析为纯文本。
- 切分：按字符数或段落切分（如 500-1000 字），保留 chunk 元数据。
- 向量化：调用 Embedding 模块将 chunk 转成向量，写入 `chunks` 表。
- 检索：对用户问题向量化，计算与 chunk 相似度（余弦），取 Top-K。
- Prompt 拼接：系统指令 + 检索片段 + 用户问题，控制上下文长度。
- 回答生成：调用 LLM，返回答案和引用信息。

## 7. 多文件与长文档处理策略

- 最小可行方案
  - 限制单文件大小与总上传大小（如 5MB/文件，20MB/会话）。
  - 长文档采用固定窗口切分 + Top-K 检索（K=3-5）。
  - 多文件统一检索，按相似度混排。
- 可加分优化方案
  - 先做文件级粗检索（基于标题/摘要）再做 chunk 细检索。
  - 引入重排序（re-rank）或多查询扩展。
  - 支持分段摘要存储，降低上下文长度。

## 8. LLM 调用封装设计

- 统一接口：`LLMClient`（输入 prompt/消息，输出回复+token 使用）。
- 配置驱动：`[chatbox/backend/app/core/config.py](chatbox/backend/app/core/config.py)` 读取 `LLM_PROVIDER`、`LLM_API_KEY`、`LLM_MODEL` 等环境变量。
- 可替换实现：按 provider 分离实现类（如 `GeminiClient`, `DeepSeekClient`）。
- 测试友好：接口允许注入 mock 实现，Service 只依赖接口而非具体实现。

## 9. 单元测试设计方案

- 必测模块
  - RAG 流程：切分、向量化接口调用、检索排序逻辑。
  - 会话/消息 Service：创建、存储、分页加载。
  - API 路由：基础请求校验、错误返回。
- Mock 外部 LLM
  - 使用依赖注入或 monkeypatch，将 `LLMClient` 替换为固定响应的 Fake。
- 覆盖率 >50% 的策略
  - 重点覆盖 Service 与 Core（业务逻辑高密度）。
  - API 仅做轻量集成测试（FastAPI TestClient）。
  - 利用参数化测试覆盖不同边界输入。

## 10. 环境配置与启动方案

- uv 使用方式
  - 依赖放入 `[chatbox/pyproject.toml](chatbox/pyproject.toml)`，使用 `uv sync` 安装。
- 依赖安装
  - 后端：FastAPI、uvicorn、pydantic、pytest、coverage、sqlite 相关库、解析库（如 pdfplumber）。
- API Key 配置
  - `.env.example` 提供 `LLM_PROVIDER=...`、`LLM_API_KEY=...`、`LLM_MODEL=...`、`DATABASE_URL=sqlite:///...`。
- 一键启动（README 中给出以下流程）
  - `## Run`
  - `### 1. Install dependencies`
  - `uv sync`
  - `### 2. Configure environment`
  - `cp .env.example .env`
  - `# edit .env to set LLM_API_KEY`
  - `### 3. Start server`
  - `uv run uvicorn backend.app.main:app --reload`
  - `### 4. Open in browser`
  - `Open http://127.0.0.1:8000`

## 11. 潜在技术风险点与规避方案（>=5）

- 向量化成本/速率限制：增加缓存与批处理，限制上传大小。
- SQLite 并发写入冲突：使用单连接与事务，避免多线程并发写。
- Prompt 超长导致失败：控制 Top-K 与 chunk 长度，截断策略。
- 文件解析失败/乱码：捕获异常，返回友好错误并记录日志。
- LLM 不稳定或超时：设置重试与超时，降级为纯对话。
- 测试覆盖率不足：优先测试 Service/Core，确保核心逻辑覆盖。

## 12. 按步骤拆解的开发计划

- Step 1：搭建项目骨架与目录；配置 uv；FastAPI 启动与健康检查。
- Step 2：实现会话与消息存储（SQLite 表与 CRUD）；基本 API 可用。
- Step 3：实现文件上传、解析与切分；chunk 存储。
- Step 4：实现向量化与检索；RAG 流程打通。
- Step 5：封装 LLM 客户端；完成聊天接口与前端简单 UI。
- Step 6：编写测试与提高覆盖率；补充 README 与一键启动说明。

## 实施 Todo

- 确认目录结构与 API 清单
- 完成数据库表与核心 Service 设计
- 打通 RAG + LLM 流程并联调
- 补齐测试与 README 文档

