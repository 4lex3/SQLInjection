# -*- coding: utf-8 -*-
"""
Created on February 2023

@author: Albert ETPX
"""

# Importación de módulos externos
import mysql.connector
from flask import Flask,render_template,request;


# Funciones de backend #############################################################################

# connectBD: conecta a la base de datos users en MySQL
def connectBD():
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        database = "users"
    )
    return db

# initBD: crea una tabla en la BD users, con un registro, si está vacía
def initBD():
    bd=connectBD()
    cursor=bd.cursor()
    
    # cursor.execute("DROP TABLE IF EXISTS users;")
    # Operación de creación de la tabla users (si no existe en BD)
    query="CREATE TABLE IF NOT EXISTS users(\
            user varchar(30) primary key,\
            password varchar(30),\
            name varchar(30), \
            surname1 varchar(30), \
            surname2 varchar(30), \
            age integer, \
            genre enum('H','D','NS/NC')); "
    cursor.execute(query)
            
    # Operación de inicialización de la tabla users (si está vacía)
    query="SELECT count(*) FROM users;"
    cursor.execute(query)
    count = cursor.fetchall()[0][0]
    if(count == 0):
        query = "INSERT INTO users \
            VALUES('user01','admin','Ramón','Sigüenza','López',35,'H');"
        cursor.execute(query)

    bd.commit()
    bd.close()
    return

# checkUser: comprueba si el par usuario-contraseña existe en la BD
def checkUser(user,password):
    bd=connectBD()
    cursor=bd.cursor()

    """
    ?Para evitar las inyecciones de codigo podemos parametrizar los comandos, es decir,
    ?debemos evitar es concatenar directamente en la consulta a realizar, ya que da salida a inyecciones de codigo.
    """

    query = "SELECT user, name, surname1, surname2, age, genre FROM users WHERE user = %s AND password = %s"

    #print(query)
    cursor.execute(query, (user, password))
    userData = cursor.fetchall()
    bd.close()
    
    if userData == []:
        return False
    else:
        return userData[0]

# cresteUser: crea un nuevo usuario en la BD
def createUser(user,password,name,surname1,surname2,age,genre):
 
    query = """
            INSERT INTO users(user, password, name, surname1, surname2, age, genre) 
            VALUES (%s,%s,%s,%s,%s,%s,%s); 
                """

    bd = connectBD()
    cursor = bd.cursor()

    try:
        cursor.execute(query, (user, password, name, surname1, surname2, age, genre))
        bd.commit(); 

        return True;
    except Exception as e:
        bd.rollback();
        return False

    finally:
        bd.close()



# Secuencia principal: configuración de la aplicación web ##########################################
# Instanciación de la aplicación web Flask
app = Flask(__name__)

# Declaración de rutas de la aplicación web
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    initBD()
    return render_template("login.html")



@app.route("/register", methods=('GET', 'POST'))
def register():


    if request.method == 'POST':

        formData = request.form;

        user = formData.get('usuario')  
        password = formData.get('contrasena')
        name = formData.get('name')
        surname1 = formData.get('surname1')
        surname2 = formData.get('surname2')
        age = formData.get('age')
        genre = formData.get('genre')

        print(formData)

        statusUser = createUser(user, password, name, surname1, surname2, age, genre)


        if (not(statusUser == True)):
            return "Usuario no creado"
    
    return render_template("register.html")



@app.route("/results",methods=('GET', 'POST'))
def results():
    if request.method == ('POST'):
        formData = request.form

        user=formData['usuario']
        password=formData['contrasena']

        userData = checkUser(user,password)

        if userData == False:
            return render_template("results.html",login=False)
        else:
            return render_template("results.html",login=True,userData=userData)
        
# Configuración y arranque de la aplicación web
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.run(host='localhost', port=5000, debug=True)