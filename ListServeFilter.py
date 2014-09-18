#!/usr/bin/python

import httplib2
import gflags
import operator
import math
from apiclient.discovery import build
import apiclient.errors
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
def getReceiver(head):
	for i in range(0,len(head)):
		subheader=header[i]
		if (subheader['name']=="To"):
			return subheader['value']
def getSender(head):
	for i in range(0,len(head)):
		subheader=header[i]
		if (subheader['name']=="From"):
			return subheader['value']

def addToSenders(sender):
	try:
		Senders[sender]+=1
	except:
		Senders[sender]=1
def addToSent(sent):
	try:
		SentTo[sent]+=1
	except:
		SentTo[sent]=1
		
def getEmail(sender):
	start=sender.find('<')
	if start==-1:
		return ""
	else:
		end=sender.find('>',start)
		if(end==-1):
			return ""
		else:
		 	return sender[start+1:end]
def ListThreadsMatchingQuery(service, user_id, query=''):
	try:
		response = service.users().threads().list(userId=user_id,maxResults=LIMIT, q=query,labelIds=['CATEGORY_FORUMS']).execute()
		threads = []
		if 'threads' in response:
			threads.extend(response['threads'])
		while ('nextPageToken' in response):
			page_token = response['nextPageToken']
			response = service.users().threads().list(userId=user_id, q=query,
				pageToken=page_token).execute()
			threads.extend(response['threads'])
			if (len(threads)>LOOP):
				break
		return threads
	except errors.HttpError, error:
		print 'An error occurred: %s' % error
def GetThread(service, user_id, thread_id):
	try:
	        thread = service.users().threads().get(userId=user_id, id=thread_id).execute()
		messages = thread['messages']
	#print ('thread id: %s - number of messages '
	#			'in this thread: %d') % (thread['id'], len(messages))
		return thread
	except errors.HttpError, error:
		print 'An error occurred: %s' % error

# Path to the client_secret.json file downloaded from the Developer Console
CLIENT_SECRET_FILE = 'client_secret.json'

# Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'

# Location of the credentials storage file
STORAGE = Storage('gmail.storage')

# Start the OAuth flow to retrieve credentials
flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
http = httplib2.Http()

# Try to retrieve credentials from storage or run the flow to generate them
credentials = STORAGE.get()
if credentials is None or credentials.invalid:
  credentials = run(flow, STORAGE, http=http)

# Authorize the httplib2.Http object with our credentials
http = credentials.authorize(http)

# Build the Gmail service from discovery
service = build('gmail', 'v1', http=http)

# Retrieve a page of threads
#threads = service.users().threads().list(userId='me').execute()
# Print ID for each thread
LIMIT=int(raw_input("Enter the number of threads (sub-threads) you want to explore "))
LOOP=math.ceil(LIMIT/100)*100
Senders={}
SentTo={}
COUNT=0
ThreadList=ListThreadsMatchingQuery(service,'me',"")
for j in range(0,len(ThreadList)):
    	id=ThreadList[j]['id']
    	Thread=GetThread(service,'me',id)
    	for x in range(0,len(Thread['messages'])):
    	    header=Thread['messages'][x]['payload']['headers']
    	    receivers=getReceiver(header)
            rlist=receivers.split(",")
            for name in rlist:
                 addToSent(getEmail(name))   
            COUNT+=1
	    if COUNT>=LIMIT:
	     	break
	if COUNT>=LIMIT:
	 	break
sorted_sent=sorted(SentTo.iteritems(),key=operator.itemgetter(1),reverse=True)
fr=open("Forums.txt",'w')
for x,y in sorted_sent:
	if len(x)>0:
		fr.write(x+"  "+str(y)+"\n");
fr.close()
