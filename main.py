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
    modelo = "mistral-small-latest"
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": modelo,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.7
    }

    max_reintentos = 5
    for intento in range(max_reintentos):
        respuesta = requests.post(url, headers=headers, json=payload)
        if respuesta.status_code == 200:
            return respuesta.json()
        elif respuesta.status_code == 429:
            tiempo_espera = min(2 ** intento, 30)
            print(f"Límite alcanzado. Reintentando en {tiempo_espera}s...")
            time.sleep(tiempo_espera)
        else:
            return {"error": f"Error {respuesta.status_code}: {respuesta.text}"}
    return respuesta.json()

@app.get("/procesar")
def procesar():
    # 1. Obtener noticias reales de NewsData.io
    news_api_key = os.getenv("NEWSDATA_API_KEY")
    if not news_api_key:
        return {"error": "Falta configurar NEWSDATA_API_KEY"}

    # Puedes cambiar "q" por cualquier tema: deportes, politica, economia...
    url = f"https://newsdata.io/api/1/news?apikey={news_api_key}&language=es&category=technology&size=5"
    
    try:
        data = requests.get(url).json()
        if data.get("status") != "success":
            return {"error": f"Error en NewsData: {data}"}
        noticia = data["results"][0]
    except Exception as e:
        return {"error": f"No se pudieron obtener las noticias: {e}"}

    # 2. Obtener API KEY de Mistral
    mistral_key = os.getenv("MISTRAL_API_KEY")
    if not mistral_key:
        return {"error": "Falta configurar MISTRAL_API_KEY"}

    # 3. Prompt para la IA
    prompt = f"Resume esta noticia en 2 líneas:\nTítulo: {noticia['title']}\n\n{noticia.get('content', '')}"
    respuesta = llamar_mistral(mistral_key, prompt)

    # 4. Extraer resumen
    try:
        analisis = respuesta["choices"][0]["message"]["content"].strip()
    except Exception:
        analisis = f"Error IA: {respuesta}"

    # 5. Crear Excel
    resultado = [{
        "titulo": noticia["title"],
        "fuente": noticia.get("source_id", "Desconocida"),
        "fecha": noticia.get("pubDate", "Sin fecha"),
        "contenido": noticia.get("content", ""),
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
            filename="resumen_noticia.xlsx"
        )
    else:
        return {"error": "No se pudo generar el archivo Excel."}