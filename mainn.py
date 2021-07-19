import sqlite3
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/ConsultarCedula/{cedula}")
def ConsultarCedula(cedula:str):
    conexion = sqlite3.connect('prueba.db')
    cursor = conexion.cursor()
    sql = "INSERT INTO p(Nombre)VALUES('"+cedula+"')"
    cursor.execute(sql)
    conexion.commit()
    return {"ok":True}
