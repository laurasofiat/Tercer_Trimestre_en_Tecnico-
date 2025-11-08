from flask import Flask, request, jsonify, send_file
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from dotenv import load_dotenv
import os

# Cargar variables desde el archivo .env
load_dotenv()

# Configuración de la aplicación
app = Flask(__name__)

DB_CONFIG = {
    'host':'localhost',
    'database':'diseño',
    'user': 'postgres',
    'password': '123456',
    'port': 5432
}

# Función para conectar la base de datos
def conectar_bd():
    try:
        conexion = psycopg2.connect(**DB_CONFIG)
        return conexion
    except psycopg2.Error as e:
        print(f" Error al conectar a la base de datos: {e}")
        return None

# Crear tabla si no existe
def crear_tabla():
    conexion = conectar_bd()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS USUSARIOS (
            id_usuarios SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            correo VARCHAR(100) NOT NULL,
            telefono VARCHAR(100) NOT FULL,
            direccion VARCHAR(100) NOT FULL,
            mensaje VARCHAR(100),
            creado TIMESTAMP DEFAULT NOW()
        );
        """)
        conexion.commit()
        cursor.close()
        conexion.close()

# Página principal
@app.route('/')
def inicio():
    return send_file('index.html')

# Ruta para guardar contacto
@app.route('/contacto', methods=['POST'])
def guardar_contactos():
    try:
        conexion = conectar_bd()
        if conexion is None:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        datos = request.get_json()
        nombre = datos.get('nombre', '').strip()
        correo = datos.get('correo', '').strip()
        mensaje = datos.get('mensaje', '').strip()

        if not nombre or not correo:
            return jsonify({'error': 'Nombre y correo son obligatorios'}), 400

        cursor = conexion.cursor()
        sql_insertar = """
        INSERT INTO contactos (nombre, correo, mensaje)
        VALUES (%s, %s, %s)
        RETURNING id;
        """
        cursor.execute(sql_insertar, (nombre, correo, mensaje))
        contacto_id = cursor.fetchone()[0]

        conexion.commit()
        cursor.close()
        conexion.close()

        return jsonify({
            'mensaje': 'Contacto guardado exitosamente',
            'id': contacto_id
        }), 201

    except Exception as e:
        print(f" Error al guardar el contacto: {e}")
        return jsonify({'error': 'Error al procesar la solicitud'}), 500

# Ruta para ver todos los contactos
@app.route('/contactos', methods=['GET'])
def ver_contactos():
    try:
        conexion = conectar_bd()
        if conexion is None:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
        
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM contactos ORDER BY creado DESC;")
        contactos = cursor.fetchall()
        cursor.close()
        conexion.close()

        for contacto in contactos:
            if contacto['creado']:
                contacto['creado'] = contacto['creado'].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify(contactos), 200

    except Exception as e:
        print(f" Error al obtener contactos: {e}")
        return jsonify({'error': 'Error al obtener contactos'}), 500

# Inicio del servidor
if __name__ == '__main__':
    print(" Iniciando servidor...")
    crear_tabla()
    app.run(debug=True, host='0.0.0.0', port=5000)