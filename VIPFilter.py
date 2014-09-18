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
from oauth2client.client import OAuth2Credentials
from datetime import date, timedelta,datetime
from flask import Flask
from flask import Response
from flask import jsonify
from flask import request
app = Flask(__name__)

def getReceiver(head, header):
	for i in range(0,len(head)):
		subheader=header[i]
		if (subheader['name']=="To"):
			return subheader['value']
def getSender(head, header):
	for i in range(0,len(head)):
		subheader=header[i]
		if (subheader['name']=="From"):
			return subheader['value']

def addToSenders(Senders,sender):
    try:
        Senders[sender]+=1
    except:
        Senders[sender]=1
def addToSent(SentTo,sent):
    try:
        SentTo[sent]+=1
    except:
        SentTo[sent]=1
		
def getEmail(sender):
	if sender:
		start=sender.find('<')
		if start==-1:
			return ""
		else:
			end=sender.find('>',start)
			if(end==-1):
				return ""
			else:
				return sender[start+1:end]
def getPastDate():
    days=30
    d=date.today()-timedelta(days=days)
    dt=datetime.strftime(d,"%Y%m%d")
    return dt
def ListThreadsMatchingQuery(service, user_id, query):
	try:
		response = service.users().threads().list(userId=user_id, q=query,labelIds=['CATEGORY_PERSONAL']).execute()
		threads = []
		if 'threads' in response:
			threads.extend(response['threads'])
		while ('nextPageToken' in response):
			page_token = response['nextPageToken']
			response = service.users().threads().list(userId=user_id, q=query,
				pageToken=page_token).execute()
			threads.extend(response['threads'])
			if (len(threads)>=500):
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

@app.route("/vip", methods=['POST'])
def vipAlgorithm():
	print(request.form)
	print(request.form.keys)
	list = []
	http = httplib2.Http()

	credentials = OAuth2Credentials("poop",
	                                "655269106649-rkom4nvj3m9ofdpg6sk53pi65mpivv7d.apps.googleusercontent.com", # Client ID
	                                "1ggvIxWh-rV_Eb9OX9so7aCt",
	                                request.form['refresh_token'],
	                                datetime.now(), # token expiry
	                                "https://accounts.google.com/o/oauth2/token", None)

	print(credentials)

	# Authorize the httplib2.Http object with our credentials
	http = credentials.authorize(http)

	# Build the Gmail service from discovery
	service = build('gmail', 'v1', http=http)

	# Retrieve a page of threads
	threads = service.users().threads().list(userId='me').execute()
	# Print ID for each thread
	Senders={}
	SentTo={}
	COUNT=0
	qry="-in:chats after:"+getPastDate()
	ThreadList=ListThreadsMatchingQuery(service,'me',qry)
	for j in range(0,len(ThreadList)):
		id=ThreadList[j]['id']
		Thread=GetThread(service,'me',id)
		for x in range(0,len(Thread['messages'])):
			header=Thread['messages'][x]['payload']['headers']
			if 'labelIds' in Thread['messages'][x]: 
				labelid=Thread['messages'][x]['labelIds']
				if "SENT" in labelid:
					receivers=getReceiver(header, header)
					if receivers:
						rlist=receivers.split(",")
						for name in rlist:
							addToSent(SentTo,getEmail(name))   
				else:
					addToSenders(Senders,getEmail(getSender(header, header)))
			else:
				addToSenders(Senders,getEmail(getSender(header, header)))
			COUNT+=1
		if COUNT>=10:
			break
	 	if COUNT>=10:
			break
	sorted_senders=sorted(Senders.iteritems(),key=operator.itemgetter(1),reverse=True)
	sorted_sent=sorted(SentTo.iteritems(),key=operator.itemgetter(1),reverse=True)
	#fr=open("Senders.txt",'w')
	for WEIGHT in [2]:
	    FinalResult=Senders     
	    for x,y in SentTo.iteritems():
	        try:
	            FinalResult[x]+=WEIGHT*y
	        except:
	            FinalResult[x]=WEIGHT*y
	    sorted_final_result=sorted(FinalResult.iteritems(),key=operator.itemgetter(1),reverse=True)
	    for x,y in sorted_final_result:
	        if x and len(x)>0:
	            z = x
	            list.append(x)
	return jsonify(results = list)
if __name__ == "__main__":
	app.debug = True
	app.run()
