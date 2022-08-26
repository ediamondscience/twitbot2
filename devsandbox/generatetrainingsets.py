import sys
import sqlite3
import time

connection = sqlite3.connect('tweetreplies.db', timeout=130)	#set up the connection to our db
c=connection.cursor()	#we always need a cursor for executing inserts 

def sql_insert(lis):		#helper function for inserting lists of data from users tweets into our db for later use
	c.executemany('INSERT INTO tweet_replies(tweet_id, reply_to_id, username, status, reply_to, favorite_count) values (?, ?, ?, ?, ?, ?)', lis)	#puts a whole list of values in at once, compuationally efficient to some degree
	connection.commit()	#always have to commit changes

def sql_delete(lis):		#helper function for deleting lists of data from users tweets into our db for later use
	c.executemany('DELETE FROM tweet_replies WHERE tweet_id LIKE ?', lis)	#removes several tweets at once, compuationally efficient to some degree
	connection.commit()	#always have to commit changes

def get_relevant_replies():
	c.execute("SELECT * FROM tweet_replies")
	counter=0
	next=c.fetchone()
	#print( set(next[3]).issubset(allowed_char_set) )

	while next != None:
		removelist=[]
		for i in next[3].split():
			if '@' in i or 'http' in i or '#' in i or '\n' in i:
				removelist.append(i)
		tofile=next[3].replace('\n', ' ')
		for i in removelist:
			tofile=tofile.replace(i, ' ')

		tofile=tofile.lstrip()
		tofile=tofile.rstrip()

		tofile=tofile+'\n'		

		with open('trainreplies.txt', 'a') as f:
			f.write(tofile)

		counter+=1
		if counter%10000 == 0:
			print(str(counter) + " replies recorded in journal so far...")
		next=c.fetchone()


def get_relevant_orig():
	c.execute("SELECT * FROM tweet_replies")
	counter=0
	next=c.fetchone()
	#print( set(next[3]).issubset(allowed_char_set) )

	while next != None:
		removelist=[]
		for i in next[4].split():
			if '@' in i or 'http' in i or '#' in i:
				removelist.append(i)
		tofile=next[4].replace('\n',' ')
		for i in removelist:
			tofile=tofile.replace(i, ' ')

		tofile=tofile.lstrip()
		tofile=tofile.rstrip()

		tofile=tofile+'\n'		

		with open('traintweets.txt', 'a') as f:
			f.write(tofile)

		counter+=1
		if counter%10000 == 0:
			print(str(counter) + " tweets recorded in journal so far...")
		next=c.fetchone()


print('Beginning by assembling original tweet training file. ')
get_relevant_orig()
print('Finished with original tweets, moving on to replies. ')
get_relevant_replies()
print('All done!')

