# Example-py-docker-iothub

## 1. Introduction

This sample code shows how to deploy an application to the EnSaaS 4.0 environment and send messages to WISE-PaaS via Iot Hub (MQTT) by the platform.

## 2. Before You Start

1. Create a [Docker](https://www.docker.com/get-started) Account
2. Development Environment
   - Install [Docker](https://docs.docker.com/install/)
   - Install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

## 3. Downloading the Project

    git clone https://github.com/WISE-PaaS/example-py-docker-iothub.git

## 4. Deploy the app to WISE-PaaS

WISE-PaaS has 2 types of data centers
**SA DataCenter**：[https://portal-mp-ensaas.sa.wise-paas.com/](https://portal-mp-ensaas.sa.wise-paas.com/)

- **Cluster**：eks004
  - **Workspace**：adv-training
    - **Namespace**：level2

**HZ DataCenter**：[https://portal-mp-ensaas.hz.wise-paas.com.cn/](https://portal-mp-ensaas.hz.wise-paas.com.cn/)

- **Cluster**：eks006
  - **Workspace**：advtraining
    - **Namespace**：level2

## 5. Application Introduce

### 5-1. index.py

Simply backend application。

```py
app = Flask(__name__)

# port from cloud environment variable or localhost:3000
port = int(os.getenv("PORT", 3000))


@app.route('/', methods=['GET'])
def root():

    if(port == 3000):
        return 'py-docker-iothub successful'
    elif(port == int(os.getenv("PORT"))):
        return render_template('index.html')
```

This is the mqtt connect config code，`ENSAAS_SERVICES` can get the application environment in WISE-PaaS。

```py
ENSAAS_SERVICES = os.getenv('ENSAAS_SERVICES')
ENSAAS_SERVICES_js = json.loads(ENSAAS_SERVICES)
#Unified service_name is p-rabbitmq
service_name = 'p-rabbitmq'
broker = ENSAAS_SERVICES_js[service_name][0]['credentials']['protocols']['mqtt']['host']
username = ENSAAS_SERVICES_js[service_name][0]['credentials']['protocols']['mqtt']['username'].strip()
password = ENSAAS_SERVICES_js[service_name][0]['credentials']['protocols']['mqtt']['password'].strip()
mqtt_port = ENSAAS_SERVICES_js[service_name][0]['credentials']['protocols']['mqtt']['port']
#Print the connection information
print(broker)
print(username)
print(password)
print(mqtt_port)
```

Check mqtt connection follow as step：

    # View existing secret_name or create new one in level1
    $ kubectl get secret --namespace=level2

![getSecret](https://tva1.sinaimg.cn/large/007S8ZIlgy1gisgbotnq5j31he0aq16b.jpg)

    # Watch ENSAAS_SERVICES
    $ kubectl get secret {secret_name} --namespace=level2 -o yaml

![-oyaml](https://tva1.sinaimg.cn/large/007S8ZIlgy1gisgbzbywvj31hc0ase11.jpg)

    # Decode ENSAAS_SERVICES
    $ kubectl get secret {secret_name} --namespace=level2 -o jsonpath="{.data.ENSAAS_SERVICES}" | base64 --decode; echo

![-ojsonpath](https://tva1.sinaimg.cn/large/007S8ZIlgy1gisge03b13j31hg0as4m7.jpg)

Copy decode data to vscode and Save as **json** file

![copyDataVS](https://tva1.sinaimg.cn/large/007S8ZIlgy1gisgz87rmqj30ky0f0te0.jpg)

**Notice:You can create new secret by yourself**

![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlgy1gilndil2pnj31jz0u0478.jpg)

This code can connect to IohHub，if it connect successful `on_connect` will print successful result and subscribe topic `/hello`，you can define topic by yourself，and when we receive message `on_message` will print it。

```py
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
```

### 5-2. publisher.py

This file can help us publish message to topic。

Edit the **publisher.py** `broker、port、username、password` you can find in **ENSAAS_SERVICES**

- bokrer："ENSAAS_SERVICES => p-rabbitmq => externalHosts"
- port :"ENSAAS_SERVICES => p-rabbitmq => mqtt => port"
- username :"ENSAAS_SERVICES => p-rabbitmq => mqtt => username"
- password: "ENSAAS_SERVICES => p-rabbitmq => mqtt => password"

![publisher](https://tva1.sinaimg.cn/large/007S8ZIlgy1gish55bh5nj318v0u0qg3.jpg)

## 6. Kubernetes Config

### 6-1. deployment.yaml

Each user needs to adjust the variables for certification, as follows：

1. metadata >> name：py-docker-iothub-**{user_name}**
2. student：**{user_name}**
3. image：**{docker_account}** / py-docker-iothub：latest
4. containerPort：listen 3000
5. env >> valueFrom >> secretRef >> name：Fill in the same secret name in portal-services in your own space

![deployment](https://tva1.sinaimg.cn/large/007S8ZIlgy1gishcm30kxj30li0f0n15.jpg)
**Notice：In Portal-Services secret name**
![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlly1gishp9o8q5j30qo09ignf.jpg)

### 6-2. ingress.yaml

**Ingress Layout**
![ingress Layout](https://tva1.sinaimg.cn/large/007S8ZIlgy1gimveupn90j31bc0fwmz6.jpg)

Each user needs to adjust the variables for certification, as follows：

1. metadata >> name：py-docker-iothub-**{user_name}**
2. host：py-docker-iothub-**{user_name}** . **{namespace_name}** . **{cluster_name}**.en.internal
3. serviceName：need to be same name in Service.yaml **{metadata name}**
4. servicePort：same **port** in Service.yaml
   ![ingress](https://tva1.sinaimg.cn/large/007S8ZIlly1gisijjbk4wj31lo0tcjyt.jpg)

### 6-3. service.yaml

Each user needs to adjust the variables for certification, as follows：

1. metadata >> name：server-**{user_name}**
2. student：**{user_name}**
3. port：same **{port}** in ingress.yaml
4. targetPort：same **{port}** in deployment.yaml **{containerPort}**
   ![service](https://tva1.sinaimg.cn/large/007S8ZIlly1gisiuqi48sj31lc0p644c.jpg)

## 7. Docker

### 7-1. dockerfile

We first download the python:3.6 and copy this application to `/app`，and install library define in `requirements.txt`

```
FROM python:3.6-slim
WORKDIR /app
ADD . /app
RUN pip3 install -r requirements.txt
EXPOSE 3000
CMD ["python", "-u", "index.py"]
```

## 8.Deployment Application Steps

### 8-1. build Docker image

Adjust to your docker account

    $ docker build -t {docker_account / py-docker-iothub：latest} .

### 8-2. push it to Docker Hub

    $ docker push {docker_account / py-docker-iothub：latest}

The above steps are successful, docker hub will have this image [Docker Hub](https://hub.docker.com/)

![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlgy1gilnlaywu4j31jz0u07bl.jpg)

### 8-3. create kubernetes object ( All object are in the k8s folder)

    $ kubectl apply -f k8s/

![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlly1gisjkzn4kuj31je05ydkl.jpg)

### 8-4. Check（Pod status is running for success）

    # grep can quickly find key words
    $ kubectl get all --namespace=level2 | grep py

![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlly1gisjlrdqb1j31la06wdlv.jpg)

### 8-5. Run publisher.py

**Open two terminal first.**

    # 1. Listen the console
    kubectl logs -f pod/{pod_name}

![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlly1gisjrxecukj31js0ha15s.jpg)

    # 2. Send message to application in WISE-PaaS
    python publisher.py

![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlly1gisjseghnwj31jq03oacg.jpg)
