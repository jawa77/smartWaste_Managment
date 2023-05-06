import RPi.GPIO as GPIO
import time
import mysql.connector
import yagmail
import Adafruit_DHT
import geocoder
import threading
import subprocess
import pika
import time
import pymongo

tomail="mail@gmail.com"
serverip="192.168.239.95"


dusbinLevelInper=10
gasprsnt=0
loation="trade center"
temperature=0

weight=1
latitute=0
langtitute=0
dusHeight=10
humidity=0

open=0
close=0

TRIG=21
ECHO=20
tem=19
ga=13
solanoid=5
pir=6
ser=16

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.setup(tem, GPIO.IN) 
GPIO.setup(pir,GPIO.IN)
GPIO.setup(ga,GPIO.IN)
GPIO.setup(solanoid,GPIO.OUT)

def mangodatabs():
    myclient = pymongo.MongoClient("mongodb://jawa:password@"+serverip+":27017/?authMechanism=DEFAULT")

    db=myclient["ibm"]
    users=db.insertedDb
    user2=db.updatedDb

    id=users.insert_one({
            "dusid":1,
            "binLevel":dusbinLevelInper,
            "temp":temperature,
            "humidity":humidity,
            "gas":gasprsnt,
            "weight":weight,
            "latitude":latitute,
            "logtitude":langtitute,
            "location":loation,
            "time":time.time()
        })
    

    filter = { 'dusid': 1 }
 
    newvalues = { "$set": {
            "binLevel":dusbinLevelInper,
            "temp":temperature,
            "humidity":humidity,
            "gas":gasprsnt,
            "weight":weight,
            "latitude":latitute,
            "logtitude":langtitute,
            "location":loation,
            "time":time.time()
        } }
    
    id2=user2.update_one(filter, newvalues)

    # print("succes fully inserted and updated  {}{} ".format(id,id2))
    print("succesfully updated in db")

def manthrd2():
    myclient = pymongo.MongoClient("mongodb://jawa:password@"+serverip+":27017/?authMechanism=DEFAULT")

    db=myclient["ibm"]
    users=db.updatedDb
    filter = { 'dusid': 1 }
    newvalues = { "$set": {
            "temp":temperature,
            "humidity":humidity,
            "time":time.time()
        } }
    id2=users.update_one(filter, newvalues)
    #print("updated --{}".format(id2))
    print("updated in db")

def DataBaseCon():
    
    mydb = mysql.connector.connect(

        host=serverip,
        user="root",
        password="jawa@2002",
        database="IbmDataBase"
    )
    mycursor = mydb.cursor()


    sql="UPDATE `dsbn` SET `dusLevel` ="+str(dusbinLevelInper)+",`humidity`= '"+str(humidity)+"',`temp`='"+str(temperature)+"',`weight`='"+str(weight)+"',`gas`='"+str(gasprsnt)+"',`location`= '"+str(loation)+"',`latitude`= '"+str(latitute)+"',`longtitude`= '"+str(langtitute)+"' WHERE dusId='1';"
    print(sql)
    mycursor.execute(sql)
    mydb.commit()

    print(mycursor.rowcount, "record(s) affected")

def DataBaseTHRD2():
    
    mydb = mysql.connector.connect(

        host=serverip,
        user="root",
        password="jawa@2002",
        database="IbmDataBase"
    )
    mycursor = mydb.cursor()


    sql="UPDATE `dsbn` SET `humidity`= '"+str(humidity)+"',`temp`='"+str(temperature)+"' WHERE dusId='1';"
    print(sql)
    mycursor.execute(sql)
    mydb.commit()

    print(mycursor.rowcount, "record(s) affected temp and humidity")

def mail():
    Frommailadress="anonymous002k2@gmail.com"
    password="uwlmlzmqywoyfwab" 
    yag = yagmail.SMTP(user=Frommailadress, password=password)
    yag.send(to=tomail, subject=' Collection of Leachate', contents="Container ID=1 \n  Container located at   "+str(loation)+" \nTemperature = "+str(temperature)+"\n Container 1 is filled ")
    print("--------->successfully mail send")  

def mailHEIgher():
    Frommailadress="anonymous002k2@gmail.com"
    password="uwlmlzmqywoyfwab" 
    yag = yagmail.SMTP(user=Frommailadress, password=password)
    yag.send(to=tomail, subject="Manage Container", contents="Container ID=1 \n  Container located at "+str(loation)+"")
    print("---------------->successfully mail send again")  

def latlong():
    global langtitute
    global latitute
    g = geocoder.ip('me')
    print(g.lat)
    print(g.lng)
    latitute=g.lat
    langtitute=g.lng

def location():
    global loation
    loation="trade center"

def gas():
    global gasprsnt
    a= GPIO.input(13) 
    
    if(a==1):
        gasprsnt=0
        print("gas present represnt in binary  "+str(gasprsnt))
    else:
        gasprsnt=1
        print("gas present represnt in binary  "+str(gasprsnt))

