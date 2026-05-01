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

    # 2. Obtener API KEY desde variables de entorno
    api_key = os.getenv("AIzaSyAUw8GOsWBp_BvDvohbPCAQFnNrMm3gZcs")

    # Validación básica
    if not api_key:
        return {"error": "Falta configurar GEMINI_API_KEY"}

    # 3. Llamada a Gemini (modelo actualizado)
    respuesta = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
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

    # 4. Extraer respuesta de la IA (seguro)
    try:
        analisis = respuesta["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        analisis = f"Error IA: {str(respuesta)}"

    # 5. Crear Excel
    resultado = [{
        "titulo": data["title"],
        "contenido": data["body"],
        "analisis_ia": analisis
    }]

    df = pd.DataFrame(resultado)
    archivo = "resultado.xlsx"
    df.to_excel(archivo, index=False)

    # 6. Forzar descarga correcta
    return FileResponse(
        archivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="resultado.xlsx"
    )