import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Configurar el pool de conexiones
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        dsn=DATABASE_URL
    )
    if connection_pool:
        print("Pool de conexiones creado exitosamente")
except (Exception, psycopg2.DatabaseError) as error:
    print(f"Error creando el pool de conexiones: {error}")
    raise

def get_connection():
    try:
        return connection_pool.getconn()
    except Exception as e:
        print(f"Error obteniendo conexión del pool: {e}")
        raise

def release_connection(conn):
    try:
        connection_pool.putconn(conn)
    except Exception as e:
        print(f"Error liberando conexión al pool: {e}")
        raise

def close_all_connections():
    try:
        connection_pool.closeall()
        print("Todas las conexiones del pool han sido cerradas")
    except Exception as e:
        print(f"Error cerrando todas las conexiones: {e}")
        raise
