def find_num_lines(filename): #simple iterator to quickly find the number of lines in a file -- used here to count the number of accounts followed by a specific account
	it=0
	with open(filename) as f:
		while f.readline() != '':
			it+=1
			f.readline()
	return it


split=.1

filelen=find_num_lines('traintweets.txt')

numlines=int(filelen*split)

testlines=[]
with open('traintweets.txt') as f:
	for i in range(0, numlines):
		testlines.append(f.readline())

replylines=[]
with open('trainreplies.txt') as f:
	for i in range(0, numlines):
		replylines.append(f.readline())

with open('tst2012.from', 'w') as f:
	for i in testlines:
		f.write(i+'\n')

with open('tst2012.to', 'w') as f:
	for i in replylines:
		f.write(i+'\n')

testlines=[]
with open('traintweets.txt') as f:
	for i in range(0, numlines):
		f.readline()
	for i in range(0, numlines):
		testlines.append(f.readline())

replylines=[]
with open('trainreplies.txt') as f:
	for i in range(0, numlines):
		f.readline()
	for i in range(0, numlines):
		replylines.append(f.readline())

with open('tst2013.from', 'w') as f:
	for i in testlines:
		f.write(i+'\n')

with open('tst2013.to', 'w') as f:
	for i in replylines:
		f.write(i+'\n')

trainreplylines=[]
with open('trainreplies.txt') as f:
	for i in range(0, 2*numlines):
		f.readline()
	next=f.readline()
	while next != '':
		trainreplylines.append(next)
		next=f.readline()

trainlines=[]
with open('traintweets.txt') as f:
	for i in range(0, 2*numlines):
		f.readline()
	next=f.readline()
	while next != '':
		trainlines.append(next)
		next=f.readline()

with open('train.from', 'w') as f:
	for i in trainlines:
		f.write(i+'\n')

with open('train.to', 'w') as f:
	for i in trainreplylines:
		f.write(i+'\n')
