

#Ԥ This is OneNet MQTT class

from umqtt_simple import MQTTClient
from machine import Timer
import json

ip='183.230.40.39'
port=6002

class OneNetMQTT:
    global ip
    global port
    def __init__(self, dev_id,product_id, api_key,sub_cba):
        self.client=MQTTClient(dev_id,ip,port,product_id,api_key,0)
        self.client.set_callback(sub_cba)
        if (self.client.connect() == 1):
            print("Connect Server Success!")
            self.connect_flag=True
            self.client.subscribe(b"home_info_mqtt")
        else:
            print("Connect Server Fail!")
        
    def __deinit(self):
        if (self.connect_flag):
            self.client.disconnect()
            self.tim.deinit()
            print("Disconnect Server!")
        else:
            print("Nothing Done!")
            
    def start_heartbeat(self,timeout):
        self.tim=Timer(-1)
        self.tim.init(period=timeout,mode=Timer.PERIODIC,callback=lambda t:print(1))
        
    
# Received messages from subscriptions will be delivered to this callback
    def sub_cb(topic, msg):
        print((topic, msg))
        
        
    def publish3(self, msg):
        topic_name='$dp'
        stra=json.dumps(msg)
        #stra=str(msg)
        #print(str)
        newb=b'\x03\x00\x00'
        newba = bytearray(newb)
        newba[1] = (len(stra))>>8
        newba[2] = len(stra)
        newb=bytes(newba)+bytes(bytearray(stra))
        print(newb)
        self.client.publish(topic_name,newb)