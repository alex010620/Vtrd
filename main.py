import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from DatosVacunacionFirst import DatosVacunacionFirst
from Dosis import Dosis

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {'Sistema': 'ApiVacunaRD'}

@app.get("/api/ConsultarCedula/{cedula}")
def ConsultarCedula(cedula:str):
    Cedul=""
    conexion = sqlite3.connect('prueba.db', check_same_thread=False)
    cursor = conexion.cursor()
    cursor.execute("SELECT Cedula FROM Usuarios WHERE Cedula = '"+cedula+"'")
    contenido = cursor.fetchall()
    for i in contenido:
        Cedul = i[0]
    if cedula == Cedul:
        return True
    else:
        return False

@app.post("/api/RegistrarVacunadosFirst")
def RegistrarVacunadosFirst(d:DatosVacunacionFirst):
    conexion = sqlite3.connect('prueba.db',check_same_thread=False) 
    cursor = conexion.cursor()
    TablaUser = (d.Cedula,d.Nombre,d.Apellido,d.Telefono,d.Fecha_Nacimiento,d.Zodiaco)
    TablaVacuna = (d.Cedula,d.NombreVacuna,d.Provincia,d.Fecha_Vacunacion)
    sql = '''INSERT INTO Usuarios(Cedula,Nombre,Apellido,Telefono,Fecha_Nacimiento,Zodiaco)VALUES(?,?,?,?,?,?)'''
    sql2 = '''INSERT INTO Vacunas(CedulaVacunado,NombreVacuna,Provincia,Fecha_Vacunacion)VALUES(?,?,?,?)'''
    cursor.execute(sql, TablaUser)
    cursor.execute(sql2, TablaVacuna)
    conexion.commit()
    return {"ok":True}

@app.post("/api/NuevaDosis")
def OtrasDosis(d:Dosis):
    try:
        conexion = sqlite3.connect('prueba.db',check_same_thread=False)
        cursor = conexion.cursor()
        TablaVacuna = (d.Cedula,d.NombreVacuna,d.Provincia,d.Fecha_Vacunacion)
        sql2 = '''INSERT INTO Vacunas(CedulaVacunado,NombreVacuna,Provincia,Fecha_Vacunacion)VALUES(?,?,?,?)'''
        cursor.execute(sql2, TablaVacuna)
        return {"ok":True} 
    except:
        return{"ok":False}

@app.get("/api/ConsultaDeVacunados")
def ConsultaDeVacunados():
    Datos = []
    conexion = sqlite3.connect('prueba.db')
    cursor = conexion.cursor()
    cursor.execute('SELECT U.*, Count(V.IdVacuna) As Cantidaddevacunas FROM Usuarios AS U INNER JOIN Vacunas AS V ON U.Cedula = V.CedulaVacunado')
    contenido = cursor.fetchall()
    conexion.commit()
    for i in contenido:
        Datos.append({"IdUsuario":i[0],"Cedula":i[1],"Nombre": i[2], "Apellido": i[3], "Telefono": i[4],"Fecha_Nacimiento":i[5],"Zodiaco":i[6],"Cantidad":i[7]})
    return Datos

