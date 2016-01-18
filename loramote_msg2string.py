#Check results of packet from MOTA with thresholds
import logging
import struct

def msg2string(msg):

    msg_str = ""

    try:
	print "Frame Payload: "
	for i in msg:
           print "%02x" % (ord(i)),
        print ""
	
	"""
	LED [1] : 0 OFF 1 ON
	Pressure [2] : hPa/10
	Temperature [2] : degree celcius * 100
	Altitude (Barometric) [2] :  
	Battery [1]
	GPS Latitude & Longitude [6]
	GPS Altitude [2]
	"""
	led = struct.unpack("!B", buffer(msg[:1]))[0]
	pressure = struct.unpack("!H", buffer(msg[1:3]))[0]
	temperature = struct.unpack("!h", buffer(msg[3:5]))[0]
	altitude = struct.unpack("!h", buffer(msg[5:7]))[0]
	battery = struct.unpack("!B", buffer(msg[7:8]))[0]
	data = struct.unpack("!BBB", buffer(msg[8:11]))
	gps_latitude = (data[0] << 16) | (data[1] << 8) | data[2]
	data = struct.unpack("!BBB", buffer(msg[11:14]))
	gps_longitude = (data[0] << 16) | (data[1] << 8) | data[2]
	gps_altitude = struct.unpack("!h", buffer(msg[14:16]))[0]
	pressure = float(pressure) * 10	
	temperature = float(temperature) / 100
	altitude = float(altitude) / 10
	#print "LED: %d" % led
	#print "Air Pressure: %.2f hPa" % pressure
	#print "Temperature: %.2f degree celsius" % temperature
	#print "Altitude: %.1f m" % altitude
	#print "Battery Level: %d" % battery
	#print "GPS latitude: %d" % gps_altitude
	#print "GPS longitude: %d" % gps_longitude
	#print "GPS altitude: %d m" % gps_altitude

	"""
	msg_string in JSON
	"""
	#msg_str = "{\"LED\":\"%d" % led + \
	#	"\",\"Air Pressure\":\"%.2f" % pressure + \
	#	"\",\"Temperature\":\"%.2f" % temperature + \
	#	"\",\"Altitude\":\"%.1f" % altitude + \
	#	"\",\"Battery\":\"%d" % battery + \
	#	"\",\"GPS Latitude\":\"%d" % gps_latitude + \
	#	"\",\"GPS Longitude\":\"%d" % gps_longitude + \
	#	"\",\"GPS Altitude\":\"%d" % gps_altitude + "\"}"
	msg_str = "\",\"LED\":\"%d" % led + \
		"\",\"Air Pressure\":\"%.2f" % pressure + \
		"\",\"Temperature\":\"%.2f" % temperature + \
		"\",\"Altitude\":\"%.1f" % altitude + \
		"\",\"Battery\":\"%d" % battery + \
		"\",\"GPS Latitude\":\"%d" % gps_latitude + \
		"\",\"GPS Longitude\":\"%d" % gps_longitude + \
		"\",\"GPS Altitude\":\"%d" % gps_altitude + "\"}"

	#print msg_str

    except struct.error:
        print "ERROR unpacking message"
        logging.error("Parsing msg")
        msg_str=""
        for i in msg:
            msg_str+= "%02x " % (ord(i))
        logging.debug(msg_str)

    return msg_str

