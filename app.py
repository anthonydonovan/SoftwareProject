import os
from flask import Flask,render_template, request, redirect, json
import requests
import sqlite3 as lite
import sys
import datetime
import csv
from os.path import join, dirname
from dotenv import load_dotenv
#all of the modules which are required

#loads in the .env file which contains sensitive information
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#global variables
ACCESS_TOKEN 	= os.getenv("ACCESS_TOKEN")
YOUR_MESSAGE 	= "Hello. Welcome to your first Spark room, send a message to start."
ADMIN_EMAIL		= os.getenv("ADMIN_EMAIL")
PUBLIC_URL		= os.getenv("PUBLIC_URL")
BOT_EMAIL       = 'gifbot@webex.bot'

app = Flask(__name__)

#sets the header to be used for authentication and data format to be sent.
def setHeaders():
	accessToken_hdr = 'Bearer ' + ACCESS_TOKEN
	spark_header = {'Authorization': accessToken_hdr, 'Content-Type': 'application/json; charset=utf-8'}
	return (spark_header)


#check if spark room already exists.  If so return the room id
def findRoom(the_header,room_name):
	roomId=None
	uri = 'https://api.ciscospark.com/v1/rooms'
	resp = requests.get(uri, headers=the_header)
	resp = resp.json()
	for room in resp["items"]:
		if room["title"] == room_name:
			roomId=room["id"]
			break
	return(roomId)

# checks if room already exists and if true returns that room ID. If not creates a new room and returns the room id.
def createRoom(the_header,room_name):
	roomId=findRoom(the_header,room_name)
	if roomId==None:
		roomInfo = {"title":room_name}
		uri = 'https://api.ciscospark.com/v1/rooms'
		resp = requests.post(uri, json=roomInfo, headers=the_header)
		var = resp.json()
		roomId=var["id"]
	return(roomId)

# adds a new member to the room
def addMembers(the_header,roomId, EMAIL):
	member = {"roomId":roomId,"personEmail":EMAIL, "isModerator": False}
	uri = 'https://api.ciscospark.com/v1/memberships'
	resp = requests.post(uri, json=member, headers=the_header)

#posts a message to the room
def postMsg(the_header,roomId,message):
	message = {"roomId":roomId,"text":message}
	uri = 'https://api.ciscospark.com/v1/messages'
	resp = requests.post(uri, json=message, headers=the_header)

#checks to see if admin token is valid
def testToken():
	url = "https://api.ciscospark.com/v1/rooms"

	headers = {
    	'Authorization': "Bearer " + ACCESS_TOKEN,
    	'Content-Type': "application/json",
    	'Cache-Control': "no-cache"
    	}

	response = requests.request("GET", url, headers=headers)
	return response

#check to see spark users status
def checkStatus():
	url = "https://api.ciscospark.com/v1/people"

	headers = {
    	'Authorization': "Bearer " + ACCESS_TOKEN,
    	'Content-Type': "application/json",
    	'Cache-Control': "no-cache"
    	}

	response = requests.request("GET", url, headers=headers)
	#print(response.text)
	return response.text

#formats data to be viewed on webpage
def processStatusData(data):
	rows = {}
	counter = 0
	for person in data['items']:
		rows[str(counter)] = [ person['emails'][0], person['created'], person['status'] ]
		counter = counter + 1
	return rows

#format data to be downloaded
def formatData2CSV(data):
	rows = [[ 'User ID', 'Date/Time', 'Email Address', 'Active on Spark' ]];
	counter = 1
	for person in data['items']:
		if person['emails'][0] != ADMIN_EMAIL:
			rows.append( [str(counter), person['created'], person['emails'][0], person['status'] ])
			counter = counter + 1
	return rows

#exports data to csv file
def printCsv(data):
	myFile = open('Users.csv', 'w')
	with myFile:
		writer = csv.writer(myFile)
		writer.writerows(data)
		myFile.close()

#set up webhook for specified room
def webhook(roomId):
	url = "https://api.ciscospark.com/v1/webhooks"
	payload = {
	    'name': 'Spark Learning Lab Webhook',
	    'targetUrl': PUBLIC_URL,
	    'resource': 'messages',
	    'event': 'created',
	    'filter': 'roomId=' + roomId
	}
	headers = {
	    'Authorization': "Bearer " + ACCESS_TOKEN,
	    'Content-Type': "application/json",
	    'Cache-Control': "no-cache",
	    }
	response = requests.request("POST", url, json=payload, headers=headers)

#example landing page, can be modified in future
@app.route('/', methods=['GET'])
def hello():
	return 'Welcome to Python Flask!'

#add specified bot into room
@app.route('/', methods=['POST'])
def addBotToRoom():
	requestData = request.get_json()
	header = setHeaders()
	roomId = requestData["filter"].split('=')[1]
	addMembers(header,roomId,BOT_EMAIL)
	return "1"

#used when user clicks on load database, to view in browser
@app.route('/loadDatabase', methods=['GET'])
def loadDatabase():
	statusData = checkStatus()
	rows = processStatusData(json.loads(statusData))
	return json.dumps({'rows': rows})

#calls function when download database button selected
@app.route('/downloadDatabase', methods=['GET'])
def downloadDatabase():
	statusData = checkStatus()
	csvData = formatData2CSV(json.loads(statusData))
	printCsv(csvData)

#function calls to check token is valid
@app.route('/checkToken', methods=['GET'])
def checkToken():
	response = testToken()
	return json.dumps({'status': response.status_code})

# directs to admin splash page
@app.route('/admin')
def admin():
	return render_template('index.html')

#directs to sign up splash page
@app.route('/signUp')
def signUp():
	return render_template('signUp.html')

#sign up new user process
@app.route('/signUpUser', methods=['POST'])
def signUpUser():
	user =  request.form['username'];
	password = request.form['password'];
	fname = request.form['fname'];
	lname = request.form['lname'];
	EMAIL = user;
	ROOM_NAME = user;
	url = "https://api.ciscospark.com/v1/people"

	payload = json.dumps({"emails": user, "displayName": password, "firstName": fname, "lastName": lname});
	headers = {
		'Authorization': "Bearer " + ACCESS_TOKEN,
		'Content-Type': "application/json",
		'Cache-Control': "no-cache"
		}
	response = requests.request("POST", url, data=payload, headers=headers)
	if response.ok == True:
		header = setHeaders()
		room_id = createRoom(header, ROOM_NAME)
		if room_id == None:
			sys.exit("Error: Please check that functions findRoom and createRoom return the room ID value.")
		addMembers(header,room_id,EMAIL)
		postMsg(header,room_id,YOUR_MESSAGE)
		webhook(room_id)
		return json.dumps({'status':'OK','user':user,'pass':password})
	else:
		return json.dumps({'status':'ERROR','user':user,'pass':password})

	return json.dumps({'status':'OK','user':user,'pass':password})

if __name__=="__main__":
	app.run()
