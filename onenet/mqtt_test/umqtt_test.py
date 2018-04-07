#mqtt test

import time
from umqtt_simple import MQTTClient

# Publish test messages e.g. with:
# mosquitto_pub -t foo_topic -m hello
Client_ID='28368380'
USER='127931'
PASSWD='oCK5MpA0TVP6E=Um8fYVe3zjack='
Data_ID='$dp'
cnt = 25.0

# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    print((topic, msg))

def main(server="localhost"):
    global cnt
    c = MQTTClient(Client_ID, server,6002,USER,PASSWD)
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(b"home_info_mqtt")
    while True:
        if False:
            # Blocking wait for message
            c.wait_msg()
        else:
            # Non-blocking wait for message
            c.check_msg()
            # Test
            cnt = cnt + 0.5
            send_data=b'\x01\x00\x00{\"datastreams\":[{\"id\":\"Temperature\",\"datapoints\":[{\"value\":'+str(cnt)+'}]}]}'
            send_d = bytearray(send_data)
            send_d[1]=(len(send_data)-3)>>8
            send_d[2]=(len(send_data)-3)
            send_data=bytes(send_d)
            #print(send_data)
            c.publish(Data_ID, send_data)
            # Then need to sleep to avoid 100% CPU usage (in a real
            # app other useful actions would be performed instead)
            time.sleep(1)

    c.disconnect()

main('183.230.40.39')


