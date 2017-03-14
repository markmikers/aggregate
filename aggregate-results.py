import os

# header for results table
# header = 'System\tNat\t'

ls = os.listdir('./')
lsd = []

# get directories with data
for i in ls:
	if os.path.isdir(os.path.abspath(i)):
		lsd.append(os.path.abspath(i))
		
analysis = ''
		
		
for i in lsd:
	entryLine = ''
	# system name, number of atoms (of each sort)
	entryLine += os.path.basename(i) + '\t'
	os.chdir(i)
	fsock = open('str.out', 'r')
	fstring = fsock.read()
	f = fstring.rstrip().split('\n')[4:]
	sorts = []
	for i in f:
		i = i.rstrip()
		if not(i[-4:-2] in sorts):
			sorts.append(i[-4:-2])
	sortcount = []
	for sort in sorts:
		# header += sort + '\t'
		sortcount.append(fstring.count(sort))
	entryLine += str(sum(sortcount)) + '\t'
	for sort in sortcount:
		entryLine += str(sort) + '\t'
	# magmom
	# header += 'magmom\t'
	fsock = open('OSZICAR', 'r')
	f = fsock.read()
	entryLine += f[f.rfind('mag=')+8:-1] + '\t'
	# volume, volume/atom, total energy
	fsock = open('OUTCAR', 'r')
	f = fsock.read()
	entryLine += f[f.rfind('volume of cell :')+23:f.rfind('volume of cell :')+28] + '\t'
	entryLine += '\t'
	entryLine += f[f.rfind('free  energy   TOTEN  =')+30:f.rfind('free  energy   TOTEN  =')+42] + '\t'
	entryLine += '\n'
	analysis += entryLine
	os.chdir('../')
fsock = open("analysis.txt", "w").write(analysis)