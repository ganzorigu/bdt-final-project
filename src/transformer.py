#!/usr/bin/python3                                                                                                      

from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

def parse_value(text):
    acc = text.split(' ')
    acc[0] = int(float(acc[0])*100)
    acc[1] = int(float(acc[1])*100)
    acc[2] = int(float(acc[2])*100)

    
    if abs(acc[0]) > 500 or abs(acc[1]) > 500:
        print("Earthquake!...")

    my_tuple = (acc[0], acc[1], acc[2], acc[3]+" "+acc[4])
    
    return my_tuple

def handle_rdd(rdd):
    if not rdd.isEmpty():
        global ss
        df = ss.createDataFrame(rdd, schema=['x', 'y', 'z', 't'])
        df.show()
        df.write.saveAsTable(name='default.sensors', format='hive', mode='append')

sc = SparkContext(appName="Something")
ssc = StreamingContext(sc, 5)

ss = SparkSession.builder \
        .appName("Something") \
        .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
        .config("hive.metastore.uris", "thrift://localhost:9083") \
        .enableHiveSupport() \
        .getOrCreate()

ss.sparkContext.setLogLevel('WARN')

ks = KafkaUtils.createDirectStream(ssc, ['sensors'], {'metadata.broker.list': 'localhost:9092'})

lines = ks.map(lambda x: x[1])

# print(lines)
# transform = lines.map(lambda sensor: (sensor, int(len(tweet.split())), int(len(tweet))))
transform = lines.map(lambda sensor: parse_value(sensor))

transform.foreachRDD(handle_rdd)

ssc.start()
ssc.awaitTermination()