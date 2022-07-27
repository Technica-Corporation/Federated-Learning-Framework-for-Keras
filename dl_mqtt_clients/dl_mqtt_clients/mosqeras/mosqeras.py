import abc
import paho.mqtt.client as mqtt
import ssl
import logging
import json
import time
import numpy as np

from dl_mqtt_clients.microservice import microservice
from dl_mqtt_clients.func._general_func import parse_json_field
from dl_mqtt_clients.clients import _mosq_client
from dl_mqtt_clients import KerasNN


class mosqeras(microservice, metaclass=abc.ABCMeta):
    """mosquitto + keras base implementation with mqtt clients to handle config/model s

    Attributes:
        logger (logger): logging module for class instance
		    dataClient (_mosq_client, paho.mqtt.client): wrapper around mqtt client for data 
		    configClient (_mosq_client, paho.mqtt.client): wrapper around mqtt client for config updates
		    model (net.net): wrapped Keras model
		    sk_scaler (sklearn.preprocessing.scaler): preprocessing module
		    serializer (PayloadSerializer): Serializes / deserialzies data received
		    data_cache (list, numpy): data structure that caches data, cleared once processed
		
	  Args:
		    model (net.net): wrapped Keras model with convenience functions to run predictions on cached data
		    sk_scaler (sclearn.preprocessing.scaler): sklearn scaler that preprocessing data and scales it to match training cond.
		    mqtt_config (MQTTConnectionConfig): MQTT Connection Info for the data client. See configurations.py
		    serializer (PayloadSerializer): Payload serializer that transforms data received on the data / config client. Assumes both are same format.
		    model_update_topic (str): topic (on the broker listened to by the config client) from which model updates will be received from the server
		    cache_size (int): define the number of messages data to store before processing it with the model
    """
    #TODO:
    def _status(self):
        self.logger.info('Client Status')

    def _validate(self):
        assert(type(self.model_update_topic)==str)
        assert(len(self.model_update_topic) > 0)
        assert(type(self.model)==KerasNN) 

    def __init__(self, model, sk_scaler, mqtt_config, serializer, model_update_topic, cache_sz = 10):
        #MQTT Configs
        super().__init__(mqtt_config=mqtt_config, serializer=serializer)
        #General Properties
        self.cache_sz = cache_sz
        self.model_update_topic = model_update_topic
        self.dataClient.add_callback(self.model_update_topic, self._on_message_model_upd)
        self.model = model                  
        self.sk_scaler = sk_scaler
        self.serializer = serializer
        self.data_cache = None
        self._validate()
        self.logger.info("Created instance of Mosqeras. Cache Size: {}".format(cache_sz))

    def _on_message(self, client, userdata, msg):
        """
		    Flow through for data client MQTT message callback. Uses modules to deserialize messages

		    @param
		    client:
		    userdata:
		    msg:
		    """
        self.logger.debug("Message (sz: {}) received on topic: {}".format(len(msg.payload), msg.topic))
        self.logger.debug("Msg: {}".format(str(msg.payload)))
   
        try:
            json_d = self.serializer.deserialize(input=msg.payload)
        except json.decoder.JSONDecodeError:
            self.logger.error("Error decoding payload from bytes to json, attempting json.loads()")
      
        try:
            if json_d is None:
                json_d = json.loads(msg.payload)
        except json.decoder.JSONDecodeError:
            self.logger.error("Error decoding payload to json, ignoring...")
        
        data = parse_json_field(values=json_d["data"]) #TODO: make field configurable
        if self.data_cache is None:
            self.data_cache = data
        else:
            self.data_cache = np.append(self.data_cache, data, axis=0)
        self._check_cache()

    def _on_message_model_upd(self, client, userdata, msg):
        """
        MQTT Message callback for when msg is received on module update topic. Model serial/deserialization occurs via JSONPickle Library 
        """
        self.logger.info("[Model Update] Message (sz: {}) received on topic: {}".format(len(msg.payload), msg.topic))
        try:
            _weights = self.model.deserialize_json_weights(json_msg=msg.payload.decode('utf8'))
        except json.decoder.JSONDecodeError:
            self.logger.error("Error decoding payload from bytes to json, ignoring.. ")
            return
        self.model.update_weights(weights=_weights)

    @abc.abstractmethod
    def _preprocess(self):
        """
        Defines preprocessing behavior used in the check_cache method
        """
        pass
    @abc.abstractmethod
    def _postprocess(self):
        """
        Defines postprocessing of results used in the check_cache method
        """
        pass
    @abc.abstractmethod
    def _check_cache(self):
        """
        Defines the behavior to happen to the data at the end of each message callbacks. 
        Implementation typically compares to the data cache size of the service and triggers behavior if filled
        """
        pass
    @abc.abstractmethod
    def _validate_configs(self):
        pass
