import paho.mqtt.client as mqtt
import random

broker="rabbitmq-001-pub.hz.wise-paas.com.cn"
mqtt_port=1883
username="d34d32b7-5256-4c48-90b6-1cdc3cf2bd35:40741fb9-44e8-48ee-bf73-50cc1c6dcfea"
password="J9DeTWe30rizaK7lR9Ds"

def on_publish(client,userdata,result):             #create function for callback
    print("data published")

client= mqtt.Client()                           #create client object
client.username_pw_set(username,password)
client.on_publish = on_publish                          #assign function to callback
client.connect(broker,mqtt_port)                                 #establish connection
client.publish("/hello",random.randint(10,30))
