import os
from fastapi import UploadFile, File, HTTPException
import psycopg2
from psycopg2 import sql
from typing import List
from app.schema.products_schema import ProductsSchema
from app.model.database import get_connection, release_connection


class ProductsConnection():

    def __init__(self):
        pass
    
    def get_products(self) -> List[ProductsSchema]:
        conn_products = get_connection()
        try:
            with conn_products.cursor() as cur:
                cur.execute("""
                    SELECT products_id, products_name, products_description, products_price,products_image_url, products_stock, products_category, products_is_active FROM "products"
                """)
                results = cur.fetchall()
                
                products=[
                    ProductsSchema(
                    products_id= row[0], 
                    products_name=row[1], 
                    products_description= row[2], 
                    products_price=row[3],
                    products_image_url= row[4],
                    products_stock=row[5], 
                    products_category=row[6],
                    products_is_active=row[7]
                    )for row in results
                ] 
                return products
            
        except Exception as e:
            print(f"Error al mostrar los productos: {e}")
            raise HTTPException(status_code=500, detail=f"Error al mostrar los productos: {e}")
        finally:
            release_connection(conn_products)
    
    def get_product_id(self, products_id: int) -> ProductsSchema:
        conn_products = get_connection()
        
        try:
            with conn_products.cursor() as cur:
                cur.execute("""
                    SELECT products_id, products_name, products_description, 
                           products_price, products_image_url, products_stock, 
                           products_category, products_is_active
                    FROM "products"
                    WHERE products_id = %s
                """, (products_id,))
                result = cur.fetchone() 

                if result:  
                    return ProductsSchema(
                        products_id=result[0], 
                        products_name=result[1], 
                        products_description=result[2], 
                        products_price=result[3],
                        products_image_url=result[4],
                        products_stock=result[5], 
                        products_category=result[6],
                        products_is_active=result[7]
                    )
                else:
                    raise HTTPException(status_code=404, detail="Producto no encontrado.") 
            
        except Exception as e:
            print(f"Error para mostrar el producto: {e}")
            raise HTTPException(status_code=500, detail="Error interno al obtener el producto.")
        finally:
            release_connection(conn_products)
    
    async def insert_products(self, data:dict)-> None:
        conn_products = get_connection()
        try: 
            with conn_products.cursor() as cur:
                cur.execute(sql.SQL("""
                    INSERT INTO "products"(products_name, products_description, products_price, products_image_url, products_stock, products_category, products_is_active) VALUES (%(products_name)s, %(products_description)s, %(products_price)s, %(products_image_url)s, %(products_stock)s, %(products_category)s, %(products_is_active)s);
                """), data)
                
                conn_products.commit()
                print("Producto guardado correctamente.")
        except Exception as e:
            conn_products.rollback()
            print(f"Error al insertar el producto: {e}")
            raise HTTPException(status_code=500, detail="Error al insertar el producto.")
        finally:
            release_connection(conn_products)

    async def update_products(self, products_id:int, data:dict)->None:
        conn_products = get_connection()
        try:
            with conn_products.cursor() as cur:
                cur.execute(sql.SQL("""
                    UPDATE "products" SET products_name=%(products_name)s, products_description=%(products_description)s, products_price=%(products_price)s, products_image_url=%(products_image_url)s, products_stock=%(products_stock)s, products_category=%(products_category)s, products_is_active=%(products_is_active)s WHERE products_id = %(products_id)s;
                """), {**data, "products_id": products_id})

                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Producto no encontrado.")

                conn_products.commit()
                print("Producto actualizado correctamente.")
        except Exception as e:
            conn_products.rollback()
            print(f"Error al actualizar el producto: {e}")
            raise HTTPException(status_code=500, detail="Error al actualizar el producto.")
        finally:
            release_connection(conn_products)
    
    async def update_products_stock(self, products_id:int, products_stock:int) -> None:
        conn_products = get_connection()
        try:
            with conn_products.cursor() as cur:
                cur.execute(sql.SQL("""
                    UPDATE "products" SET products_stock=%(products_stock)s WHERE products_id = %(products_id)s;
                """), {"products_stock": products_stock, "products_id": products_id})

                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Producto no encontrado.")

                conn_products.commit()
                print("Stock actualizado correctamente.")
        except Exception as e:
            conn_products.rollback()
            print(f"Error al actualizar el stock: {e}")
            raise HTTPException(status_code=500, detail="Error al actualizar el stock.")
        finally:
            release_connection(conn_products)
        
    async def delete_products(self, products_id:int)-> None:
        conn_products = get_connection()
        try:
            with conn_products.cursor() as cur:
                cur.execute(sql.SQL("""
                    UPDATE products SET products_is_active = FALSE WHERE products_id = %s;
                """), (products_id,))

                if cur.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Producto no encontrado.")

                conn_products.commit()
                print("Producto marcado inactivo correctamente.")
        except Exception as e:
            conn_products.rollback() 
            print(f"Error al marcar inactivo el producto: {e}")
            raise HTTPException(status_code=500, detail="Error al marcar inactivo el producto.")
        finally:
            release_connection(conn_products)
