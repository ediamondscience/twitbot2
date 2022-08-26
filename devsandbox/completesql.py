import sys
import sqlite3
import json
import tweepy
import time

apilist=[]
accselect=1

connection = sqlite3.connect('tweetreplies.db')	#set up the connection to our db
c=connection.cursor()	#we always need a cursor for executing inserts 

def get_auth(acc_details):	#Useful for getting a tweepy Auth object for streaming tweets, possibly not needed here

	auth = tweepy.OAuthHandler(acc_details['consumer_key'], acc_details['consumer_secret'])
	auth.set_access_token(acc_details['access_token'], acc_details['access_token_secret'])
	return auth

def get_api(acc_details):	#Returns api object of pulling old tweets

	api = tweepy.OAuthHandler(acc_details['consumer_key'], acc_details['consumer_secret'])
	api.set_access_token(acc_details['access_token'], acc_details['access_token_secret'])
	return tweepy.API(api, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)	#set tweepy's automatic rate limiting on to avoid rate limiting issues

def readjson():	#reads an account file for the keys needed to connect to the twitter API
	accfile='./accts.json'	#location of the file, just expected in the same directory as this file for now
	try:
		with open(accfile, 'r') as account_data:
			d = json.load(account_data)
			for item in d:	#checking for duplicate accounts
				duplicate=0
				for api in apilist:
					if(api["consumer_key"] == item["consumer_key"] and api["consumer_secret"] == item["consumer_secret"] and api["access_token"] == item["access_token"] and api["access_token_secret"] == item["access_token_secret"]):
						duplicate=1
				if(duplicate==0):
					apilist.append(item)
				else:
					print("Duplicate Account Read & Ignored")
	except:
		print("No json Account file found.")

def writejson():	#rewrites account file
	with open("./accts.json", "w") as outfile:
		json.dump(apilist, outfile)

def initaccs():		#reads text files containing twitter api keys, converts them into more compact json file, just auxillary here
	readjson()	#starts by reading existing json accounts
	path='./input/'	#path to directory containing individual text files
	namearray=[]
	try:
		for filename in os.listdir(path):	#get filenames to open them in a loop
			namearray.append(path+filename)
		for name in namearray:	#open the files in a loop and make sure they aren't duplicates that already exist in accts.json
			try:
				f = open(name)
		
				store = {}	#read data into a dictionary
				store["acc_name"]=name[8:] #removes directory preamble
				store["consumer_key"]=f.readline()[:-1] #removes the \n
				store["consumer_secret"]=f.readline()[:-1]
				store["access_token"]=f.readline()[:-1]
				store["access_token_secret"]=f.readline()[:-1]
				
				duplicate=0	#check the data for duplicates
				for api in apilist:
					if(api["consumer_key"] == store["consumer_key"] and api["consumer_secret"] == store["consumer_secret"] and api["access_token"] == store["access_token"] and api["access_token_secret"] == store["access_token_secret"]):
						duplicate=1
				if(duplicate==0):
					apilist.append(store)
				else:
					print("Discarded duplicate account file")
			except:
				print("Cannot open: "+name)
		print("Found "+str(len(apilist))+" account file(s).")
		writejson()
		#print(apilist)
	except:
		print("Please enter your Twitter App Keys into four seperate lines in a text file in this order: \n 1.consumer key\n 2.consumer secret\n 3.access token\n 4.access token secret\n Place the text file into the input directory and rerun")

#function to pick active account out of multiple available
def pick_acc():
	readjson()
	accselmsg="Please enter a number corresponding to the account you with to use: \n"
	for i in range(0,len(apilist)):
		accdetail=str(i)+" - "+apilist[i]["acc_name"]+"\n"
		accselmsg+=accdetail
	print(accselmsg)
	accselect=int(input())
	print("Setting current account to "+apilist[accselect]["acc_name"])

def sql_insert(lis):		#helper function for inserting lists of data from users tweets into our db for later use
	c.executemany('INSERT INTO tweet_replies(tweet_id, reply_to_id, username, status, reply_to, favorite_count) values (?, ?, ?, ?, ?, ?)', lis)	#puts a whole list of values in at once, compuationally efficient to some degree
	connection.commit()	#always have to commit changes

def get_id_list():
	c.execute('SELECT reply_to_id FROM tweet_replies WHERE reply_to LIKE "None"')
	wow = c.fetchmany(100)	#how many tweets we can request from twitter at a time
	retlist=[]
	for item in wow:
		retlist.append(int(item[0]))
	return retlist

def ret_original_tweets(idlist):
	api=get_api(apilist[accselect])
	retlist=[]

	try:	
		new_tweets=api.statuses_lookup(idlist, trim_user=True)
		#print(new_tweets)
	except tweepy.TweepError as e:
		print(e)  #useful for debugging new codes and problems
		
	for tweet in new_tweets:
		#print(tweet.text)
		if tweet.text == '' or len(tweet.text)==0:
			print('trying to delete bad tweet from db')
			c.execute("DELETE FROM tweet_repies WHERE reply_to_id=?", tweet.id)
			connection.commit()
		else:
			retlist.append([str(tweet.text), str(tweet.id)])
	if len(retlist)==0:
		idstr=[(str(ids), ) for ids in idlist]	#set up list for requests
		#print(idstr)
		c.executemany("DELETE FROM tweet_replies WHERE reply_to_id=?",idstr)
		connection.commit()
	return retlist
	
def update_sql(toadd):
	c.executemany('UPDATE tweet_replies SET reply_to=? WHERE reply_to_id=?', toadd)
	#print("Updating db")
	connection.commit()

def finish_db():
	readjson()
	api=get_api(apilist[accselect])
	idlist=get_id_list()
	while len(idlist) != 0:
		toadd=ret_original_tweets(idlist)
		update_sql(toadd)
		idlist=get_id_list()
	
	print('All Done!')

		
finish_db()

