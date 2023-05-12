sigma = sigma.split(',')
pList = []
#splits predicates by each predicate statment and creates list to store the parts of each predicate in a single 2D array
for i in sigma:
	pList.append(i.split(' '))
for i in range(int(n)+1): # loop through the table to evaluate each grouping variable
    # 0th pass of the algorithm, where each row of the MF Struct is initalized for every unique group based on the grouping variables.
    # Each row in the MF struct also has its columns initalized appropriately based on the aggregates in the F-Vect
	if i == 0:
		for row in salesTable:
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
					if (fVectAttr.split('_')[1] == 'avg'):
                        # Average is saved as an object with the sum, count, and overall average
						value[fVectAttr] = {'sum':0, 'count':0, 'avg':0}
					elif (fVectAttr.split('_')[1] == 'min'):
                        # Min is initialized as 4994, which is the largest value of 'quant' in the sales table.
                        # This allows the first value that the algorithm comes across will be saved as the min (except the row with quant=4994)
						value[fVectAttr] = 4994 # Max quant in sales table
					else:
                        # Initalize values of count, sum and max to 0
						value[fVectAttr] = 0
				MF_Struct[key] = value #add row into MF Struct
	else: #The other n passes for each grouping variable 
			for aggregate in F.split(','):
				aggList = aggregate.split('_')
				groupVar = aggList[0]
				aggFunc = aggList[1]
				aggCol = aggList[2]
                # Check to make sure the aggregate function is being called on the grouping variable you are currently on (i)
				if i == int(groupVar):
					for row in query:
						key = ''
						for attr in V.split(','):
							key += f'{str(row[attr])},'
						key = key[:-1]
						if aggFunc == 'sum':
                            # Creates a string to be run with the eval() method by replacing grouping variables with their actual values
							evalString = sigma[i-1]
							for string in pList[i-1]:
								if len(string.split('.')) > 1 and string.split('.')[0] == str(i):
									rowVal = row[string.split('.')[1]]
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
                            # If evalString is true and count isn't 0, update the avg
							if eval(evalString.replace('=', '==')):
								sum += int(row[aggCol])
								count += 1
								if count != 0:
									MF_Struct[key][aggregate] = {'sum': sum, 'count': count, 'avg': (sum/count)}
						elif aggFunc == 'min':
							# check if row meets predicate requirements
							evalString = sigma[i-1]
							for string in pList[i-1]:
								if len(string.split('.')) > 1 and string.split('.')[0] == str(i):
									rowVal = row[string.split('.')[1]]
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
							# check if row meets predicate requirements
							evalString = sigma[i-1]
							for string in pList[i-1]:
								if len(string.split('.')) > 1 and string.split('.')[0] == str(i):
									rowVal = row[string.split('.')[1]]
									try:
										int(rowVal)
										evalString = evalString.replace(string, str(rowVal))
									except:
										evalString = evalString.replace(string, f"'{rowVal}'")
                            # If evalString is true, update the max
							if eval(evalString.replace('=', '==')):
								max = int(MF_Struct[key][aggregate])
								if int(row[aggCol]) > max:
									MF_Struct[key][aggregate] = row[aggCol]
						elif aggFunc == 'count':
							# check if row meets predicate requirements
							evalString = sigma[i-1]
							for string in pList[i-1]:
								if len(string.split('.')) > 1 and string.split('.')[0] == str(i):
									rowVal = row[string.split('.')[1]]
									try:
										int(rowVal)
										evalString = evalString.replace(string, str(rowVal))
									except:
										evalString = evalString.replace(string, f"'{rowVal}'")
							if eval(evalString.replace('=', '==')): # If evalString is true, increment the count
								MF_Struct[key][aggregate] += 1
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
        #there is no having condition, thus every MFStruct row will be in the output table
		row_info = []
		for val in S.split(','):
			if len(val.split('_')) > 1 and val.split('_')[1] == 'avg':
				row_info += [str(MF_Struct[row][val]['avg'])]
			else:
				row_info += [str(MF_Struct[row][val])]
		output.add_row(row_info)
print(output) #Pretty table corresponding to evaluation of query