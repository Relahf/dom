from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, Form, Depends, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

from app.config import settings
from app.database import engine, Base, get_db, SessionLocal
from app.models import User, ChatMessage, File as FileModel
from app.auth import hash_password, verify_password, create_token, decode_token

# Create tables
Base.metadata.create_all(bind=engine)

# Create directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.BACKUP_DIR, exist_ok=True)

# FastAPI app
app = FastAPI(
    title=settings.APP_TITLE,
    description="Autonomous apartment hub",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
    
    async def disconnect(self, user_id: int, websocket: WebSocket):
        try:
            if user_id in self.active_connections:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:\n                    del self.active_connections[user_id]
        except:\n            pass
    
    async def broadcast(self, message: dict):
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                try:
                    await connection.send_json(message)
                except:\n                    pass

manager = ConnectionManager()

# ===== ROUTES =====

# Home
@app.get("/")\nasync def home():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Apartment Hub</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
            h1 { color: #333; }
            p { color: #666; }
            a { color: #0066cc; text-decoration: none; margin: 0 10px; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>🏢 Apartment Hub</h1>
        <p>Локальный хаб для вашего дома</p>
        <p><a href="/auth/login">Вход</a> | <a href="/auth/register">Регистрация</a></p>
    </body>
    </html>
    """)\n\n# Catch all (Captive Portal)
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    if not full_path.startswith(('static', 'api', 'ws')):
        return RedirectResponse(url="/", status_code=302)
    return {"error": "not found"}

# === AUTH ===
@app.post("/api/auth/register")
async def register(username: str = Form(...), password: str = Form(...), apartment: str = Form(...), db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User exists")
    
    is_first = db.query(User).count() == 0
    user = User(
        username=username,
        password_hash=hash_password(password),
        apartment=apartment,
        role="admin" if is_first else "resident"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_token({"sub": user.id})
    return {"token": token, "user_id": user.id, "role": user.role}

@app.post("/api/auth/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid")
    
    if user.is_blocked:
        raise HTTPException(status_code=403, detail="Blocked")
    
    token = create_token({"sub": user.id})
    return {"token": token, "user_id": user.id, "role": user.role}

# === CHAT ===
@app.get("/api/chat/messages")
async def get_messages(db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.is_deleted == False).order_by(ChatMessage.created_at.desc()).limit(50).all()
    return [{"id": m.id, "sender": m.sender.username, "content": m.content, "time": m.created_at.isoformat()} for m in reversed(messages)]

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, token: str):
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001)
        return
    
    user_id = payload.get("sub")
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        db.close()
        await websocket.close(code=4002)
        return
    
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            msg_data = json.loads(data)
            
            message = ChatMessage(
                sender_id=user_id,
                content=msg_data.get("content", "")[:settings.MAX_MESSAGE_LENGTH]
            )
            db.add(message)
            db.commit()
            
            await manager.broadcast({
                "type": "message",
                "id": message.id,
                "sender": user.username,
                "apartment": user.apartment,
                "content": message.content,
                "time": message.created_at.isoformat()
            })
    except WebSocketDisconnect:
        await manager.disconnect(user_id, websocket)
    finally:
        db.close()

# === FILES ===
@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    
    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail="File too large")
    
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {"filename": file.filename, "size": file_size_mb}

@app.get("/api/files")
async def list_files(db: Session = Depends(get_db)):
    files = db.query(FileModel).order_by(FileModel.created_at.desc()).all()
    return [{"id": f.id, "name": f.filename, "size": f.file_size} for f in files]

print("✅ Приложение готово!\")\n"
