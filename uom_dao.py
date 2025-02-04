from sql_connection import get_sql_connection

def get_uoms(connection):
    cursor = connection.cursor()
    query = "SELECT * FROM uom"
    cursor.execute(query)
    response = [
        {'uom_id': row[0], 'uom_name': row[1]}
        for row in cursor.fetchall()
    ]
    
    cursor.close()
    return response
