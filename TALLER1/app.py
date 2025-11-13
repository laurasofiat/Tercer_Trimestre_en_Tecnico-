import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

# CONFIGURACIÓN INICIAL

load_dotenv()

app = Flask(__name__)

#CONEXIÓN A POSTGRESQL

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS')
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        # Retorna None si la conexión falla
        return None

#define la ruta
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':

        id_usuarios=request.form['id_usuarios']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        correo = request.form['correo_electronico']
        mensaje = request.form['mensaje']

        conn = None
        try:
            #Conectarse a la base de datos
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
            
                cur.execute(
                    'INSERT INTO formulario (id_usuarios,nombre, apellido, direccion, telefono, correo_electronico, mensaje) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (id_usuarios, nombre, apellido, direccion, telefono, correo, mensaje)
                )
                conn.commit()  
                cur.close()
                
                flash('¡Datos registrados exitosamente en PostgreSQL!', 'success')
            else:
                flash('Error: No se pudo establecer la conexión a la base de datos.', 'danger')
        
        except psycopg2.Error as e:
            # Muestra un error sí algo falla
            flash(f'Error al insertar datos: {e}', 'danger')
        
        finally:
            # Asegura que la conexión se cierre, haya habido un error o no
            if conn:
                conn.close()

        # Redirigir a la misma ruta 
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)