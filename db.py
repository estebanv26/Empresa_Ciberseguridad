import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Ver ruta actual y cargar .env
print("📁 Cargando archivo .env desde:", os.getcwd())
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "sistema_incidentes_db")

print("🔍 MONGO_URI cargado:", MONGO_URI)

if not MONGO_URI:
    print("⚠️  No se cargó la URI de MongoDB. Usando localhost por defecto.")
    MONGO_URI = "mongodb://localhost:27017"

# Conexión
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

usuarios_col = db["usuarios"]
incidentes_col = db["incidentes"]
auditorias_col = db["auditorias"]
evidencias_col = db["evidencias"]
