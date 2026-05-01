from fastapi import FastAPI
import requests
import pandas as pd
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok"}

@app.get("/procesar")
def procesar():
    data = requests.get("https://jsonplaceholder.typicode.com/posts/1").json()

    resultado = [{
        "titulo": data["title"],
        "contenido": data["body"]
    }]

    df = pd.DataFrame(resultado)
    archivo = "resultado.xlsx"
    df.to_excel(archivo, index=False)

    # 🔥 AQUÍ es donde va el FileResponse corregido
    return FileResponse(
        archivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="resultado.xlsx"
    )