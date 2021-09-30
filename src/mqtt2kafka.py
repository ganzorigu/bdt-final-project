#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from kafka import KafkaProducer 
from time import sleep 
import sys 

from datetime import datetime

BROKER = 'localhost:-9092'                                                                         
TOPIC = 'sensors' 

# This is the Subscriber
count = 0

try:                                                                                                                    
    p = KafkaProducer(bootstrap_servers=BROKER)                                                                         
except Exception as e:                                                                                                  
    print(f"ERROR --> {e}")                                                                                             
    sys.exit(1)
    
def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe("/sensor/1/get")

def on_message(client, userdata, msg):
	global count	
	# current date and time
	timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	tempString = msg.payload.decode() + " " + timestamp
	print(tempString)

	p.send(TOPIC, bytes(tempString, encoding="utf8"))
	count = count + 1
	if count >= 50:
		print("client will disconnect")
		client.disconnect()
    
client = mqtt.Client()
client.connect("192.168.0.112",1883,60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
