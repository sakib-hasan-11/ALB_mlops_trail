# ALB_mlops_trail

Production-ready FastAPI chatbot backend (powered by OpenAI) and Streamlit frontend for AWS ECS Fargate deployment.

## Project Structure

```text
mlops_trails/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py
│   │       └── query.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── query.py
│   └── services/
│       ├── __init__.py
│       └── query_service.py
├── src/
│   └── __init__.py
├── api.py
├── main.py
├── streamlit_app.py
├── Dockerfile.api
├── Dockerfile.streamlit
├── .env.example
├── requirements.in
├── requirements.txt
└── README.md
```

## API Endpoints (All under /api)

- `GET /api/health` - Health check endpoint for ALB
- `POST /api/chat` - Send a chat message with optional conversation history

### /api/chat Request Payload
```json
{
  "message": "Hello, how are you?",
  "conversation_history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ]
}
```

### /api/chat Response Payload
```json
{
  "reply": "I'm doing well, thank you for asking!",
  "conversation_history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"},
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "assistant", "content": "I'm doing well, thank you for asking!"}
  ]
}
```

## Setup

1. Set your OpenAI API key in `.env`:
```bash
OPENAI_API_KEY=sk-...your-key-here...
```

2. Or set it as an environment variable:
```bash
export OPENAI_API_KEY=sk-...your-key-here...
```

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run FastAPI (required command):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Run Streamlit UI:

```bash
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

Set Streamlit API target (ALB DNS):

```bash
export HOST_API=http://your-alb-dns-name
```

On Windows PowerShell:

```powershell
$env:HOST_API = "http://your-alb-dns-name"
```

## AWS ECS / Fargate Notes

- Deploy FastAPI and Streamlit as separate ECS services (or tasks).
- FastAPI container listens on `8000`.
- Streamlit container listens on `8501`.
- Configure CloudWatch logs for both services.
- Use the ALB DNS as `HOST_API` for the Streamlit service.
- Provide `OPENAI_API_KEY` as a secret in ECS Task Definition.

## ALB /api/* Routing

Create an ALB listener rule:

- If path is `/api/*` -> forward to FastAPI target group (port 8000)
- Default rule (or another path rule) -> forward to Streamlit target group (port 8501)

Because FastAPI uses `APIRouter(prefix="/api")`, every application route starts with `/api`, which matches the ALB path condition and is routed to the backend service.

## Health Checks

- ALB health check path: `/api/health`
- Expected HTTP status: `200`
- Response body: `{ "status": "ok" }`

## Logging

- FastAPI outputs JSON logs suitable for CloudWatch ingestion with request ID, method, path, status code, and latency.
- Middleware logs request start, completion, latency, and request ID.
- Streamlit logs outbound chat API calls and errors to CloudWatch.
