# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import board
import adafruit_fxos8700
### Secrets File Setup ###

try:
    from secrets import secrets
except ImportError:
    print("Connection secrets are kept in secrets.py, please add them there!")
    raise

# Setup topic to publish data 
topic_pub = "/sensor/1/get"

# Setup a feed named 'onoff' for subscribing to changes
topic_sub = "/sensor/1/set"

### Code ###

# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print("Connected to Broker! Listening for topic changes on %s" % topic_sub)
    # Subscribe to all changes on the onoff_feed.
    client.subscribe(topic_sub)


def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from Broker!")


def message(client, topic, message):
    # This method is called when a topic the client is subscribed to
    # has a new message.
    print("New message on topic {0}: {1}".format(topic, message))


# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=secrets["broker"],
    port=1883,
    username=secrets["user"],
    password=secrets["pass"],
    socket_pool=socket,
)

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = adafruit_fxos8700.FXOS8700(i2c,0x1e)

# Setup the callback methods above
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message

# Connect the client to the MQTT broker.
print("Connecting to Adafruit IO...")
mqtt_client.connect()

while True:
    # Poll the message queue
    mqtt_client.loop()

    # Read acceleration & magnetometer.
    accel_x, accel_y, accel_z = sensor.accelerometer

    print(
        "Acceleration (m/s^2): ({0:0.3f}, {1:0.3f}, {2:0.3f})".format(
            accel_x, accel_y, accel_z
        )
    )

    mqtt_client.publish(topic_pub, "{0:0.3f} {1:0.3f} {2:0.3f}".format(
	    accel_x, accel_y, accel_z
	)
    )
    print("Sent!")
    time.sleep(1)

