# bdt-final-project
Spark Streaming project using IoT Sensor Data

Took a permission to submit the final project in 2 days (09/28/2021). It will be updated shortly.


# miu-bdt-final-project

`IoT node -> MQTT Broker -> mqtt2kafka -> kafka -> spark -> hive`

- Author: Ganzorig Ulziibayar
- Course: Big Data Technology
- Professor: Mrudula Mukadam
- VIDEO LINK: 

This repo includes source of the final project implemented as a final project of CS523: Big Data Technology in Maharishi Internation University.


Topics:
* Overview
* Requirements
* Project detail

## Overview

IoT is said to be the next big like the internet in the past. There will be billions of devices connected. And it produces massive data. So in this project, I did proof of concept of how we can use apache spark to receive these iot data and process it to get some valuable insights. 

For this purpose, I have used raspberry pi as edge iot device which has IMU sensor reporting acceleration data in X, Y, Z directions. 

In short, data will flow in following manner.

IoT node -> MQTT Broker -> mqtt2kafka -> kafka -> spark -> hive

MQTT is the simple, lightweight tcp based protocol used for transferring data. Of course, we can add more security by using ssl, authorization using credentials. But for simplicity, I have ommitted security layer. MQTT operates very much similar to kafka. There is a concept publisher, subcriber. It is analogous to producer, consumer. And there is topic. 

> Spark Streaming - Earthquake analysis
I have depicted small diagram of how everything flows.

Project Parts:
- **`[1]`** Create your own project for Spark Streaming
- **`[2]`** Integrate Hive with Part 1
- **`[3]`** Create a simple demo project for any of the following tools: Kafka
- **`[4]`** Record a demo of your Presentation of all the above 3 parts.

Things completed here:
- **`[1]`** Real Sensor data is generated from Raspberry pi, and this data will be transferred to spark via MQTT broker, Kafka broker. And using this data, system will evaluate whether earthquake is happenning.
- **`[2]`** Result of the process is stored on `hive`.
- **`[3]`** Main project uses kafka.
- **`[4]`** [Recorded demo](https:example.com)

## Requirements

| Name | Version |
| - | - |
| Ubuntu | 20.04 |
| Python | 3.6.7 |
| Scala | 2.11.12 |
| Hadoop | 2.8.5 |
| Hive | 2.3.5 |
| Kafka (For Hadoop2) | 2.12 |
| Spark (For Hadoop2) | 3.1.1 |

Hardware requirements:
1. [Raspberry pi](https://www.raspberrypi.org/) 
2. [IMU Click Sensor](https://www.mikroe.com/6dof-imu-3-click)

Python requirements:

| Package | Version |
| - | - |
| pyspark | 3.7.12 |
| kafka-python | 2.0.2 |

Download spark streaming to kafka util from 
https://search.maven.org/search?q=a:spark-streaming-kafka-0-8-assembly_2.11

Hive Installer
http://archive.apache.org/dist/hive/hive-2.3.5/

Spark for Hadoop2
https://www.apache.org/dyn/closer.lua/spark/spark-3.1.2/spark-3.1.2-bin-hadoop2.7.tgz

Kafka:
https://kafka.apache.org/downloads

Hadoop2
https://hadoop.apache.org/release/2.8.5.html


## Project detail:
### Commands for start and stop services

Please make sure do following steps to run the project.

1. start kafka
```
sudo systemctl start kafka // stop
```

2. Create a Topic "sensors"
```
./kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic sensors
```

3. Check if it is created
```
kafka@ubuntu:~/kafka/bin$ ./kafka-topics.sh --list --bootstrap-server localhost:9092
__consumer_offsets
sensors
```

4. Start Hive MetaStore 
```
hive --service metastore
```

5. Create Hive Table
```
hive> CREATE TABLE sensors (text STRING, sentiment DOUBLE)
    > ROW FORMAT DELIMITED FIELDS TERMINATED BY '\\|'
    > STORED AS TEXTFILE;
```
### 

After this, our environment is ready. And we can start running our project code.

Firstly, iot sensor node code should run. 
```
python iot_sensor.py
```

As soon as you execute, following will be printed to console. These are acceleration value of X, Y, Z axis. `Connected to broker` means node is connected to MQTT broker running on the host PC and successfully publish data into topic `/sensor/1/get/`. Inside the topic, there is index 1 which identifies the actual node. There can be thousands of nodes.

```
pi@raspberrypi:~/projects/iot $ python iot_sensor.py
Connecting to Adafruit IO...
Connected to Broker! Listening for topic changes on /sensor/1/set
Acceleration (m/s^2): (0.266, 0.340, 10.083)
Sent!
Acceleration (m/s^2): (0.225, 0.306, 10.062)
Sent!
```
Note: each acceleration data is between -9.81 to 9.81. Our sensor has bit offset from manufacturing. When the sensor is stationary, Z acc is 10.062. if we tilt it sideways, X, Y acc will change. So based on this, we can do some transformation on the data, determine if there is earthquake happenning. 

Secondly, we need to inject this data into spark via kafka. mqtt2kafka.py script is written, so that i subscribes to topic /sensor/1/get/ and as soon as data arrives, it produces the message to kafka.

```
python3 mqtt2kafka.py
```

Afterwards, data is in the kafka, we can consume this data, do the proper transformation and store the result on the hive.

```
spark-submit --jars spark-streaming-kafka-0-8-assembly_2.11-2.4.8.jar consumer.py
```