from database import database
from models import users, chats, messages
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MAX_PASSWORD_LEN = 72

def hash_password(password: str):
    return pwd_context.hash(password[:MAX_PASSWORD_LEN])

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain[:MAX_PASSWORD_LEN], hashed)

async def get_user_by_email(email: str):
    query = users.select().where(users.c.email == email)
    return await database.fetch_one(query)

async def get_user_by_id(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)

async def create_user(email: str, password: str, name: str | None = None):
    hashed = hash_password(password)
    print(hashed, "*********************")
    query = users.insert().values(email=email, hashed_password=hashed, name=name)
    user_id = await database.execute(query)
    return {"id": user_id, "email": email, "name": name}

async def create_chat(user_id: int, title: str):
    query = chats.insert().values(user_id=user_id, title=title)
    chat_id = await database.execute(query)
    return {"id": chat_id, "user_id": user_id, "title": title}

async def list_chats(user_id: int):
    query = chats.select().where(chats.c.user_id == user_id).order_by(chats.c.created_at.desc())
    return await database.fetch_all(query)

async def get_chat(user_id: int, chat_id: int):
    query = chats.select().where(chats.c.user_id == user_id).where(chats.c.id == chat_id)
    return await database.fetch_one(query)

async def delete_chat(user_id: int, chat_id: int):
    query = chats.delete().where(chats.c.user_id == user_id).where(chats.c.id == chat_id)
    await database.execute(query)

async def add_message(user_id: int, chat_id: int, role: str, content: str):
    c = await get_chat(user_id, chat_id)
    if not c:
        raise Exception("Chat not found or unauthorized")
    query = messages.insert().values(chat_id=chat_id, role=role, content=content)
    msg_id = await database.execute(query)
    return {"id": msg_id, "chat_id": chat_id, "role": role, "content": content}

async def get_messages(user_id: int, chat_id: int):
    c = await get_chat(user_id, chat_id)
    if not c:
        return []
    query = messages.select().where(messages.c.chat_id == chat_id).order_by(messages.c.created_at.asc())
    return await database.fetch_all(query)
