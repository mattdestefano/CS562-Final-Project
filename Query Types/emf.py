sigma = sigma.split(',') #splits predicates by each predicate statment and creates list to store the parts of each predicate in a single 2D array
pList = []
for i in sigma:
	pList.append(i.split(' '))
for i in range(int(n)+1):
    # 0th pass of the algorithm, where each row of the MF Struct is initalized for every unique group based on the grouping variables.
    # Each row in the MF struct also has its columns initalized appropriately based on the aggregates in the F-Vect
	if i == 0:
		for row in query:
			key = ''
			value = {}
			for attr in V.split(','):
				key += f'{str(row[attr])},'
			key = key[:-1]
			if key not in MF_Struct.keys():
				for groupAttr in V.split(','):
					colVal = row[groupAttr]
					if colVal:
						value[groupAttr] = colVal
				for fVectAttr in F.split(','):
                    # Average is saved as an object with the sum, count, and overall average
					if (fVectAttr.split('_')[1] == 'avg'):
						value[fVectAttr] = {'sum':0, 'count':0, 'avg':0}
                    # Min is initialized as 4994, which is the largest value of 'quant' in the sales table. This allows the first value that the algorithm comes across will be saved as the min (except the row with quant=4994)
					elif (fVectAttr.split('_')[1] == 'min'):
						value[fVectAttr] = 4994
					else:
						value[fVectAttr] = 0
				MF_Struct[key] = value
	else:
        # Begin n passes for each of the n grouping variables
		for aggregate in F.split(','):
			aggList = aggregate.split('_')
			groupVar = aggList[0]
			aggFunc = aggList[1]
			aggCol = aggList[2]
            # Check to make sure the aggregate function is being called on the grouping variable you are currently on (i)
            # Also loop through every key in the MF_Struct to update every row of the MF_Struct the predicate statments apply to(1.state = state and 1.cust = cust vs 1.state = state)
			if i == int(groupVar):
				for row in query:
					for key in MF_Struct.keys():
						if aggFunc == 'sum':
							evalString = sigma[i-1]
                            # Creates a string to be run with the eval() method by replacing grouping variables with their actual values
                            # Since it's an EMF query, it must also check if the string is a grouping variable and replace that with the actual value from the table row as well
							for string in pList[i-1]:
								if len(string.split('.')) > 1 and string.split('.')[0] == str(i):
									rowVal = row[string.split('.')[1]]
									try:
										int(rowVal)
										evalString = evalString.replace(string, str(rowVal))
									except:
										evalString = evalString.replace(string, f"'{rowVal}'")
								elif string in V.split(','):
									rowVal = MF_Struct[key][string]
									try:
										int(rowVal)
										evalString = evalString.replace(string, str(rowVal))
									except:
										evalString = evalString.replace(string, f"'{rowVal}'")
                            # If evalString is true, update the sum
							if eval(evalString.replace('=', '==')):
								sum = int(row[aggCol])
								MF_Struct[key][aggregate] += sum
						elif aggFunc == 'avg':
							sum = MF_Struct[key][aggregate]['sum']
							count = MF_Struct[key][aggregate]['count']
							evalString = sigma[i-1]
							for string in pList[i-1]:
								if len(string.split('.')) > 1 and string.split('.')[0] == str(i):
									rowVal = row[string.split('.')[1]]
									try:
										int(rowVal)
										evalString = evalString.replace(string, str(rowVal))
									except:
										evalString = evalString.replace(string, f"'{rowVal}'")
								elif string in V.split(','):
									rowVal = MF_Struct[key][string]
									try:
										int(rowVal)
										evalString = evalString.replace(string, str(rowVal))
									except:
										evalString = evalString.replace(string, f"'{rowVal}'")
                            # If evalString is true and count isn't 0, update the avg
							if eval(evalString.replace('=', '==')):
								sum += int(row[aggCol])
								count += 1
								if count != 0:
									MF_Struct[key][aggregate] = {'sum': sum, 'count': count, 'avg': (sum/count)}
						elif aggFunc == 'min':
							evalString = sigma[i-1]
							for string in pList[i-1]:
								if len(string.split('.')) > 1 and string.split('.')[0] == str(i):
									rowVal = row[string.split('.')[1]]
									try:
										int(rowVal)
										evalString = evalString.replace(string, str(rowVal))
									except:
										evalString = evalString.replace(string, f"'{rowVal}'")
								elif string in V.split(','):
									rowVal = MF_Struct[key][string]
									try:
										int(rowVal)
										evalString = evalString.replace(string, str(rowVal))
									except:
										evalString = evalString.replace(string, f"'{rowVal}'")
                            # If evalString is true, update the min
							if eval(evalString.replace('=', '==')):
								min = int(MF_Struct[key][aggregate])
								if int(row[aggCol]) < min:
									MF_Struct[key][aggregate] = row[aggCol]
						elif aggFunc == 'max':
							evalString = sigma[i-1]
							for string in pList[i-1]:
								if len(string.split('.')) > 1 and string.split('.')[0] == str(i):
									rowVal = row[string.split('.')[1]]
									try:
										int(rowVal)
										valString = evalString.replace(string, str(rowVal))
									except:
										evalString = evalString.replace(string, f"'{rowVal}'")
								elif string in V.split(','):
									rowVal = MF_Struct[key][string]
									try:
										int(rowVal)
										valString = evalString.replace(string, str(rowVal))
									except:
										evalString = evalString.replace(string, f"'{rowVal}'")
                            # If evalString is true, update the max
							if eval(evalString.replace('=', '==')):
								max = int(MF_Struct[key][aggregate])
								if int(row[aggCol]) > max:
									MF_Struct[key][aggregate] = row[aggCol]
						elif aggFunc == 'count':
							evalString = sigma[i-1]
							for string in pList[i-1]:
								if len(string.split('.')) > 1 and string.split('.')[0] == str(i):
									rowVal = row[string.split('.')[1]]
									try:
										int(rowVal)
										evalString = evalString.replace(string, str(rowVal))
									except:
										evalString = evalString.replace(string, f"'{rowVal}'")
								elif string in V.split(','):
									rowVal = MF_Struct[key][string]
									try:
										int(rowVal)
										evalString = evalString.replace(string, str(rowVal))
									except:
										evalString = evalString.replace(string, f"'{rowVal}'")
                            # If evalString is true, increment the count
							if eval(evalString.replace('=', '==')):
								MF_Struct[key][aggregate] += 1
