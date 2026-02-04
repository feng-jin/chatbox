---
name: Implement Chatbox
overview: 在当前目录（/Users/jinfeng/chatbot）按既定方案创建完整可运行项目结构与代码实现，包含后端 FastAPI、SQLite 持久化、RAG、前端与测试，并补齐 README 与一键启动流程。
todos: []
isProject: false
---

# 实施计划

## 目标与范围

- 以 `/Users/jinfeng/chatbot` 作为项目根目录（不再额外创建 `chatbox/` 子目录）。
- 生成与既定方案一致的目录结构、后端/前端代码、测试与文档。
- 保持 LLM 通过环境变量配置，可替换 provider。

## 主要交付物（按文件）

- 项目骨架：`[backend/app/](backend/app/)`、`[frontend/](frontend/)`、`[tests/](tests/)`、`[data/](data/)`、`[docs/](docs/)`、`[screenshots/](screenshots/)`。
- 后端入口与路由：`[backend/app/main.py](backend/app/main.py)`，`[backend/app/api/](backend/app/api/)`。
- 服务与核心模块：`[backend/app/services/](backend/app/services/)`、`[backend/app/core/](backend/app/core/)`。
- DB 层与模型：`[backend/app/db/](backend/app/db/)`。
- 前端页面：`[frontend/index.html](frontend/index.html)`、`[frontend/styles.css](frontend/styles.css)`、`[frontend/app.js](frontend/app.js)`。
- 测试用例与覆盖率配置：`[tests/](tests/)`。
- 配置与文档：`[pyproject.toml](pyproject.toml)`、`[.env.example](.env.example)`、`[README.md](README.md)`。

## 实施步骤

1. 初始化项目结构
  - 创建目录与空文件，确保与方案目录结构匹配。
  - 添加 `.gitignore`（至少忽略 `data/` 与本地环境文件）。
2. 后端基础框架与配置
  - 在 `backend/app/main.py` 搭建 FastAPI 应用与路由注册。
  - 在 `backend/app/core/config.py` 定义环境变量读取与默认值。
3. DB 层与持久化
  - 实现 `backend/app/db/database.py` 的 SQLite 连接与生命周期管理。
  - 在 `backend/app/db/models.py` 定义表结构与建表逻辑。
  - 在 `backend/app/db/repo.py` 提供 CRUD 与分页查询。
4. Service 层与业务逻辑
  - 会话/历史：`session_service.py` 负责会话创建与历史读写。
  - 聊天：`chat_service.py` 负责对话流程与消息存储。
  - RAG：`rag_service.py` 负责文件解析、切分、向量化与检索流程编排。
5. Core 层能力封装
  - `llm_client.py`：统一接口 + 可替换 provider 实现。
  - `embeddings.py`：向量化接口（可基于同一 LLM provider）。
  - `chunker.py`：文本切分策略与参数。
  - `prompt_builder.py`：拼接 system 指令与检索片段。
6. API 层路由实现
  - `routes_session.py`、`routes_chat.py`、`routes_files.py` 提供 REST API。
  - 定义请求/响应模型与错误处理规范。
7. 前端最小可用界面
  - 纯 HTML/CSS/JS 实现会话列表、对话窗、文件上传与请求调用。
  - 确保与后端 API 字段一致。
8. 测试与覆盖率
  - Service/Core 单元测试为主，API 路由基础集成测试。
  - 使用 mock LLM 保证测试稳定、可离线运行。
  - 在 README 记录覆盖率命令与目标阈值。
9. 文档与启动流程
  - README 包含安装、配置、启动、测试与常见问题。
  - `.env.example` 明确 LLM 相关配置项。

## 关键实现约束

- 仅使用 Python + uv + FastAPI + SQLite + 原生前端技术栈。
- 所有密钥与配置通过环境变量读取。
- 保持本地一键启动流程与测试流程可复现。

