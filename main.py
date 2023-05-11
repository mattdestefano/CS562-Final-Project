# CS 562 Final Project
# Author: Matthew DeStefano
# 12 May 2023

import psycopg2

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

# Initialize the database
def dbInit(db):
    init = open("load_sales_10000_table.sql", "r")
    for line in init:
        db.execute(line)
    init.close()

def displayMenu():
    print("Welcome to the CS 562 Final Project!")
    print("Please select an option from the following menu:")
    print("1. Inline SQL")
    print("2. Read from file")
    print("3. Quit")
    pass

# Prompt the user for input
def promptUser():
    choice = input("Enter your choice: ")
    if choice == "1":
        pass
        #inlineSQL()
    elif choice == "2":
        pass
        #readFile(operand)
    elif choice == "3":
        return
    else:
        print("Invalid input. Please try again.")
        promptUser()

if __name__ == "__main__":
    # Connect to the database
    print("Connecting to database...")
    cursor, db = dbConnect()
    print("Done.\n")

    # Initialize the database
    print("Initializing database...")
    dbInit(cursor)
    print("Done.\n")

    # Prompt the user for input
    displayMenu()
    promptUser()
    
    # Close the database
    print("Closing database...")
    cursor.execute("drop table sales;")
    cursor.close()
    db.close()
    print("Done.\n")