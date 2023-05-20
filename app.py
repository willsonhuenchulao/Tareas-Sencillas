from flask import Flask, render_template, request, session, redirect, url_for
import config
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = config.HEX_SEC_KEY
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASS  # Corrección en la clave de configuración
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)

@app.route('/', methods=['GET']) 
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST']) 
def login():
    email = request.form['email']
    password = request.form['password']

    # Conectar a MySQL
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()
    cur.close()

    if user is not None:
        session['email'] = email
        session['nombre'] = user[1]
        session['apellido'] = user[2]

        return redirect(url_for('tareas'))
    else:
        return render_template('index.html', message="Usuario o contraseña incorrectos")

@app.route('/tareas', methods=['GET'])
def tareas():
    email = session['email']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tarea WHERE email = %s", [email])
    tasks = cur.fetchall()

    insertObject = []
    columNames = [colum[0] for colum in cur.description]
    for record in tasks:
        insertObject.append(dict(zip(columNames, record)))
    cur.close( )   

    return render_template('tareas.html', task = insertObject)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/nueva-tarea', methods=['POST'])
def nueva_tarea():
    title = request.form['title']
    description = request.form['description']
    email = session['email']
    d = datetime.now()
    dateTask = d.strftime("%Y-%m-%d $H:%M:%S")

    if title and description and email:
        cur = mysql.connection.cursor()
        sql = "INSERT INTO tarea (email, title, description, date_task) VALUES (%s,%s,%s,%s)"
        data =(email, title, description,dateTask)
        cur.execute(sql,data)
        mysql.connection.commit()
    return redirect(url_for('tareas'))

@app.route('/nuevo-usuario', methods=['POST'])
def nuevo_usuario():
    name = request.form['nombre']
    surnames = request.form['apellido']
    email = request.form['email']
    password= request.form['password']

    if name and surnames and email and password:
        cur = mysql.connection.cursor()
        sql = "INSERT INTO user (nombre, apellido, email, password) VALUES (%s,%s,%s,%s)"
        data =(name, surnames, email, password)
        cur.execute(sql,data)
        mysql.connection.commit()
    return redirect(url_for('tareas'))

@app.route("/delete-task", methods=["POST"])
def deleteTask():
    cur = mysql.connection.cursor()
    id = request.form['id']
    sql = "DELETE FROM tarea WHERE id = %s"
    data = [id]
    cur.execute(sql, data)
    mysql.connection.commit()
    return redirect(url_for('tareas'))

if __name__ == '__main__':
    app.run(debug=True)
