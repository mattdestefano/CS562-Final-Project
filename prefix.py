import psycopg2
from prettytable import PrettyTable

MF_Struct = {}

# Connect to the database
def dbConnect():
    db = psycopg2.connect(
        user = "postgres",
        password = "password",
        host = "127.0.0.1",
        port = "5432",
        database = "sales"
    )
    cursor = db.cursor()
    return cursor, db

def dbInit(db):
    init = open("load_sales_10000_table.sql", "r")
    for line in init:
        db.execute(line)
    init.close()

# Connect to the database
print("Connecting to database...")
cursor, db = dbConnect()
print("Done.\n")

# Initialize the database
print("Initializing database...")
dbInit(cursor)
print("Done.\n")

query = cursor.execute('SELECT * FROM sales;')
salesTable = cursor.fetchall()


# Phi Operators:
