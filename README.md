# Example-py-docker-ioyhub

- [1. Introduction](#1-introduction)
- [2. Environment](#2-environment)
- [3. Downloading the Project](#3-Downloading-the-project)
- [4. Deploy the app to HZ.WISE-PaaS](#4-deploy-the-app-to-hzwise-paas)
- [5. Application Introduce](#5-application-introduce)
  - [5-1. index.py](#5-1-indexpy)
  - [5-2. publisher.py](#5-2-publisherpy)
  - [5-3. SSO (Single Sign On)](#5-3-sso-single-sign-on)
- [6. Kubernetes Config](#6-kubernetes-config)
  - [6-1. deployment.yaml](#6-1-deploymentyaml)
  - [6-2. ingress.yaml](#6-2-ingressyaml)
  - [6-3. service.yaml](#6-3-serviceyaml)
- [7. Docker](#7-docker)
  - [7-1. dockerfile](#7-1-dockerfile)
- [8.Deployment Application Steps](#8deployment-application-steps)
  - [8-1. build Docker image](#8-1-build-docker-image)
  - [8-2. push it to Docker Hub](#8-2-push-it-to-docker-hub)
  - [8-3. create kubernetes object ( All object are in the k8s folder)](#8-3-create-kubernetes-object--all-object-are-in-the-k8s-folder)
  - [8-4. Check（Pod status is running for success）](#8-4-checkpod-status-is-running-for-success)
  - [8-5. Run publisher.py](#8-5-run-publisherpy)

## 1. Introduction

This is WIES-PaaS Iothub example-code include the sso and rabbitmq service，and we use the Docker package this file。

## 2. Environment

[Python3](https://www.python.org/downloads/) （ need include pip3 ）

    #mqtt
    pip3 install paho-mqtt
    #python-backend
    pip3 install Flask

[Docker](https://www.docker.com/get-started) ( Use to packaged our application )

## 3. Downloading the Project

    git clone https://github.com/WISE-PaaS/example-py-docker-iothub.git

## 4. Deploy the app to HZ.WISE-PaaS

[HZ.WISE-PaaS](https://portal-mp-ensaas.hz.wise-paas.com.cn/namespace-info/workloads)

- Cluster：eks006
  - Workspace：advtraining
    - Namespace：level1

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
        return 'hello world! i am in the local'
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
    $ kubectl get secret --namespace=level1

![getSecret](https://tva1.sinaimg.cn/large/007S8ZIlgy1gilmywhphbj326m0a6tiu.jpg)

    # Watch ENSAAS_SERVICES
    $ kubectl get secret {py-level1-secret} --namespace=level1 -o yaml

![-oyaml](https://tva1.sinaimg.cn/large/007S8ZIlgy1gilmhaf21jj326c0panpd.jpg)

    # Decode ENSAAS_SERVICES
    $ kubectl get secret {py-level1-secret} --namespace=level1 -o jsonpath="{.data.ENSAAS_SERVICES}" | base64 --decode; echo

![-ojsonpath](https://tva1.sinaimg.cn/large/007S8ZIlgy1gilmpj2gk8j326c0pau0x.jpg)

Copy decode data to vscode and Save as **json** file

![-ojsonpath](https://tva1.sinaimg.cn/large/007S8ZIlgy1giln7ute9aj30n50r9n33.jpg)

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

- bokrer:"ENSAAS_SERVICES => p-rabbitmq => externalHosts"
- port :"ENSAAS_SERVICES => p-rabbitmq => mqtt => port"
- username :"ENSAAS_SERVICES => p-rabbitmq => mqtt => username"
- password: "ENSAAS_SERVICES => p-rabbitmq => mqtt => password"

### 5-3. SSO (Single Sign On)

This is the [sso](https://advantech.wistia.com/medias/vay5uug5q6) applicaition，open **`templates/index.html`** and editor the `ssoUrl` to your application name，
If you don't want it，you can ignore it。

    #change this **`python-demo-try`** to your **application name**
    var ssoUrl = myUrl.replace('python-demo-try', 'portal-sso');

## 6. Kubernetes Config

### 6-1. deployment.yaml

Each user needs to adjust the variables for certification, as follows：

6-1. metadata >> name：py-docker-iothub-**{user_name}** 2. student：**{user_name}** 3. image：**{docker_account}** / py-docker-iothub：latest 4. containerPort：listen 3000 5. env >> valueFrom >> secretRef >> name：Fill in the secret name in the corresponding space
![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlgy1gimrc1gddcj31fh0u07fw.jpg)
**Notice：In Portal-Services secret name**
![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlgy1gimn6nv1s3j31jx0u0dof.jpg)

### 6-2. ingress.yaml

**Ingress Layout**
![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlgy1gimveupn90j31bc0fwmz6.jpg)

Each user needs to adjust the variables for certification, as follows：

1. metadata >> name：py-docker-iothub-**{user_name}**
2. host：py-docker-iothub-**{user_name}** . **{namespace_name}** . **{cluster_name}**.en.internal
3. serviceName：need to be same name in cluster-ip.yaml **metadata name**
4. servicePort：need to be same name in cluster-ip.yaml **port**
   ![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlgy1gimqrv8uu4j324u0pq0za.jpg)

### 6-3. service.yaml

Each user needs to adjust the variables for certification, as follows：

1. metadata >> name：server-**{user_name}**
2. student：**{user_name}**
3. port：listen 3344
4. targetPort：need to be same port in deployment.yaml **containerPort**
   ![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlgy1gimr7hcbojj324u0l6wj8.jpg)

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

![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlgy1gilnq5u7qaj318g05ygpf.jpg)

### 8-4. Check（Pod status is running for success）

    $ kubectl get all --namespace=level1

![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlgy1gilnsphz69j313m0cyqbe.jpg)

### 8-5. Run publisher.py

**Open two terminal first.**

    # 1. Send message to application in WISE-PaaS
    python publisher.py

![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlgy1gilnwgivrrj318803amys.jpg)

    # 2. Listen the console
    kubectl logs -f pod/{pod_name}

![createSecret](https://tva1.sinaimg.cn/large/007S8ZIlgy1gilnv93ttpj311c0fcqbd.jpg)
