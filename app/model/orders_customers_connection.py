import os
import psycopg2
from fastapi import HTTPException
from typing import List
from app.schema.orders_schema import CreateProvinces
from app.model.database import get_connection, release_connection

class OrdersCustomersConnections():
    def __init__(self):
        pass

    def get_provinces(self) -> List[CreateProvinces]:
        conn = get_connection() 
        try:
            with conn.cursor() as cur:
                cur.execute(""" SELECT provinces_id, provinces_name, provinces_cod FROM "provinces";
                """, )
                results = cur.fetchall()
                
                provinces = [
                    CreateProvinces(
                        provinces_id=row[0],
                        provinces_name=row[1],
                        provinces_cod=row[2],
                    ) for row in results
                ]
                return provinces
        except Exception as e:
            print(f"Error al mostrar las provincias: {e}")
            raise HTTPException(status_code=500, detail=f"Error al mostrar las provincias: {e}")
        finally:
            release_connection(conn)
            
    def get_customers(self, customers_email:str)-> dict:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(""" 
                    SELECT customers_id, customers_email 
                    FROM "customers"
                    WHERE customers_email= %(customers_email)s;
                """, {"customers_email": customers_email} )
                result = cur.fetchone()

                if result:
                    return {"customers_id": result[0], "customers_email": result[1]}
                else:
                    raise HTTPException(status_code=404, detail="Cliente no encontrado.")
                
        except Exception as e:
            print(f"Error al traer el cliente: {e}")
            raise HTTPException(status_code=500, detail=f"Error al traer el cliente: {e}")
        finally:
            release_connection(conn)
            
    def insert_customers(self, data:dict)-> int:
        conn = get_connection()
        try:
            print(f"Datos a insertar: {data}")
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO "customers"(customers_name, customers_surname, customers_address_one, customers_address_two, customers_email, customers_phone, customers_provinces_cod, customers_cp) VALUES (%(customers_name)s, %(customers_surname)s, %(customers_address_one)s, %(customers_address_two)s, %(customers_email)s, %(customers_phone)s , %(customers_provinces_cod)s, %(customers_cp)s) RETURNING customers_id;
                """, data)

                customers_id = cur.fetchone()[0]
                conn.commit()
                print("Cliente guardado exitosamente.")
                return customers_id

        except Exception as e:
            conn.rollback() 
            print(f"Error al insertar el cliente: {e}")
            raise HTTPException(status_code=500, detail="Error al insertar el cliente.")
        finally:
            release_connection(conn)
    
    def insert_orders(self, data:dict)->int:
        conn = get_connection()
        try:
            print(f"Datos a insertar: {data}")
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO "orders"(orders_date, orders_total, orders_customers_id, orders_number)VALUES (%(orders_date)s, %(orders_total)s, %(orders_customers_id)s, %(orders_number)s) RETURNING orders_id;
                """, data)

                orders_id = cur.fetchone()[0]
                conn.commit()
                print("Pedido guardado exitosamente.")
                return orders_id
        except Exception as e:
            conn.rollback()
            print(f"Error al insertar el producto: {e}")
            raise HTTPException(status_code=500, detail="Error al insertar el pedido.")
        finally:
            release_connection(conn)

    def insert_orderproducts(self, data:dict)->None:
        conn = get_connection()
        try:
            print(f"Datos a insertar: {data}")
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO "orderproducts"(orderproducts_name, orderproducts_quantity, orderproducts_price, orderproducts_subtotal, orderproducts_orders_id, orderproducts_products_id) VALUES (%(orderproducts_name)s, %(orderproducts_quantity)s, %(orderproducts_price)s, %(orderproducts_subtotal)s, %(orderproducts_orders_id)s, %(orderproducts_products_id)s);
                    
                """, data)
                conn.commit()
                print("Producto del pedido guardado exitosamente.")
        
        except Exception as e:
            conn.rollback()
            print(f"Error al insertar el producto: {e}")
            raise HTTPException(status_code=500, detail="Error al insertar el producto.")
        finally:
            release_connection(conn)