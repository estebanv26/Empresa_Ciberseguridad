# auth.py
import bcrypt
from db import usuarios_col, auditorias_col
from datetime import datetime
from bson.binary import Binary

# Encripta la contraseña
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

# Verifica la contraseña
def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed)

# Registro de usuario
def register_user(email: str, password: str, role: str = "usuario", nombre: str = ""):
    if not email or not password:
        raise ValueError("Email y password requeridos")
    if usuarios_col.find_one({"email": email}):
        raise ValueError("Usuario ya existe")
    hashed = hash_password(password)
    user = {
        "email": email,
        "password": Binary(hashed),
        "role": role,
        "nombre": nombre,
        "active": True,
        "created_at": datetime.utcnow()
    }
    usuarios_col.insert_one(user)
    auditorias_col.insert_one({
        "action": "register_user",
        "email": email,
        "timestamp": datetime.utcnow()
    })
    return True

# Inicio de sesión
def login_user(email: str, password: str):
    user = usuarios_col.find_one({"email": email})
    if not user:
        return None
    if not user.get("active", True):
        return None
    hashed = user.get("password")
    if isinstance(hashed, (bytes, bytearray)):
        hashed_bytes = bytes(hashed)
    else:
        hashed_bytes = hashed
    if check_password(password, hashed_bytes):
        auditorias_col.insert_one({
            "action": "login",
            "email": email,
            "timestamp": datetime.utcnow()
        })
        user.pop("password", None)
        return user
    return None
