"""
Contoh penggunaan reqtrace v0.2.0 dengan FastAPI.

Jalankan dengan:
    uvicorn examples.fastapi_example:app --reload

Lalu coba endpoint:
    GET  http://localhost:8000/users
    POST http://localhost:8000/users   body: {"name": "Diz", "email": "diz@mail.com"}
    GET  http://localhost:8000/users/99   (trigger 404)

Untuk melihat diff:
    Panggil GET /users dua kali — reqtrace akan otomatis menampilkan diff
    jika ada perubahan response.

Keyboard shortcut:
    Tekan 'c' di terminal untuk clear output.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from reqtrace import ReqTrace
from reqtrace.middleware import ReqTraceMiddleware


# -------------------------------------------------------------------
# Pilih salah satu konfigurasi:
# -------------------------------------------------------------------

# Mode 1: terminal + auto-diff (default contoh ini)
rt = ReqTrace(output="terminal", diff=True)

# Mode 2: file only
# rt = ReqTrace(output="file", file_path="logs/trace.json")

# Mode 3: both + diff
# rt = ReqTrace(output="both", file_path="logs/trace.json", diff=True)

# Mode 4: nonaktifkan clear key
# rt = ReqTrace(output="terminal", diff=True, clear_key=None)

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
