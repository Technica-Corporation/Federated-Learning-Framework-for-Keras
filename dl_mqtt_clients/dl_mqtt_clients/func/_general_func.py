import numpy as np
import paho.mqtt.client as mqtt
import ssl
import time

import logging

logging.basicConfig(level=logging.INFO)

def parse_json_field(values):
    """
    Takes a json value field and returns it as NumPy array to be used in Keras
    @params
    values (list / str): list or csv string of float values
    """
    if type(values) is list:
        data = [float(x) for x in values]
    elif type(values) is str:
        data = [float(x) for c in values]
    elif type(values) is dict:
        raise TypeError
        
    data = np.array(values)
    #expand dimensions to be batch_size, ndims or (1, ndims) since NeuralNets expect (batch_size, features) as input
    data = np.expand_dims(data, axis=0)
    return data

def utf8len(s):
    """Returns length of a string encoded in utf-8"""
    return len(s.encode('utf-8'))

def logging_format():
    """Returns a logging format to be used for logger module"""
    return '[%(asctime)s] %(name)s {%(filename)10s:%(lineno)3d} %(levelname)5s - %(message)s'

def simple_logging_format():
    """Returns a simplified logging format to be used for logger module"""
    return '[%(asctime)s] {%(filename)10s:%(lineno)3d} %(levelname)5s - %(message)s'

def get_time_unix():
    """Returns the unix time (rounded as an integer)"""
    return int(time.time())

def _translate_mosq_protocol(x):
    """Function that takes a integer value representing the protocol version (e.g. 311 is v3.11). 
           If invalid arg, returns None
       Args:
           x (int): version
       Returns:
           proto_string or None
    """
    mqtt_map = {
        311: mqtt.MQTTv311,
        31: mqtt.MQTTv31
    }
    if x in mqtt_map:
        return mqtt_map[x]
    else:
        return None

def _translate_ssl_protocol(x):
    """Function that takes a integer value representing the protocol version (e.g. 311 is v3.11)
       If invalid arg, returns None
       Args:
           x (str): ssl version
       Returns:
           proto_string or None
    """
    ssl_map = {
        'tls_12': ssl.PROTOCOL_TLSv1_2,
        'tls_1': ssl.PROTOCOL_TLSv1, 
        'tls_11': ssl.PROTOCOL_TLSv1_1,
        'None': 'None'
    }
    if x in ssl_map:
        return ssl_map[x]
    else:
        return None