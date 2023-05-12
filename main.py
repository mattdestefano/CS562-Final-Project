# CS 562 Final Project
# Author: Matthew DeStefano
# 12 May 2023

import psycopg2
import os

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

def createQuery(S, n, V, F, sigma, G):
    print("Generating query...")
    with open('generated.py', "w") as generated:
        pre = open("prefix.py", "r")
        for line in pre:
            generated.write(line)
        pre.close()
        generated.write(f"""S = "{S}"\nn = "{n}"\nV = "{V}"\nF = "{F}"\nsigma = "{sigma}"\nG = "{G}"\n""")
        queryType = "mf"
        for x in sigma.split(","):
            for y in x.split(" "):
                if y in V.split(","):
                    queryType = "emf"
        if(n == "0"):
            queryType = "sql"
        generated.close()
        generated = open("generated.py", "a")
        generated.write(f"\n\n# Query Type Detected: {queryType}\n\n")
        queryTypeFile = open(f"./Query Types/{queryType}.py", "r")
        for line in queryTypeFile:
            generated.write(line)
        queryTypeFile.close()
        generated.close()
    print(f"Generated query ({queryType}) in {os.getcwd()}\\generated.py\n")
    print("Run script using 'py .\generated.py'.")

def enterInline():
    S = input("Enter the SELECT attribute(s): ")
    n = input("Enter the number of grouping variables: ")
    V = input("Enter the grouping attribute(s): ")
    F = input("Enter the F-Vector: ")
    sigma = input("Enter the sigma condition(s): ")
    G = input("Enter the having condition(s): ")
    createQuery(S, n, V, F, sigma, G)

def enterFile():
    filename = input("Enter the filename, type ls for options, or type exit to exit: ")
    if filename == "exit":
        return
    elif filename == "ls":
        print("Available files: ")
        for file in os.listdir("./Queries"):
            if(file.endswith(".txt")):
                print(file)
        enterFile()
    else:
        try:
            file = open("./Queries/" + filename, "r")
            lines = [x.rstrip() for x in file.readlines()]
            S = ""
            n = ""
            V = ""
            F = ""
            sigma = ""
            G = ""
            x = 0
            while x < len(lines):
                if lines[x] == "SELECT ATTRIBUTE(S):":
                    S = lines[x+1].replace(" ", "") 
                    x += 2
                elif lines[x] == "NUMBER OF GROUPING VARIABLES(n):":
                    n = lines[x+1].replace(" ", "")
                    x += 2
                elif lines[x] == "GROUPING ATTRIBUTES(V):":
                    V = lines[x+1].replace(" ", "")
                    x += 2
                elif lines[x] == "F-VECT([F]):":
                    F = lines[x+1].replace(" ", "")
                    x += 2
                elif lines[x] == "SELECT CONDITION-VECT([sigma]):":
                    sigma = lines[x+1].replace(" ", "").replace('"','\\"')
                    x += 2
                elif lines[x] == "HAVING_CONDITION(G):":
                    G = lines[x+1]
                    x += 2
                else:
                    sigma += f",{lines[x]}".replace('"','\\"')
                    x += 1
            S = S.replace(" ", "")
            n = n.replace(" ", "")
            V = V.replace(" ", "")
            F = F.replace(" ", "")
            createQuery(S, n, V, F, sigma, G)
        except:
            print("Error Reading File. Check that file exists and is formatted correctly.")
            enterFile()

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
        # Inline SQL
        enterInline()
        return
    elif choice == "2":
        # Read from file
        enterFile()
        return
    elif choice == "3":
        # Exit the program
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