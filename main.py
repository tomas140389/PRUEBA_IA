from fastapi import FastAPI
import requests
import pandas as pd
from fastapi.responses import FileResponse
import os
import time

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok"}

def llamar_mistral(api_key, prompt):
    """
    Llama a la API de Mistral (modelo gratuito) con reintentos básicos.
    """
    modelo = "mistral-small-latest"  # Modelo disponible en el plan gratuito
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": modelo,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,  # Limita la respuesta para ahorrar tokens
        "temperature": 0.7
    }

    max_reintentos = 5
    for intento in range(max_reintentos):
        respuesta = requests.post(url, headers=headers, json=payload)

        if respuesta.status_code == 200:
            return respuesta.json()

        # Manejo de rate limiting (HTTP 429)
        elif respuesta.status_code == 429:
            tiempo_espera = min(2 ** intento, 30)  # Espera exponencial máx. 30s
            print(f"Límite alcanzado. Reintentando en {tiempo_espera}s...")
            time.sleep(tiempo_espera)
        else:
            # Otro error (p. ej., clave incorrecta, modelo no disponible)
            return {"error": f"Error {respuesta.status_code}: {respuesta.text}"}

    # Si agota reintentos, devuelve el error de la última solicitud
    return respuesta.json()

@app.get("/procesar")
def procesar():
    # 1. Obtener datos de API externa
    try:
        data = requests.get("https://jsonplaceholder.typicode.com/posts/1").json()
    except Exception as e:
        return {"error": f"No se pudieron obtener los datos externos: {e}"}

    # 2. Obtener API KEY desde variable de entorno
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        return {"error": "Falta configurar MISTRAL_API_KEY"}

    # 3. Llamada a Mistral con el prompt
    prompt = f"Resume este texto en 2 líneas:\n{data['body']}"
    respuesta = llamar_mistral(api_key, prompt)

    # 4. Extraer la respuesta
    try:
        analisis = respuesta["choices"][0]["message"]["content"].strip()
    except Exception:
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

    # 6. Devolver archivo
    if os.path.exists(archivo):
        return FileResponse(
            archivo,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="resultado.xlsx"
        )
    else:
        return {"error": "No se pudo generar el archivo Excel."}