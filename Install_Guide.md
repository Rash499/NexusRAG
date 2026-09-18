Absolutely. Here is the current **NexusRAG development startup procedure**, with the folder and commands for each terminal.

## 1. FastAPI API

**Folder:**

```powershell
D:\NexusRAG\api
```

Open PowerShell:

```powershell
cd D:\NexusRAG\api
```

Activate the API virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Verify Python if needed:

```powershell
where.exe python
```

It should show:

```text
D:\NexusRAG\api\.venv\Scripts\python.exe
```

Start FastAPI:

```powershell
python -m uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Health:

```text
http://127.0.0.1:8000/health
```

**Keep this terminal running.**

---

## 2. Embedding Service

Open a **second PowerShell**.

**Folder:**

```powershell
D:\NexusRAG\embedding-service
```

Run:

```powershell
cd D:\NexusRAG\embedding-service
```

Activate its virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Verify Python if needed:

```powershell
where.exe python
```

It should show:

```text
D:\NexusRAG\embedding-service\.venv\Scripts\python.exe
```

Start the embedding service:

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Embedding service:

```text
http://127.0.0.1:8001
```

Swagger:

```text
http://127.0.0.1:8001/docs
```

**Keep this terminal running.**

---

## 3. Qdrant

If you're running Qdrant with Docker, open a **third PowerShell**.

First check:

```powershell
docker ps
```

If the Qdrant container is already running, you don't need to do anything.

If you need to start it:

```powershell
docker start qdrant
```

If your container has a different name, check:

```powershell
docker ps -a
```

Qdrant is normally available at:

```text
http://localhost:6333
```

You can test it with:

```powershell
Invoke-WebRequest http://localhost:6333
```

---

## 4. NexusRAG Frontend

Open a **fourth PowerShell**.

You need the folder containing your React/Vite project. If your frontend is, for example:

```text
D:\NexusRAG\frontend
```

run:

```powershell
cd D:\NexusRAG\frontend
```

Then:

```powershell
npm install
```

You only need `npm install` when dependencies have changed or this is a fresh checkout.

Start the frontend:

```powershell
npm run dev
```

It should give you something similar to:

```text
Local: http://localhost:5173/
```

Open:

```text
http://localhost:5173
```

---

# Complete setup

So you'll have **four terminals**:

### Terminal 1 — FastAPI

```powershell
cd D:\NexusRAG\api
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

### Terminal 2 — Embedding Service

```powershell
cd D:\NexusRAG\embedding-service
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Terminal 3 — Qdrant

If already created:

```powershell
docker start qdrant
```

Check:

```powershell
docker ps
```

### Terminal 4 — Frontend

```powershell
cd D:\NexusRAG\frontend
npm run dev
```

Then open:

```text
http://localhost:5173
```

---

## Quick health checks

Before using the frontend, you can verify the services individually.

### FastAPI

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health
```

Expected:

```text
{"status":"healthy"}
```

### Embedding service

Open:

```text
http://127.0.0.1:8001/docs
```

### Qdrant

```powershell
Invoke-WebRequest http://localhost:6333
```

### Frontend

Open:

```text
http://localhost:5173
```

---

### Important

Your `vite.config.js` now needs to retain this proxy:

```javascript
server: {
  proxy: {
    "/api": {
      target: "http://127.0.0.1:8000",
      changeOrigin: true
    }
  }
}
```

This is what makes:

```text
localhost:5173/api/v1/query
```

forward to:

```text
127.0.0.1:8000/api/v1/query
```

So **don't remove that configuration**.
