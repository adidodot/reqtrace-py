"""
Contoh penggunaan reqtrace dengan FastAPI.

Jalankan dengan:
    uvicorn examples.fastapi_example:app --reload

Lalu coba endpoint:
    GET  http://localhost:8000/users
    POST http://localhost:8000/users   body: {"name": "Diz", "email": "diz@mail.com"}
    GET  http://localhost:8000/users/99   (trigger 404)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from reqtrace import ReqTrace
from reqtrace.middleware import ReqTraceMiddleware


# -------------------------------------------------------------------
# Pilih salah satu konfigurasi di bawah untuk mencoba output mode:
# -------------------------------------------------------------------

# Mode 1: terminal only (default)
rt = ReqTrace(output="terminal")

# Mode 2: file only
# rt = ReqTrace(output="file", file_path="logs/trace.json")

# Mode 3: both
# rt = ReqTrace(output="both", file_path="logs/trace.txt", file_format="txt")

# -------------------------------------------------------------------

app = FastAPI(title="reqtrace example")
app.add_middleware(ReqTraceMiddleware, config=rt.config)


# --- fake data ---
_users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
]


class UserCreate(BaseModel):
    name: str
    email: str


@app.get("/users")
def list_users():
    return {"status": "ok", "data": _users}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = next((u for u in _users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return {"status": "ok", "data": user}


@app.post("/users", status_code=201)
def create_user(payload: UserCreate):
    new_user = {"id": len(_users) + 1, **payload.model_dump()}
    _users.append(new_user)
    return {"status": "ok", "data": new_user}
