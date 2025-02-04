from sql_connection import get_sql_connection

def get_all_products(connection):
    cursor = connection.cursor()
    query = """
        SELECT products.product_id, products.name, products.uom_id, products.price_per_unit, uom.uom_name
        FROM products 
        INNER JOIN uom ON products.uom_id = uom.uom_id
    """
    cursor.execute(query)
    response = [
        {
            'product_id': row[0],
            'name': row[1],
            'uom_id': row[2],
            'price_per_unit': row[3],
            'uom_name': row[4]
        }
        for row in cursor.fetchall()
    ]
    
    cursor.close()
    return response

def insert_new_product(connection, product):
    cursor = connection.cursor()
    query = """
        INSERT INTO products (name, uom_id, price_per_unit) 
        VALUES (%s, %s, %s) RETURNING product_id
    """
    data = (product['product_name'], product['uom_id'], product['price_per_unit'])
    
    cursor.execute(query, data)
    product_id = cursor.fetchone()[0]
    connection.commit()

    cursor.close()
    return product_id

def delete_product(connection, product_id):
    cursor = connection.cursor()
    query = "DELETE FROM products WHERE product_id = %s"
    cursor.execute(query, (product_id,))
    connection.commit()

    cursor.close()
    return product_id
