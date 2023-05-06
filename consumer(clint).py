import pika

import time

def on_msgReceived(ch,method,properties,body):
    
    file1 = open("myfile.txt", "a")
    file1.write("\n")
    file1.write(str(body))
    time.sleep(2)

credentials = pika.PlainCredentials('admin', 'password')
parameters = pika.ConnectionParameters('localhost',
                                       5672,
                                       '/',
                                       credentials)


conectn=pika.BlockingConnection(parameters)
chanel=conectn.channel()

chanel.queue_declare(queue='msgbox')

chanel.basic_consume(queue='msgbox',auto_ack=True,
                     on_message_callback=on_msgReceived)

print("start consuming")

chanel.start_consuming()