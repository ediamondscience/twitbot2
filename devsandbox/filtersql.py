import sys
import sqlite3
import time

connection = sqlite3.connect('tweetreplies.db', timeout=130)	#set up the connection to our db
c=connection.cursor()	#we always need a cursor for executing inserts 

def sql_insert(lis):		#helper function for inserting lists of data from users tweets into our db for later use
	c.executemany('INSERT INTO tweet_replies(tweet_id, reply_to_id, username, status, reply_to, favorite_count) values (?, ?, ?, ?, ?, ?)', lis)	#puts a whole list of values in at once, compuationally efficient to some degree
	connection.commit()	#always have to commit changes

def sql_delete(lis):		#helper function for deleting lists of data from users tweets into our db for later use
	c.executemany('DELETE FROM tweet_replies WHERE tweet_id = ?', lis)	#removes several tweets at once, compuationally efficient to some degree
	connection.commit()	#always have to commit changes

def get_irrelevant_replies():
	c.execute("SELECT * FROM tweet_replies")
	dellist=[]

	#The allowed character set can be changed here to get a region specific bot (hopefully)
	allowed_char_set=set(' abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.:;<>/?`~!@#$%^&*()-=_+[]{}"'+"\\ \n'")
	
	next=c.fetchone()
	#print( set(next[3]).issubset(allowed_char_set) )
	while next != None:
		if ( set(next[3]).issubset(allowed_char_set) ): 
			pass
		else:
			dellist.append( (str(next[0]),) )
		next=c.fetchone()
	return dellist

def get_irrelevant_tweets():
	c.execute("SELECT * FROM tweet_replies")
	dellist=[]

	#The allowed character set can be changed here to get a region specific bot (hopefully)
	allowed_char_set=set(' abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.:;<>/?`~!@#$%^&*()-=_+[]{}"'+"\\ \n'")
	
	next=c.fetchone()
	#print( set(next[3]).issubset(allowed_char_set) )
	while next != None:
		if ( set(next[4]).issubset(allowed_char_set) ): 
			pass
		else:
			dellist.append( (str(next[0]),) )
		next=c.fetchone()
	return dellist

def clean_db():
	c.execute("SELECT * FROM tweet_replies")
	dellist=[]
	
	next=c.fetchone()
	while next != None:

		lis1=[]
		lis2=[]
		string1=next[3].replace('\n',' ').split()
		string2=next[4].replace('\n',' ').split()

		for i in string1:
			if '@' in i or '#' in i or 'http' in i:
				lis1.append(i)

		for i in string2:
			if '@' in i or '#' in i or 'http' in i:
				lis2.append(i)
		
		string1=' '.join(string1)
		string2=' '.join(string2)

		#print(lis1)
		#print(lis2)

		for i in lis1:
			string1=string1.replace(i,' ')
		for i in lis2:
			string2=string2.replace(i,' ')

		string1=string1.lstrip()
		string2=string2.lstrip()

		string1=string1.rstrip()
		string2=string2.rstrip()

		#print('String1 remains: '+string1)
		#print('String2 remains: '+string2)

		if len(string1.replace(' ',''))==0 or len(string2.replace(' ',''))==0:
			dellist.append( (str(next[0]), ) )
		next=c.fetchone()
	return dellist

badlist = get_irrelevant_replies()
print('List of bad ids from replies compiled, purging from db.... Entries to remove: '+str(len(badlist)))
for i in range(0, len(badlist), 1000):
	sql_delete(badlist[i:i+1000])
	print("Now on step :" +str(i+1000 ))

badlist = get_irrelevant_tweets()
print('List of bad ids from original tweets compiled, purging from db....'+str(len(badlist)))
for i in range(0, len(badlist), 1000):
	sql_delete(badlist[i:i+1000])
	print("Now on step :" +str(i+1000 ))

badlist = clean_db()
print('List of mostly extraneous tweets compiled, purging from db....'+str(len(badlist)))
for i in range(0, len(badlist), 1000):
	sql_delete(badlist[i:i+1000])
	print("Now on step :" +str(i+1000 ))