def Temp():
        global temperature
        global humidity
        dhtsensor= Adafruit_DHT.DHT11
        pin=19
        humidity,temp=Adafruit_DHT.read(dhtsensor,pin)
        print("temperature is {}".format(temp))
        print("humidty is{}".format(humidity))
        if(temp==None or humidity==None):
            pass
        else:  
            temperature=temp
            humidity=humidity
            if not t1.is_alive():
                #DataBaseTHRD2()
                manthrd2()
           
            if(temperature>=20):
                global open
                global close
                if(open==1):
                    print("\n Already open \n")
                else:
                    subprocess.run(["python3", "seropen.py"])
                    print("open--->")
                    time.sleep(2)
                    open=1
                    close=0
            else:
                if(close==1):
                    print("alredy closed")
                else:
                    subprocess.run(["python3", "sercls.py"])
                    print("close----->")
                    time.sleep(2)
                    close=1
                    open=0

def solaidOn():
    GPIO.output(solanoid,0)

def solanoidof():
    GPIO.output(solanoid,1)
    print("volve closed")

def distances():
    global dusbinLevelInper
    global weight
    #print("distance measurement in progress")
    GPIO.output(TRIG,False)
    #print("waiting for sensor to settle")
    time.sleep(0.2)
    GPIO.output(TRIG,True)
    time.sleep(0.00001)
    GPIO.output(TRIG,False)
    while GPIO.input(ECHO)==0:
        pulse_start=time.time()
    while GPIO.input(ECHO)==1:
        pulse_end=time.time()
    pulse_duration=pulse_end-pulse_start
    distance=pulse_duration*17150
    distance=round(distance,2)
    print("distance:",distance,"cm")
    time.sleep(2)


   
    if(distance>=dusHeight):
            
        dusbinLevelInper=0
        weight=0    
    elif(distance<=dusHeight and distance>=dusHeight*75/100):
            
        dusbinLevelInper=25
        weight=2.5
        
    elif(distance<=dusHeight*75/100 and distance>=dusHeight*50/100):
        dusbinLevelInper=50
        weight=5
        
    elif(distance<=dusHeight*50/100 and distance>=dusHeight*30/100):
        dusbinLevelInper=80
        weight=8
 
    else:
        dusbinLevelInper=100
        weight=10
       
        
       #60     0
       #60-45  25
       #45-30  50   
       #30-18  80
       #18-0   100 
       
    #Temp()
    location()
    latlong()
    gas()   
    #DataBaseCon()
    mangodatabs()
                          
def findDstnce():
    global dusHeight
    GPIO.output(TRIG,False)
    time.sleep(0.2)
    GPIO.output(TRIG,True)
    time.sleep(0.00001)
    GPIO.output(TRIG,False)
    while GPIO.input(ECHO)==0:
        pulse_start=time.time()
    while GPIO.input(ECHO)==1:
        pulse_end=time.time()
    pulse_duration=pulse_end-pulse_start
    distance=pulse_duration*17150
    distance=round(distance,2)
    print("distance:",distance,"cm")
    time.sleep(2)
    
    dusHeight=int(distance)
    
def find():
    findDstnce()
    print("\n PRESS \n\n 1--->Above cm is correct \n\n 2--->Recalculate distance")
    a=int(input("Enter 1 or 2    # "))
    if(a==1):
        print("your bin distance{} cm ".format(str(dusHeight)))
    else:
        find()

def thrd1():
    # print("thread 1 start")
    solaidOn()
   
    while True: 
        distances()
        if dusbinLevelInper==100:    
           mail()
           solanoidof()
           time.sleep(5)
           a=latitute
           b=langtitute
           h = geocoder.ip('me')
           new_a=h.lat
           new_b=h.lng
           if(new_a!=a or new_b!=b):
               print("bin is moved no problem")
               break
           else:
               mailHEIgher()
               break
        time.sleep(5)

def thrd2():
    while True:
        # print("thread 2 start")
        Temp()
        time.sleep(6)

def thrd3():
    while True:
            credentials = pika.PlainCredentials('admin', 'password')
            parameters = pika.ConnectionParameters(serverip,
                                       5672,                
                                       "/",
                                       credentials)

            conectn=pika.BlockingConnection(parameters)

            chanel=conectn.channel()

            chanel.queue_declare(queue='msgbox')
            messg="level {} temp {} humidy {} location {}".format(dusbinLevelInper,temperature,humidity,loation)
            chanel.basic_publish(exchange="",routing_key='msgbox',body=messg)

            # print("send msg=={}".format(messg))
            print("msg send to rabbitmq")

            time.sleep(7)

def thrd4():

    while True:
        # print("thrd 4 start")
        a= GPIO.input(pir)
        if a==1:
            print("\n\n waterflow present")
        elif a==0:
            print("\n\n no waterflow present")
        time.sleep(8)

if __name__ == "__main__":
       
    find()
    t1 = threading.Thread(target=thrd1, name='t1')
    t2 = threading.Thread(target=thrd2, name='t2')
    t3=threading.Thread(target=thrd3,name='t3')
    t4=threading.Thread(target=thrd4,name='t4')

    t1.start()
    t2.start()
    t3.start()
    t4.start()
