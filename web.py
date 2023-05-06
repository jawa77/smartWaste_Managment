from flask import Flask,redirect, url_for,request,render_template
import os
import json
import math
app = Flask(__name__)
import mysql.connector
import geocoder
import pymongo
import requests

motorcntrl="192.168.199.168"
mong="192.168.199.95"

def db():
   
    mydb = mysql.connector.connect(

        host="localhost",
        user="root",
        password="jawa@2002",
        database="IbmDataBase"
    )
    mycursor = mydb.cursor()
    sql= "SELECT * FROM dsbn WHERE dusId = '1'"
    mycursor.execute(sql)

    records=mycursor.fetchall()
    return records

@app.route('/mysq')
def dashboard():
  data=db()
  print(data[0][0])
  g = geocoder.ip('me')
  print(g.lat)
  print(g.lng)
  print(g.ip)
  
  return render_template('web.html',data={"title":"Dashboadsss","id":data[0][0],
  "duslevel":data[0][1],"gas":data[0][2],"temp":data[0][3],"weight":data[0][4],
  "location":data[0][5],"humidity":data[0][6],"lat":data[0][7],"long":data[0][8]})

@app.route('/mong')
def dash():
   
  client = pymongo.MongoClient("mongodb://jawa:password@"+mong+":27017/?authMechanism=DEFAULT")
  db = client["ibm"]
# Collection Name
  col = db["updatedDb"]
  x = col.find_one()
  return render_template('web.html',data={"title":"Dashboadsss","id":x['dusid'],
  "duslevel":x['binLevel'],"gas":x['gas'],"temp":x['temp'],"weight":x['weight'],
  "location":x['location'],"humidity":x['humidity'],"lat":x['latitude'],"long":x['logtitude']})

@app.route('/')
def hello_world():
   data=db()
   gaspresent="no gas present"
   for row in data:
     print("Id = ", row[0], )
     print("duslevel = ", row[1])
     print("location  = ", row[2])
     print("temp =" , row[3])
     
  
   return "<h1>"+" BinID = "+ str(row[0])+", Level of Bin = "+str(row[1])+", Temperature = "+str(row[3])+", Location = '"+row[5]+"'</h1>"
   
@app.route('/ibm')
def hello_():
  
   return render_template('login.html')

@app.route('/login',methods=['POST'])
def loginibm(): 
  if 'username' in request.form and 'password' in request.form:
    username = request.form['username']
    password = request.form['password']

    client = pymongo.MongoClient("mongodb://jawa:password@"+mong+":27017/?authMechanism=DEFAULT")
    db = client["ibm"]

    col = db["login"]

    result=col.find_one({
            "username": username
        })
    if result:
            if result['password']==password:
                return redirect(url_for('dash'))
            else:
               raise Exception("incorrect password")
    


    return 
  
  else:
    return {
            "message": "Not enough parameters",
            "authenticated": False
         }, 400
     
@app.route('/motopen')
def motop():
   
  requests.get("http://"+motorcntrl+":1111/open")
  return redirect(url_for('dash'))

@app.route('/motcls')
def motcls():
   requests.get("http://"+motorcntrl+":1111/cls")
   return redirect(url_for('dash'))

if __name__ == '__main__':
   app.run(host='0.0.0.0',port=1134,debug=True)   # 0000 acept all public and localhost also