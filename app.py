from flask import Flask, render_template, request, session, jsonify
import urllib.request
from pusher import Pusher
from datetime import datetime
import httpagentparser
import json
import os
import hashlib
from dbsetup import create_connection, create_session, update_or_create_page, select_all_sessions, select_all_user_visits, select_all_pages
from waitress import serve

app = Flask(__name__)
app.secret_key = os.urandom(24)

# configure pusher object
pusher = Pusher(
app_id="883225",
key="0011ebc3764957afb33d",
secret="cce1ddd8a3bba4716086",
cluster='ap2',
ssl=True)

database = "./pythonsqlite.db"
conn = create_connection(database)
c = conn.cursor()

userOS = None
userIP = None
userCity = None
userBrowser = None
userCountry = None
userContinent = None
sessionID = None

def main():
    global conn, c

def file_creation(data):
    print("creating ths file")
    p=open('data.txt','w')
    for i in data:
        print(i)
        print(type(i))        
        if 1:
            p.write("\n===================================================================")
            p.write("\nuserIP - ")
            p.write(i['ip'])
            p.write("\ntime - ")
            p.write(i['time'])
            p.write("\nsessionID - ")
            p.write(i['session'])
            p.write("\nuserBrowser - ")
            p.write(i['browser'])
            p.write("\nuserOS - ")
            p.write(i['os'])
            p.write("\nuserCity - ")
            p.write(i['city'])
            p.write("\nuserCountry - ")
            p.write(i['country'])
            p.write("\nuserContinent - ")
            p.write(i['continent'])
            p.write("\n")
    p.close()
    print("created ths file")
    
def parseVisitor(data):
    update_or_create_page(c,data)
    pusher.trigger(u'pageview', u'new', {
        u'page': data[0],
        u'session': sessionID,
        u'ip': userIP
    })
    pusher.trigger(u'numbers', u'update', {
        u'page': data[0],
        u'session': sessionID,
        u'ip': userIP
    })

@app.before_request
def getAnalyticsData():
    global userOS, userBrowser, userIP, userContinent, userCity, userCountry,sessionID 
    userInfo = httpagentparser.detect(request.headers.get('User-Agent'))
    userOS = userInfo['platform']['name']
    userBrowser = userInfo['browser']['name']
    host_ip = urllib.request.urlopen('https://api.ipify.org/').read().decode('utf8')
    userIP = host_ip if request.remote_addr == '127.0.0.1' else request.remote_addr
    api = "https://www.iplocate.io/api/lookup/" + userIP
    try:
        resp = urllib.request.urlopen(api)
        result = resp.read()
        result = json.loads(result.decode("utf-8"))                                                                                                     
        userCountry = result["country"]
        userContinent = result["continent"]
        userCity = result["city"]
    except:
        print("Could not find: ", userIP)
    getSession()

def getSession():
    global sessionID
    time = datetime.now().replace(microsecond=0)
    if 'user' not in session:
        lines = (str(time)+userIP).encode('utf-8')
        session['user'] = hashlib.md5(lines).hexdigest()
        sessionID = session['user']
        pusher.trigger(u'session', u'new', {
            u'ip': userIP,
            u'continent': userContinent,
            u'country': userCountry,
            u'city': userCity,
            u'os': userOS,
            u'browser': userBrowser,
            u'session': sessionID,
            u'time': str(time),
        })
        data = [userIP, userContinent, userCountry, userCity, userOS, userBrowser, sessionID, time]
        create_session(c,data)
    else:
        sessionID = session['user']

@app.route('/')
def index():
    data = ['home', sessionID, str(datetime.now().replace(microsecond=0))]
    parseVisitor(data)
    return render_template('index.html')

@app.route('/about')
def about():
    data = ['about',sessionID, str(datetime.now().replace(microsecond=0))]
    parseVisitor(data)
    return render_template('about.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/dashboard/<session_id>', methods=['GET'])
def sessionPages(session_id):
    result = select_all_user_visits(c,session_id)
    print("\n\n\n\n entered session "+str(result)+"\n\n")
    return render_template("dashboard-single.html",data=result)

@app.route('/get-all-sessions')
def get_all_sessions():
    data = []
    dbRows = select_all_sessions(c)
    for row in dbRows:
        data.append({
            'ip' : row['ip'],
            'continent' : row['continent'],
            'country' : row['country'], 
            'city' : row['city'], 
            'os' : row['os'], 
            'browser' : row['browser'], 
            'session' : row['session'],
            'time' : row['created_at']
        })

    file_creation(data)
    return jsonify(data)

if __name__ == '__main__':
    main()
    serve(app.run(debug=False), host='0.0.0.0', port=8080)
    #app.run(debug=True
        
