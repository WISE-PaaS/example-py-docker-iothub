from flask import Flask, render_template
import json
import paho.mqtt.client as mqtt
import os


app = Flask(__name__)

# port from cloud environment variable or localhost:3000
port = int(os.getenv("PORT", 3000))

@app.route('/', methods=['GET'])
def root():

    if(port == 3000):
        return 'py-docker-iothub successful'
    elif(port == int(os.getenv("PORT"))):
        return render_template('index.html')

IOTHUB_SERVICE_NAME = 'p-rabbitmq'

# Get the environment variables
ENSAAS_SERVICES = os.getenv('ENSAAS_SERVICES')
ENSAAS_SERVICES_js = json.loads(ENSAAS_SERVICES)

# --- MQTT(rabbitmq) ---
credentials = ENSAAS_SERVICES_js[IOTHUB_SERVICE_NAME][0]['credentials']
mqtt_credential = credentials['protocols']['mqtt']

broker = mqtt_credential['host']
username = mqtt_credential['username'].strip()
password = mqtt_credential['password'].strip()
mqtt_port = mqtt_credential['port']

print(broker)
print(username)
print(password)
print(mqtt_port)

# mqtt connect
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("/hello")
    print('subscribe on /hello')

def on_message(client, userdata, msg):
    print(msg.topic+','+msg.payload.decode())

client = mqtt.Client()

client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, mqtt_port, 60)
client.loop_start()


if __name__ == '__main__':
    # Run the app, listening on all IPs with our chosen port number
    app.run(host='0.0.0.0', port=port)
