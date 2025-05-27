import pymysql

def connect_to_database():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="shop",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )