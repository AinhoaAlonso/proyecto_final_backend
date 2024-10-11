import psycopg2
import os
from typing import List
from fastapi import HTTPException
from app.schema.posts_schema import PostSchema
from app.model.database import get_connection, release_connection

class PostsConnection():
    def __init__(self):
        pass
    
    def show_posts(self) -> List[PostSchema]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT posts_id, posts_title, posts_content, posts_author, posts_date, posts_users_id, posts_image_url FROM "posts"
                """)
                results = cur.fetchall()

                posts = [
                    PostSchema(posts_id = row[0], posts_title = row[1], posts_content= row[2], posts_author= row [3], posts_date= row [4], posts_users_id =row[5], posts_image_url= row[6])
                    for row in results
                ]
                return posts
        except Exception as e:
            print(f"Error para mostrar los posts: {e}")
            raise HTTPException(status_code=500, detail="Error al mostrar los posts.")
        finally:
            release_connection(conn)
    
    async def insert_posts(self, data:dict)->None:
        conn = get_connection()
        try:
            print(f"Datos a insertar: {data}")
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO "posts" (posts_title, posts_users_id, posts_date, posts_content, posts_author, posts_image_url) VALUES (%(posts_title)s, %(posts_users_id)s, %(posts_date)s, %(posts_content)s, %(posts_author)s, %(posts_image_url)s);
                """, data)

                conn.commit()

                print("Post guardado correctamente.")
        except Exception as e:
            conn.rollback()
            print(f"Error al insertar el producto: {e}")
            raise HTTPException(status_code=500, detail="Error al insertar el post.")
        finally:
            release_connection(conn)
    
    async def update_posts(self, posts_id:int, data:dict)->None:
        conn = get_connection()
        try:
            print(f"Datos a actualizar: {data}")
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE "posts" SET posts_title=%(posts_title)s, posts_users_id=%(posts_users_id)s, posts_date=%(posts_date)s, posts_content=%(posts_content)s, posts_author=%(posts_author)s, posts_image_url=%(posts_image_url)s WHERE posts_id=%(posts_id)s;
                """, {**data, "posts_id": posts_id})

                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Post no encontrado.")
                
                conn.commit()
                print("Post actualizado correctamente.")
        except Exception as e:
            conn.rollback()
            print(f"Error al actualizar el post: {e}")
            raise HTTPException(status_code=500, detail="Error al actualizar el post.")
        finally:
            release_connection(conn)

    async def delete_posts(self, posts_id:int)-> None:
        conn = get_connection() 
        try:
            print(f"Post a eliminar: {posts_id}")
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM "posts" WHERE posts_id=%s;
                """, (posts_id,))

                if cur.rowcount == 0:
                    raise Exception(f"No se encontró el post con posts_id {posts_id}")

                conn.commit()
                print("Post eliminado correctamente.")
        except Exception as e:
            conn.rollback()
            print(f"Error al eliminar el post: {e}")
            raise HTTPException(status_code=500, detail="Error al eliminar el post.")
        finally:
            release_connection(conn)
