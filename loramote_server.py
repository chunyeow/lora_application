#!/usr/bin/python -u 
import socket
import json
import sys
import base64 
import paho.mqtt.client as mqtt
from Crypto.Cipher import AES
from datetime import tzinfo, timedelta, datetime 
execfile("loramote_msg2string.py")

# Application Session Key
APPSKEY="\x2b\x7e\x15\x16\x28\xae\xd2\xa6\xab\xf7\x15\x88\x09\xcf\x4f\x3d"
# Network Session Key
NETSKEY="\x2b\x7e\x15\x16\x28\xae\xd2\xa6\xab\xf7\x15\x88\x09\xcf\x4f\x3d"

UDP_IP = "127.0.0.1"
UDP_PORT = 1780

DIR=0 # UPLINK

def decrypt_appmsg(dev_addr, seq_nbr, appmsg):
    len_appmsg = len(appmsg) 
    msg_pad = bytearray(appmsg)
    if len_appmsg < 16:
        i = len(appmsg)
        while i < 16:
            msg_pad.append(0x0)
            i+=1
    
    aBlock = bytearray("\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00");

    aBlock[5] = int(DIR);

    aBlock[6] = (dev_addr) & 0xFF;
    aBlock[7] = (dev_addr  >> 8) & 0xFF;
    aBlock[8] = (dev_addr  >> 16) & 0xFF;
    aBlock[9] = (dev_addr  >> 24) & 0xFF;

    aBlock[10] = (seq_nbr) & 0xFF;
    aBlock[11] = (seq_nbr >> 8) & 0xFF;
    aBlock[12] = (seq_nbr >> 16) & 0xFF;
    aBlock[13] = (seq_nbr >> 24) & 0xFF;
    #aBlock[15] = 0;
    aBlock[15] = 1;
    
    IV = '\x00' * 16
    mode = AES.MODE_CBC
    decryptor = AES.new(str(APPSKEY), mode, IV=IV)
    sBlock = decryptor.encrypt(str(aBlock))
    sBlock_array = bytearray(sBlock)
    
    i = 0;
    unencryptedmsg = bytearray()
    while i < len_appmsg:
        unencryptedmsg.append(msg_pad[i] ^sBlock_array[i])
        i +=1
    return unencryptedmsg

def main():

    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))

    """
    Lora Packet GW-Server Bytes
    0 version = 1
    1-2random token
    3 PUSH_DATA identifier 0x00
    4-11 Gateway unique identifier (MAC address)
    12-end JSON object, starting with {, ending with }, see section 4

    Size (Bytes):     1      |   1 ~ M     |  4 
    PHY Payload	: MAC Header | MAC Payload | MIC
   
    Bit#	:     7..5     |    4..2   | 1..0
    MAC Header	: Message Type |    RFU    | Major

    Size (Bytes) :    7..23     |   0..1     |    0..N
    MAC Playload : Frame Header | Port Field | Frame Payload  

    * Port Field: 0 - Network Session Key; 1 - Application Session Key

    Size (Bytes) :       4        |       1       |       2       |     0..15
    Frame Header : Device Address | Frame Control | Frame Counter | Frame Options

    Size (Bytes)  :          7         |     6     |  5  |     4    |   3..0
    Frame Control : Adaptive Data Rate | ADRACKReq | ACK | FPending | FOptsLen 
    """
    print "Waiting LoRa messages ..."
    while True:
        data, addr = sock.recvfrom(4096) # buffer size is 1024 bytes 
        if len(data) > 12: 
            json_data = data[12:]
            ojson = json.loads(json_data)
            #print ojson
            try:
                for p in ojson["rxpk"]:
                    msg = base64.b64decode(p["data"])
		    #print msg
		    """
		    Confirm data
		    """
                    if msg.startswith("\x80") and len(msg) > 8:
                        #print "MAC MSG: ",
                        #for i in msg:
                        #    print "%02x" % (ord(i)),
                        #print "" 
                        byte_msg = bytearray(msg)
                        rx_dev_addr = (byte_msg[4] << 24) | (byte_msg[3] << 16) | byte_msg[2] << 8 | byte_msg[1]
                        seq_nbr =   byte_msg[7] << 8 | byte_msg[6]
                        appmsg = msg[9:-4]
                        #print "APP MSG: ", 
                        #for i in appmsg:
                        #    print "%02x" % (ord(i)),
                        #print "" 
                        fpappmsg = decrypt_appmsg(rx_dev_addr, seq_nbr, appmsg)
			#mqtt_msg = msg2string(str(fpappmsg))

			"""
			Get some valuable value
			"""
			ts = ojson['rxpk'][0]['time']
			rssi = ojson['rxpk'][0]['rssi']
			devaddr = struct.unpack("!BBBB", buffer(msg[1:5]))
			id = (devaddr[3] << 24) | (devaddr[2] << 16) | (devaddr[1] << 8) | devaddr[0]
			#print "Mote ID : %x" % id
			#print "TS: %s" % ts
			#print "RSSI: %s" % rssi
			mqtt_msg = "{\"Mote ID\":\"%x" % id + "\",\"ts\":\"%s" % ts + "\",\"RSSI\":\"%s" % rssi + msg2string(str(fpappmsg))
			
			#print mqtt_msg
			"""
			MQTT publishing
			"""
			mqttc = mqtt.Client("python_pub")
			mqttc.connect("10.44.39.155", 1883)
			mqttc.publish("lora/sensor", mqtt_msg)
			mqttc.loop(2)
            except:  
                print "Something went wrong!" 

if __name__ == "__main__":
    sys.exit(main())
