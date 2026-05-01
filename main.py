from fastapi import FastAPI
import requests
import pandas as pd
from fastapi.responses import FileResponse
import os

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok"}

@app.get("/procesar")
def procesar():
    # 1. Obtener datos de API externa
    data = requests.get("https://jsonplaceholder.typicode.com/posts/1").json()

    # 2. Obtener API KEY desde variable de entorno
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {"error": "Falta configurar GEMINI_API_KEY"}

    # 3. Llamada a Gemini (modelo compatible)
    respuesta = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent?key={api_key}",
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"Resume este texto en 2 líneas:\n{data['body']}"
                        }
                    ]
                }
            ]
        }
    ).json()

    # 4. Extraer respuesta de IA
    try:
        analisis = respuesta["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        # Si falla, mostramos respuesta completa para debug
        analisis = f"Error IA: {respuesta}"

    # 5. Crear Excel
    resultado = [{
        "titulo": data["title"],
        "contenido": data["body"],
        "analisis_ia": analisis
    }]

    df = pd.DataFrame(resultado)
    archivo = "resultado.xlsx"
    df.to_excel(archivo, index=False)

    # 6. Devolver archivo (descarga automática)
    return FileResponse(
        archivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="resultado.xlsx"
    )