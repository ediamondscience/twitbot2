import sys
import sqlite3
import json
import tweepy
import time

apilist=[]
accselect=0

connection = sqlite3.connect('tweetreplies.db', timeout=130)	#set up the connection to our db
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

#makes a list of twitter ids that are being followed by a specific account
def makeacclist():
	readjson()	#assumes json file has been set up, does not check text file directory
	api = get_api(apilist[accselect])
	acclistid=63796828	#in this case I want verified accounts, so this is the verified twiiter account that follows all verified users
	accs=tweepy.Cursor(api.friends_ids, id=acclistid).items()	#set up the list of ids that this account is following
	while True:	#iterate through friend ids
		try:
			idnum=accs.next()
			#print(idnum)
			with open('bluecheckmarks.txt', 'a') as f:	#would probably be better to open this once at the beginning of this function but we're more limited by twitters api rate limits anyway
				f.write(str(idnum)+'\n')
		except tweepy.TweepError as e:	#catches stange issues, may not be needed here
			#print(e)
			print("Sleeping for Twitter API")
			time.sleep(60*15)
			continue
		except StopIteration:	#stop condition, essentially there are no ids left to give us so we stop updating our list
			break

def find_num_lines(filename): #simple iterator to quickly find the number of lines in a file -- used here to count the number of accounts followed by a specific account
	it=0
	with open(filename) as f:
		while f.readline() != '':
			it+=1
			f.readline()
	return it

def collect_relevant_tweets(uid):	#returns a list containing the information we need from tweets matching our criteria
	api = get_api(apilist[accselect])	#set up our api for pulling tweets from twitter
	retlist=[]	#set up a list to contain what we want to pass back to be put into our SQLite3 db

	new_tweets = tweepy.Cursor(api.user_timeline, user_id=uid).items() #initiate our tweetlist for iteration in our loop below
	
	#keep pulling data until we reach a stop execption
	while True:

		#try to iterate and catch specific errors for easy autonomous operation
		try:
			tweet = new_tweets.next()
		except tweepy.TweepError as e:
			
			if e.response.status_code==401:    #this seems to mean that the user has some sort of privacy control on their account		apparently e.response.status_code works but e.api_code doesn't
				break     #return empty list to not waste time on stubborn privacy settings

			print(e)  #useful for debugging new codes and problems
			print()  #useful for debugging new codes and problems
			print('Sleeping for Twitter API restriction') #setting the program to sleep for 15min is the default routine for handling exceptions -- seems to work in most but not all cases
			print('Tweets collected so far for ' + str(uid) + ' : ' + str(len(retlist)) )
			time.sleep((60*1)+2)    #this mostly catches 503 errors
			continue	#restart the loop
		except StopIteration:   #this of course means the list of tweets is empty and our job is done
			break	#break out of the loop and return retlist

		#saving the relevent bits of the most recent tweets if they are replies
		if tweet.in_reply_to_status_id != None:
			tin=[str(tweet.id), str(tweet.in_reply_to_status_id), str(tweet.user.name), str(tweet.text), str(None), int(tweet.favorite_count)]	#getting the relevent bits
			retlist.append(tin)	#saving them
		
	
		if ( len(retlist)%100==0 and len(retlist)!=0 ):
			print("...{} tweets downloaded so far".format(len(retlist)))

	return retlist

def sql_insert(lis):		#helper function for inserting lists of data from users tweets into our db for later use
	c.executemany('INSERT INTO tweet_replies(tweet_id, reply_to_id, username, status, reply_to, favorite_count) values (?, ?, ?, ?, ?, ?)', lis)	#puts a whole list of values in at once, compuationally efficient to some degree
	connection.commit()	#always have to commit changes

def assemble_db():
	readjson()	#init our account details
	listlen= find_num_lines('bluecheckmarks.txt')	#figure out how many lines are in our account list file, how many peoples tweets we want to mine
	
	try:		#try to open file containing our save indicating which line of the 
		with open('listprog.txt', 'r') as f:
			prog=int(f.readline())	#read our value from file
			proginit=prog	#for keeping a record of where we started this time

	except IOError:	#this usually means listprog.txt isn't in the right directory or doesn't exist
		#init_prog()	#this is a dangerous function so I'm suspending it's danger by not writing it until I have all the data I want
		print("Couldn't init prog var, check listprog file")	#its not hard to remake this file, it's one number on one line

	with open('bluecheckmarks.txt', 'r') as f:	#open our account file 
		for i in range(0,prog):		#read through enough lines to get back to where we were according to our previous save
			f.readline()
			
		for i in range(proginit, listlen):	#starting to collect tweets for users in this loop
			newtweets=collect_relevant_tweets(f.readline())		#get new user id and return a list of their tweets we want to store
			if len(newtweets) == 0:		#don't insert nothing
				print("No tweets could be collected for user")
			else:
				sql_insert(newtweets)	#insert our list of relevant information
			prog+=1	#increment prog and save it's values
			with open('listprog.txt', 'w') as progressfile:
				progressfile.write(str(prog))
			print(str(prog) + "people's tweet's collected")	#update the user to assure them that the program is still running
				
		

def make_db():	#helper function for setting up our db to store our cool data
	c.execute("CREATE TABLE IF NOT EXISTS tweet_replies(tweet_id TEXT UNIQUE PRIMARY KEY,  reply_to_id TEXT, username TEXT, status TEXT, reply_to TEXT, favorite_count INT)")

#make_db()
assemble_db()
	