#Generate output table(also checks the HAVING condition)
output = PrettyTable()
output.field_names = S.split(',')
for row in MF_Struct:
    #create an evalString to be used to check each having condition
	evalString = ''
	if G != '':
		for string in G.split(' '):
            #if there is a having condition, loop through each element of the having condition to fill in the correct information into the evalString
            #the eval string will be equal to the having condition, replaced with the values of the variables in question, 
            #then evaluated to check if the row of the MFStruct being examined is to be included in the output table
			if string not in ['>', '<', '==', '<=', '>=', 'and', 'or', 'not', '*', '/', '+', '-']:
				try:
					float(string)
					evalString += string
				except:
					if len(string.split('_')) > 1 and string.split('_')[1] == 'avg':
						evalString += str(MF_Struct[row][string]['avg'])
					else:
						evalString += str(MF_Struct[row][string])
			else:
				evalString += f' {string} '
		if eval(evalString.replace('=', '==')):
			row_info = []
			for val in S.split(','):
				if len(val.split('_')) > 1 and val.split('_')[1] == 'avg':
					row_info += [str(MF_Struct[row][val]['avg'])]
				else:
					row_info += [str(MF_Struct[row][val])]
			output.add_row(row_info)
		evalString = ''
	else:
        #there is no having condition, thus every MFStruct row will be added to the output table
		row_info = []
		for val in S.split(','):
			if len(val.split('_')) > 1 and val.split('_')[1] == 'avg':
				row_info += [str(MF_Struct[row][val]['avg'])]
			else:
				row_info += [str(MF_Struct[row][val])]
		output.add_row(row_info)
print(output)