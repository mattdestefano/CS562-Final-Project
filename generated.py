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

columns = ["cust", "prod", "day", "month", "year", "state", "quant", "date"]

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
S = "cust,state,avg_quant,max_quant"
n = "0"
V = "cust,prod"
F = "avg_quant,max_quant,min_quant,count_quant"
sigma = ""
G = ""


# Query Type Detected: sql

for row in salesTable:
    key = '' #key to store into the MF Struct
    value = {} #value that will store the columns of the MF Struct for the given row
    for attr in V.split(','): #create key out of the grouping attributes of the current row in the table
        attr = columns.index(attr)
        key += f'{str(row[attr])},'
    key = key[:-1] #remove trailing comma
    if key not in MF_Struct.keys(): #if the key is not in the MF Struct, create a new entry for the MF Struct
        for groupAttr in V.split(','):
            groupAttr = columns.index(groupAttr)
            colVal = row[groupAttr]
            if colVal:
                value[groupAttr] = colVal
        #loop through the fVects and initalize the values for each aggreagte function being calculated
        #initalize count to 1, sum to the current row's quant value, min and max to the current row's quant value, and average to a dictionary with 3 componenets
        for fVectAttr in F.split(','):
            tableCol = fVectAttr.split('_')[1]
            tableCol = columns.index(tableCol)
            if (fVectAttr.split('_')[0] == 'avg'): 
                #average is stored as a dictionary tracking, sum, count, and average. Each is calculated and stored when the row is updated
                value[fVectAttr] = {'sum': row[tableCol], 'count': 1, 'avg': row[tableCol]}
            elif (fVectAttr.split('_')[0] == 'count'):
                value[fVectAttr] = 1
            else:
                value[fVectAttr] = row[tableCol]
        MF_Struct[key] = value #insert new row into the MFStruct
    else: #row in table already corresponds to an existing entry in the MF Struct, update the existing entry
        for fVectAttr in F.split(','):
            tableCol = fVectAttr.split('_')[1]
            tableCol = columns.index(tableCol)
            if (fVectAttr.split('_')[0] == 'sum'):
                MF_Struct[key][fVectAttr] += int(row[tableCol]) #Add the quant to the sum for the corresponding row in the MF Struct
            elif (fVectAttr.split('_')[0] == 'avg'):
                newSum = MF_Struct[key][fVectAttr]['sum'] + int(row[tableCol])
                newCount = MF_Struct[key][fVectAttr]['count'] + 1
                MF_Struct[key][fVectAttr] = {'sum': newSum, 'count': newCount, 'avg': newSum / newCount}
            elif (fVectAttr.split('_')[0] == 'count'):
                MF_Struct[key][fVectAttr] += 1
            elif (fVectAttr.split('_')[0] == 'min'): #check if the row's quant is a new min compared to the corresponding row of the MFStruct
                if row[tableCol] < MF_Struct[key][fVectAttr]:
                    MF_Struct[key][fVectAttr] = int(row[tableCol])
            else: #check if the row's quant is a new max compared to the corresponding row of the MFStruct
                if row[tableCol] > MF_Struct[key][fVectAttr]:
                    MF_Struct[key][fVectAttr] = int(row[tableCol])
#Generate output table(also checks the HAVING condition)
output = PrettyTable()
output.field_names = S.split(',')
for row in MF_Struct:
    evalString = ''
    if G != '':
        #if there is a having condition, loop through each element of the having condition to fill in the correct information into the evalString
        #the eval string will be equal to the having condition, replaced with the values of the variables in question,
        # then evaluated to check if the row of the MFStruct being examined is to be included in the output table
        for string in G.split(' '):
            if string not in ['>', '<', '==', '<=', '>=', 'and', 'or', 'not', '*', '/', '+', '-']:
                try:
                    int(string)
                    evalString += string
                except:
                    if len(string.split('_')) > 1 and string.split('_')[0] == 'avg':
                        evalString += str(MF_Struct[row][string]['avg'])
                    else:
                        evalString += str(MF_Struct[row][string])
            else:
                evalString += f' {string} '
        if eval(evalString.replace('=', '==')):
            row_info = []
            for val in S.split(','):
                if len(val.split('_')) > 1 and val.split('_')[0] == 'avg':
                    row_info += [str(MF_Struct[row][val]['avg'])]
                else:
                    row_info += [str(MF_Struct[row][val])]
            output.add_row(row_info)
        evalString = ''
    else:
        #there is no having condition, thus every MFStruct row will be in the output table
        row_info = []
        for val in S.split(','):
            if len(val.split('_')) > 1 and val.split('_')[0] == 'avg':
                row_info += [str(MF_Struct[row][val]['avg'])]
            else:
                try:
                    row_info += [str(MF_Struct[row][val])]
                except:
                    val = S.split(',').index(val)
                    row_info += [str(MF_Struct[row][val])]
        output.add_row(row_info)
print(output)