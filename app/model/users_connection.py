import os
import psycopg2
import bcrypt
from fastapi import HTTPException
from typing import List, Optional
from app.schema.users_schema import ResponseUsersSchema, CreateUsersSchema
from app.model.database import get_connection, release_connection


class UsersConnection():
    #connection = None
    def __init__(self, connection):
        pass

    def show_users(self) -> List[ResponseUsersSchema]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT users_id, users_name, users_lastname_one, users_lastname_two, users_email, users_role, users_is_active FROM "users"
                """)
                results = cur.fetchall()

                users = [
                    ResponseUsersSchema(
                        users_id = row[0],
                        users_name = row[1],
                        users_lastname_one = row[2],
                        users_lastname_two = row[3],
                        users_email= row[4], 
                        users_role= row[5],
                        users_is_active = row[6]
                        )for row in results
                ]
                #return users
        except Exception as e:
            print(f"Error para mostrar los posts: {e}")
            return []
        finally:
            release_connection(conn)
    
    def show_userId(self, users_id: int) -> Optional[dict]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT users_id, users_name, users_lastname_one, users_lastname_two, users_email, users_password, users_role, users_is_active
                    FROM "users" WHERE users_id = %s
                """, (users_id,))
                result = cur.fetchone()
                if result:
                    return {
                        "users_id": result[0],
                        "users_name": result[1],
                        "users_lastname_one": result[2],
                        "users_lastname_two": result[3],
                        "users_email": result[4],
                        "users_password": result[5],  
                        "users_role": result[6],
                        "users_is_active": result[7]
                    }
                return None  
        except Exception as e:
            print(f"Error al obtener el usuario por ID: {e}")
            return None
        finally:
            release_connection(conn)

    async def insert_user(self,data:dict):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # Hashear la contraseña antes de guardarla
                hashed_password = bcrypt.hashpw(data['users_password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cur.execute("""
                    INSERT INTO "users" (users_name, users_lastname_one, users_lastname_two, users_email, users_password, users_role, users_is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING users_id
                """, (data['users_name'], data['users_lastname_one'], data['users_lastname_two'],
                      data['users_email'], hashed_password, data['users_role'], data['users_is_active']))
                user_id = cur.fetchone()[0]
                conn.commit()
                return user_id
        except Exception as e:
            print(f"Error al insertar el usuario: {e}")
            conn.rollback()  # Hacer rollback en caso de error
            raise HTTPException(status_code=500, detail="Error al insertar usuario")
        finally:
            release_connection(conn)

    async def update_users(self, users_id:int, data:dict):
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # Si no se proporciona una nueva contraseña, se mantiene la actual
                if data.get('users_password'):
                    hashed_password = bcrypt.hashpw(data['users_password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                else:
                    # Obtener la contraseña actual del usuario para mantenerla
                    cur.execute("SELECT users_password FROM users WHERE users_id = %s", (users_id,))
                    current_password = cur.fetchone()
                    hashed_password = current_password[0] if current_password else None

                cur.execute("""
                    UPDATE "users"
                    SET users_name = %s,
                        users_lastname_one = %s,
                        users_lastname_two = %s,
                        users_email = %s,
                        users_password = %s,
                        users_role = %s,
                        users_is_active = %s
                    WHERE users_id = %s
                """, (data['users_name'], data['users_lastname_one'], data['users_lastname_two'],
                      data['users_email'], hashed_password, data['users_role'], data['users_is_active'], users_id))
                conn.commit()
        except Exception as e:
            print(f"Error al actualizar el usuario: {e}")
            conn.rollback()
            raise HTTPException(status_code=500, detail="Error al actualizar el usuario.")
        finally:
            release_connection(conn) 

    def login_users(self, email:str, password:str) -> ResponseUsersSchema:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT users_id, users_name, users_lastname_one, users_lastname_two, users_email, users_password, users_role, users_is_active 
                    FROM "users"
                    WHERE users_email = %s
                """, (email,))
                results = cur.fetchone()
                
                if results is None:
                    raise HTTPException(status_code=400, detail="Usuario no encontrado")

                users_id, users_name, users_lastname_one, users_lastname_two, users_email, users_password, users_role, users_is_active = results

                if not bcrypt.checkpw(password.encode('utf-8'), users_password.encode('utf-8')):
                    raise HTTPException(status_code=400, detail="Contraseña incorrecta")

                if not users_is_active:
                    raise HTTPException(status_code=403, detail="Usuario inactivo")

                return ResponseUsersSchema(
                    users_id=users_id,
                    users_name=users_name,
                    users_lastname_one=users_lastname_one,
                    users_lastname_two=users_lastname_two,
                    users_email=users_email,
                    users_role=users_role,
                    users_is_active=users_is_active,
                    )
                
        except Exception as e:
            print(f"Error para mostrar los usuarios: {e}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")
        finally:
            release_connection(conn)