@app.get("/api/ConsultaDeVacunadoUnico/{NombreOApellido}")
def ConsultaDeVacunadoUnico(NombreOApellido:str):
    Datos = []
    idf = 0
    Cedula=""
    Nombre=""
    Apellido=""
    Telefono=""
    Fecha_Nacimiento=""
    Zodiaco=""
    Cantidad=""
    conexion = sqlite3.connect('prueba.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT U.*, Count(V.IdVacuna) As Cantidaddevacunas FROM Usuarios AS U INNER JOIN Vacunas AS V ON U.Cedula = V.CedulaVacunado WHERE U.Nombre = '"+NombreOApellido+"' or U.Apellido= '"+NombreOApellido+"' GROUP BY U.idUsuario,U.Cedula, U.Nombre, U.Apellido,U.Telefono,U.Fecha_Nacimiento,U.Zodiaco")
    contenido = cursor.fetchall()
    conexion.commit()
    for i in contenido:
        idf = i[0]
        Cedula=i[1]
        Nombre= i[2]
        Apellido= i[3]
        Telefono= i[4]
        Fecha_Nacimiento=i[5]
        Zodiaco=i[6]
        Cantidad=i[7]
    cursor.execute("select NombreVacuna, Provincia,Fecha_Vacunacion from Vacunas WHERE CedulaVacunado = '"+Cedula+"'")
    contenido2 = cursor.fetchall()
    for i in contenido2:
        Datos.append({"NombreVacuna":i[0], "Provincia":i[1], "FechaVacunacion":i[2]})

    return {"idUsuario":idf,"Cedula":Cedula,"Nombre": Nombre, "Apellido": Apellido, "Telefono": Telefono,"Fecha_Nacimiento":Fecha_Nacimiento
                    ,"Zodiaco":Zodiaco,"Cantidad":Cantidad, "DatosVAcunas": Datos}

@app.get("/api/VacunadosPorProvincia/{provincia}")
def VacunadosPorProvincia(provincia:str):
    Datos = []
    conexion = sqlite3.connect('prueba.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT U.Cedula,U.Nombre, U.Apellido,U.Telefono,V.NombreVacuna,V.Provincia,V.Fecha_Vacunacion,U.IdUsuario FROM Usuarios AS U INNER JOIN Vacunas AS V ON U.Cedula = V.CedulaVacunado WHERE V.Provincia = '"+provincia+"' GROUP BY U.Cedula, U.Nombre,U.Apellido,U.Telefono,V.NombreVacuna,V.Provincia,V.Fecha_Vacunacion,U.IdUsuario")
    contenido = cursor.fetchall()
    conexion.commit()
    for i in contenido:
        Datos.append({"ok":True,"Cedula":i[0],"Nombre": i[1], "Apellido": i[2], "Telefono": i[3],"NombreVacuna":i[4],
                    "Provincia":i[5],"Fecha_Vacunacion":i[6], "IdUsuario":i[7]})
    if Datos == []:
        return {"ok":False}
    else:
        return Datos

@app.get("/api/VacunadosPorMarcaDeVacuna")
def VacunadosPorMarcaDeVacuna():
    Datos = []
    conexion = sqlite3.connect('prueba.db')
    cursor = conexion.cursor()
    cursor.execute('SELECT NombreVacuna, count(IdVacuna) as Cantidad from Vacunas WHERE NombreVacuna = NombreVacuna')
    contenido = cursor.fetchall()
    conexion.commit()
    for i in contenido:
        Datos.append({"ok":True,"NombreVacuna":i[0],"Cantidad":i[1]})
    if Datos == []:
        return {"ok":False}
    else:
        return Datos


@app.get("/api/VacunadosPorZodiaco")
def VacunadosPorZodiaco():
    Datos = []
    conexion = sqlite3.connect('prueba.db')
    cursor = conexion.cursor()
    cursor.execute('Select Zodiaco, Count(IdUsuario) as Cantidad from Usuarios where Zodiaco = Zodiaco GROUP BY Zodiaco')
    contenido = cursor.fetchall()
    conexion.commit()
    for i in contenido:
        Datos.append({"ok":True,"Zodiaco":i[0],"Cantidad":i[1]})
    if Datos == []:
        return {"ok":False}
    else:
        return Datos



@app.delete("/api/EliminarRegistroVacunado/{IdUser}")
def EliminarRegistroVacunado(IdUser:str):
    try:
        Cedula = ""
        conexion = sqlite3.connect('prueba.db')
        cursor = conexion.cursor()
        cursor.execute("Select CedulaVacunado from Vacunas where IdVacuna = '"+IdUser+"'")
        contenido = cursor.fetchall()
        conexion.commit()
        for i in contenido:
            Cedula = i[0]
        cursor.execute("Delete from Usuarios where IdUsuario = '"+IdUser+"'")
        cursor.execute("Delete from Vacunas where CedulaVacunado = '"+Cedula+"'")
        return {"ok":True}
    except TypeError as e:
        return e

#CRUD PROVINCIAS

#Select All
@app.get("/api/Provincias")
def Provincias():
    try:
        Datos =[]
        conexion = sqlite3.connect('prueba.db')
        cursor = conexion.cursor()
        cursor.execute("SELECT IdProvincia, NombreProvincia FROM Provincias")
        contenido = cursor.fetchall()
        for i in contenido:
            Datos.append({"ok":True,"IdProvincia":i[0],"NombredeProvincia":i[1]})
        if Datos == []:
            return {"ok":False}
        else:
            return Datos
    except TypeError:
        return{"ok":False}
#Create
@app.post("/api/NuevaProvincia/{Nombre}")
def NuevaProvincia(Nombre:str):
    try:
        N = ""
        conexion = sqlite3.connect('prueba.db')
        cursor = conexion.cursor()
        cursor.execute("SELECT NombreProvincia FROM Provincias WHERE NombreProvincia = '"+Nombre+"'")
        contenido = cursor.fetchall()
        for i in contenido:
            N = i[0]
        if Nombre == N:
            return {"ok":False}
        else:
            sql = "INSERT INTO Provincias(NombreProvincia)VALUES('"+Nombre+"')"
            cursor.execute(sql)
            conexion.commit()
            return {"ok":True}
    except TypeError:
        return{"ok":False}
#UPDATE
@app.put("/api/ActualizarProvincia/{IdProvincia}/{NuevoNombre}")
def ActualizarProvincia(IdProvincia:str,NuevoNombre:str):
    try:
        conexion = sqlite3.connect('prueba.db')
        cursor = conexion.cursor()
        cursor.execute("Update Provincias set NombreProvincia = '"+NuevoNombre+"' where IdProvincia = '"+IdProvincia+"'")
        conexion.commit()
        return {"ok":True}
    except:
        return {"ok":False}
#Delete
@app.delete("/api/EliminarProvincia/{IdProvincia}")
def EliminarProvincia(IdProvincia:str):
    try:
        conexion = sqlite3.connect('prueba.db')
        cursor = conexion.cursor()
        cursor.execute("Delete from Provincias where IdProvincia = '"+IdProvincia+"'")
        conexion.commit()
        return {"ok":True}
    except:
        return {"ok":False}

#CRUD VacunasExistente

#Select All
@app.get("/api/VacunasExistente")
def VacunasExistente():
    try:
        Datos =[]
        conexion = sqlite3.connect('prueba.db')
        cursor = conexion.cursor()
        cursor.execute("SELECT IdVacuna, NombreVacuna FROM VacunasDisponibles")
        contenido = cursor.fetchall()
        for i in contenido:
            Datos.append({"ok":True,"IdVacuna":i[0],"NombreVacuna":i[1]})
        if Datos == []:
            return {"ok":False}
        else:
            return Datos
    except TypeError:
        return{"ok":False}
#Create
@app.post("/api/NuevoNombreVacunas/{Nombre}")
def NuevoNombreVacuna(Nombre:str):
    try:
        N = ""
        conexion = sqlite3.connect('prueba.db')
        cursor = conexion.cursor()
        cursor.execute("SELECT NombreVacuna FROM VacunasDisponibles WHERE NombreVacuna = '"+Nombre+"'")
        contenido = cursor.fetchall()
        for i in contenido:
            N = i[0]
        if Nombre == N:
            return {"ok":False}
        else:
            sql = "INSERT INTO VacunasDisponibles(NombreVacuna)VALUES('"+Nombre+"')"
            cursor.execute(sql)
            return {"ok":True}
    except TypeError:
        return{"ok":False}
#UPDATE
@app.put("/api/ActualizarVacuna/{IdVacuna}/{NuevoNombre}")
def ActualizarVacuna(IdVacuna:str,NuevoNombre:str):
    try:
        conexion = sqlite3.connect('prueba.db')
        cursor = conexion.cursor()
        cursor.execute("Update VacunasDisponibles set NombreVacuna = '"+NuevoNombre+"' where IdVacuna = '"+IdVacuna+"'")
        conexion.commit()
        return {"ok":True}
    except:
        return {"ok":True}

@app.get("/api/ConsultarC/{cedula}")
def ConsultarC(cedula:str):
    conexion = sqlite3.connect('prueba.db')
    cursor = conexion.cursor()
    sql = "INSERT INTO p(Nombre)VALUES('"+cedula+"')"
    cursor.execute(sql)
    conexion.commit()
    return {"ok":True}
#Delete
@app.delete("/api/EliminarVacuna/{IdVacuna}")
def EliminarVacuna(IdVacuna:str):
    try:
        conexion = sqlite3.connect('prueba.db')
        cursor = conexion.cursor()
        cursor.execute("Delete from VacunasDisponibles where IdVacuna = '"+IdVacuna+"'")
        conexion.commit()
        return {"ok":True}
    except:
        return {"ok":True}

