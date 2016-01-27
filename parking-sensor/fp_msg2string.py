#Check results of packet from MOTA with thresholds
import logging
import struct

def get_occ_state(state):
    ret = "---"
    if state == 0:
        ret = "FREE"
    elif state == 1:
        ret = "OCCUP"
    elif state == 2:
        ret = "INDET"
    return ret

def get_occ_event(msg):
    unp_msg = struct.unpack("!BBH", msg)
    occ_event_str = get_occ_state(unp_msg[0]) + "\",\"Event\":\"" + str(unp_msg[1]) + "\",\"Pre Event Time\":\"" + str(unp_msg[2])
    return occ_event_str

def get_type_msg_str(msg_type, msg):
    if msg_type == 3:
        type_msg_str = "\",\"Occ State\":\"" + get_occ_event(msg)

    return type_msg_str


def msg2string(msg):

    msg_str = ""

    try:
        unp_header_and_type = struct.unpack("!BBBBB", buffer(msg[:5]))
        if (unp_header_and_type[0] & 0xC0) != 0xC0:
            logging.error("Invalid header")
        else:
            mote_id = ((unp_header_and_type[0] & 0x3F) << (8+8+2)) | (unp_header_and_type[1] << (8+2)) | (unp_header_and_type[2] << 2) | (unp_header_and_type[3] >> 6)
            num_seq = unp_header_and_type[3] & 0x3F
            type_msg_str = get_type_msg_str(unp_header_and_type[4], buffer(msg[5:]))
	    msg_str = "{\"Mote ID\":\"" + str(mote_id) + "\",\"Seq\":\"" + str(num_seq) + type_msg_str

    except struct.error:
        print "ERROR unpacking message"
        logging.error("Parsing msg")
        msg_str=""
        for i in msg:
            msg_str+= "%02x " % (ord(i))
        logging.debug(msg_str)

    return msg_str

