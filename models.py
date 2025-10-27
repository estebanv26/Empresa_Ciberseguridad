# models.py
from db import usuarios_col, auditorias_col
from datetime import datetime

def crear_incidente(titulo, descripcion, usuario_id):
    """Crea un nuevo incidente en la base de datos."""
    print(f"[DEBUG] Creando incidente: {titulo}, {descripcion}, usuario={usuario_id}")
    return {"status": "ok", "mensaje": "Incidente registrado correctamente"}

def listar_incidentes():
    """Retorna la lista de incidentes."""
    print("[DEBUG] Listando incidentes...")
    return [{"titulo": "Ejemplo de incidente", "estado": "Abierto"}]

def agregar_evidencia(incidente_id, evidencia_path):
    """Agrega evidencia a un incidente."""
    print(f"[DEBUG] Agregando evidencia {evidencia_path} al incidente {incidente_id}")
    return {"status": "ok", "mensaje": "Evidencia agregada"}

def asignar_responsable(incidente_id, responsable):
    """Asigna un responsable a un incidente."""
    print(f"[DEBUG] Asignando responsable {responsable} al incidente {incidente_id}")
    return {"status": "ok", "mensaje": "Responsable asignado"}

def actualizar_estado(incidente_id, nuevo_estado):
    """Actualiza el estado de un incidente."""
    print(f"[DEBUG] Actualizando estado del incidente {incidente_id} a {nuevo_estado}")
    return {"status": "ok", "mensaje": "Estado actualizado"}
