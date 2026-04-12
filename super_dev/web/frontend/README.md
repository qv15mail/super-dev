# Super Dev Web UI

Frontend dashboard for the Super Dev pipeline — a single-page application that provides
visual access to project initialisation, workflow execution, phase monitoring, and expert
advice through the Super Dev REST API.

## 快速启动

The web API serves the compiled frontend automatically at `/` when the `dist/` directory
is present. Start the server with either command:

```bash
# Via CLI
super-dev web --port 8000

# Or directly with uvicorn (hot reload for API development)
uvicorn super_dev.web.api:app --reload --port 8000
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

## API 地址

| Prefix       | Description          |
|--------------|----------------------|
| `/api/`      | Current API (all endpoints below) |

## 核心接口

The frontend interacts with the following key endpoints:

| Method | Endpoint                             | 说明                     |
|--------|--------------------------------------|--------------------------|
| GET    | `/api/health`                        | 健康检查                 |
| GET    | `/api/config`                        | 获取项目配置              |
| POST   | `/api/init`                          | 初始化项目                |
| POST   | `/api/workflow/run`                  | 启动流水线                |
| GET    | `/api/workflow/status/{run_id}`      | 查询运行状态              |
| GET    | `/api/phases`                        | 列出流水线阶段            |
| GET    | `/api/experts`                       | 列出专家角色              |
| GET    | `/api/workflow/runs`                 | 列出历史运行              |
| POST   | `/api/workflow/docs-confirmation`    | 文档确认网关              |
| POST   | `/api/workflow/preview-confirmation` | 预览确认网关              |

> Endpoints that modify state require an API key (`Authorization` header).

## 技术栈

- **Framework**: Vue 3 (bundled as a single `index.html` — no build step required)
- **Styling**: Inline CSS, designed for dashboard use
- **Deployment**: Static files served via FastAPI `StaticFiles` mount

## 开发说明

- **Hot reload** (API only): `uvicorn super_dev.web.api:app --reload` watches `api.py`
  for changes and reloads automatically.
- **Frontend edits**: Modify `dist/index.html` directly, then refresh the browser.
  For a full rebuild, re-run the frontend build pipeline that generated the bundle.
- **API authentication**: Set `SUPER_DEV_API_KEY` environment variable to enable
  key-protected endpoints.
