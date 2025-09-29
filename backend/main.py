from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import os
from auth import create_access_token, get_current_user, authenticate_user
from database import database, metadata
import crud
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Chat App - Async")

origins = ["http://0.0.0.0:5173", "http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup():
    await database.connect()
    # create tables if using sqlite for quick start
    from sqlalchemy.ext.asyncio import create_async_engine
    engine = create_async_engine(os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db"), future=True)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None

@app.post("/register")
async def register(payload: RegisterIn):
    exists = await crud.get_user_by_email(payload.email)
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await crud.create_user(payload.email, payload.password, payload.name)
    return {"id": user["id"], "email": user["email"]}

from fastapi.security import OAuth2PasswordRequestForm

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": str(user["id"]) })
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
async def me(user=Depends(get_current_user)):
    return {"id": user["id"], "email": user["email"], "name": user.get("name")}

@app.post("/chats")
async def create_chat(payload: dict, user=Depends(get_current_user)):
    chat = await crud.create_chat(user["id"], payload.get("title") or "New chat")
    return chat

@app.get("/chats")
async def list_chats(user=Depends(get_current_user)):
    return await crud.list_chats(user["id"])

@app.get("/chats/{chat_id}")
async def get_chat(chat_id: int, user=Depends(get_current_user)):
    chat = await crud.get_chat(user["id"], chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Not found")
    return chat

@app.delete("/chats/{chat_id}")
async def delete_chat(chat_id: int, user=Depends(get_current_user)):
    await crud.delete_chat(user["id"], chat_id)
    return {"ok": True}

@app.post("/chats/{chat_id}/messages")
async def post_message(chat_id: int, payload: dict, user=Depends(get_current_user)):
    message = await crud.add_message(user["id"], chat_id, payload.get("role","user"), payload.get("content",""))
    from openai_client import ask_openai_for_response
    if payload.get("role","user") == "user" and payload.get("content",""):
        assistant = await ask_openai_for_response(chat_id, user["id"], payload.get("content",""))
        await crud.add_message(user["id"], chat_id, "assistant", assistant)
        return {"assistant": assistant, "message": message}
    return message

@app.get("/chats/{chat_id}/messages")
async def get_messages(chat_id: int, user=Depends(get_current_user)):
    return await crud.get_messages(user["id"], chat_id)

class ChatUpdate(BaseModel):
    title: str

@app.put("/chats/{chat_id}")
async def update_chat(chat_id: int, update: ChatUpdate, user=Depends(get_current_user)):
    try:
        chat = await crud.rename_chat(user["id"], chat_id, update.title)
        return chat
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))




from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
# ------------------ FILES ------------------ #
@app.post("/chats/{chat_id}/files")
async def upload_file(
    chat_id: int,
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    contents = await file.read()
    saved = await crud.save_file(user["id"], chat_id, file.filename, contents)
    return {"message": "File uploaded successfully", "file": saved}


@app.get("/chats/{chat_id}/files")
async def get_files(chat_id: int, user=Depends(get_current_user)):
    return await crud.list_files(chat_id, user["id"])

