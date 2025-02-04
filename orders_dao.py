from datetime import datetime
from sql_connection import get_sql_connection

def insert_order(connection, order):
    cursor = connection.cursor()

    # Insert into the orders table
    order_query = """
        INSERT INTO orders (customer_name, total, datetime) 
        VALUES (%s, %s, %s) RETURNING order_id
    """
    order_data = (order['customer_name'], order['grand_total'], datetime.now())
    cursor.execute(order_query, order_data)
    order_id = cursor.fetchone()[0]  # Fetch generated order_id

    # Insert into the order_details table
    order_details_query = """
        INSERT INTO order_details (order_id, product_id, quantity, total_price) 
        VALUES (%s, %s, %s, %s)
    """
    order_details_data = [
        (order_id, int(detail['product_id']), float(detail['quantity']), float(detail['total_price']))
        for detail in order['order_details']
    ]
    
    cursor.executemany(order_details_query, order_details_data)
    connection.commit()

    cursor.close()
    return order_id

def get_order_details(connection, order_id):
    cursor = connection.cursor()
    query = """
        SELECT order_details.order_id, order_details.quantity, order_details.total_price,
               products.name, products.price_per_unit 
        FROM order_details 
        LEFT JOIN products ON order_details.product_id = products.product_id 
        WHERE order_details.order_id = %s
    """
    cursor.execute(query, (order_id,))
    records = [
        {
            'order_id': row[0],
            'quantity': row[1],
            'total_price': row[2],
            'product_name': row[3],
            'price_per_unit': row[4]
        }
        for row in cursor.fetchall()
    ]
    
    cursor.close()
    return records

def get_all_orders(connection):
    cursor = connection.cursor()
    query = "SELECT * FROM orders"
    cursor.execute(query)
    response = [
        {
            'order_id': row[0],
            'customer_name': row[1],
            'total': row[2],
            'datetime': row[3],
            'order_details': get_order_details(connection, row[0])  # Append order details
        }
        for row in cursor.fetchall()
    ]

    cursor.close()
    return response
