import paho.mqtt.client as mqtt
import random

# mqtt credentials in RabbitMQ
broker="rabbitmq-001-pub.hz.wise-paas.com.cn"
mqtt_port=1883
username="d34d32b7-5256-4c48-90b6-1cdc3cf2bd35:40741fb9-44e8-48ee-bf73-50cc1c6dcfea"
password="J9DeTWe30rizaK7lR9Ds"

# create function for callback
def on_publish(client,userdata,result):
    print("data published")

# create client object
client= mqtt.Client()       
# Set login account password
client.username_pw_set(username,password)
# assign function to callback
client.on_publish = on_publish               
# establish connection
client.connect(broker,mqtt_port)          
# Published topics and content
client.publish("/hello",random.randint(10,30))
