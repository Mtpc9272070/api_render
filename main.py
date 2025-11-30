# main.py
import json
from fastapi import FastAPI, Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
import os

# Clave de API esperada. La leeremos de una variable de entorno para mayor seguridad.
# En Render, configurarás esta variable en el dashboard.
API_KEY = os.getenv("API_KEY", "default-secret-key-para-desarrollo-local")
API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI(
    title="API de Aranceles",
    description="API para consultar datos de aranceles desde un archivo JSON.",
    version="1.0.0"
)

# --- Carga de datos ---
# Carga el archivo JSON en memoria cuando la aplicación se inicia.
try:
    with open('aranceles_desde_excel.json', 'r', encoding='utf-8') as f:
        aranceles_data = json.load(f)
except FileNotFoundError:
    aranceles_data = []
    print("ADVERTENCIA: El archivo 'aranceles_desde_excel.json' no fue encontrado.")
except json.JSONDecodeError:
    aranceles_data = []
    print("ADVERTENCIA: El archivo 'aranceles_desde_excel.json' tiene un formato inválido.")


# --- Función de Seguridad ---
async def get_api_key(api_key_header: str = Security(api_key_header)):
    """
    Verifica que la clave de API proporcionada en la cabecera es correcta.
    """
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Clave de API no válida o ausente."
        )

# --- Endpoints de la API ---

@app.get("/", summary="Endpoint de Bienvenida")
def read_root():
    """
    Un endpoint simple para verificar que la API está funcionando.
    No requiere autenticación.
    """
    return {"mensaje": "Bienvenido a la API de Aranceles. Usa /docs para ver la documentación."}


@app.get("/aranceles", summary="Obtener todos los aranceles")
def get_all_aranceles(api_key: str = Depends(get_api_key)):
    """
    Devuelve la lista completa de aranceles.
    **Requiere una clave de API en la cabecera `X-API-Key`**.
    """
    return aranceles_data


@app.get("/aranceles/{codigo}", summary="Obtener un arancel por código")
def get_arancel_by_codigo(codigo: str, api_key: str = Depends(get_api_key)):
    """
    Busca y devuelve un arancel específico por su código.
    **Requiere una clave de API en la cabecera `X-API-Key`**.
    """
    for arancel in aranceles_data:
        if arancel.get("codigo") == codigo:
            return arancel
    raise HTTPException(status_code=404, detail=f"Arancel con código '{codigo}' no encontrado.")

