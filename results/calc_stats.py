import pandas as pd

# Load the CSV file
df = pd.read_csv('new_atl_normal.csv')
#df = pd.read_csv('CTL_comp.csv')

# only consider those rows where Sample size is between 20 and 40
df = df[(df['Sample size'] <= 40)]


# For each formula create a dictionary that gives the running time and sample size for each Sample size
result = df.groupby('Original Formula').apply(lambda x: list(zip(x['Size Upper'], x['Total Time']))).to_dict()
#result = df.groupby('Original Formula').apply(lambda x: list(zip(x['Size Upper'], x['Total_Time_U']))).to_dict()

print(type(result))

new_dict = {}

for formula in result:
	new_dict[formula] = {}
	for pair in result[formula]:
		if pair[0] not in new_dict[formula]:
			new_dict[formula][pair[0]] = pair[1]
		else:
			new_dict[formula][pair[0]] = (new_dict[formula][pair[0]]+ pair[1])/2

#print(result)
print(new_dict)


# print new dict in as a csv file
df = pd.DataFrame(new_dict)

df.to_csv('CTL_comp_avg.csv')
