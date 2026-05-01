import os

@app.get("/procesar")
def procesar():
    # 1. Obtener datos
    data = requests.get("https://jsonplaceholder.typicode.com/posts/1").json()

    # 2. Obtener API KEY
    api_key = os.getenv("AIzaSyAfu2VBecRNuVdWcNJSYs9kEAKm2Iriplw")

    # 3. Llamar a Gemini
    respuesta = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}",
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"Resume este texto en 2 líneas: {data['body']}"
                        }
                    ]
                }
            ]
        }
    ).json()

    # 4. Extraer texto de IA (más limpio)
    try:
        analisis = respuesta["candidates"][0]["content"]["parts"][0]["text"]
    except:
        analisis = "Error procesando IA"

    # 5. Crear Excel
    resultado = [{
        "titulo": data["title"],
        "contenido": data["body"],
        "analisis_ia": analisis
    }]

    df = pd.DataFrame(resultado)
    archivo = "resultado.xlsx"
    df.to_excel(archivo, index=False)

    return FileResponse(
        archivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="resultado.xlsx"
    )