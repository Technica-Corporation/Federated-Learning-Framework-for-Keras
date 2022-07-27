import abc
import logging
import json
from dl_mqtt_clients.func._serializer_func import decode_bytestr_to_json
from dl_mqtt_clients.clients import _mosq_client

class microservice(object, metaclass=abc.ABCMeta):
    def __init__(self, mqtt_config, serializer=None, 
					       logger_name=None):
        """
        Initialization function for microservice

        Args:
            mqtt_config (MQTTConnectionConfig): MQTT Configuration Connection object for the data client, 
				        the client where the streamed data will be received
                
			      serializer (Serializer): Serializer, used to deserialize incoming MQTT payloads (exact usage undefined - 
                but should be specified to use in on_message callbacks)
                
		        logger_name (str) [Optional]: optionally pass in the name of which namespace the logger should run it, 
                otherwise will run in the class name space
        """
		#Data Structs
        self.dataClient = _mosq_client(mqtt_config, self._on_message)                
        self.serializer = serializer
        if logger_name:
            self.logger = logging.getLogger(logger_name)
        else:
            self.logger = logging.getLogger(__name__)

    def __del__(self):
        """
        Ensures that MQTT Connections are closed when object is destructed
        """
        self.shutdown()	

    def connect_clients(self):
        """
        Connects the data and configuration mqtt clients to their respective broker
        These client connect calls are asynchronous
        """
        try:
            self._validate()
        except Exception as e:
            self.logger.error("Error with validating configurations, client will not connect", exc_info=e)
            raise
        self.logger.info("Connecting data client")
        self.dataClient.connect_client()
        self.logger.info("Connecting config client")

    def shutdown(self):
        """
        Shuts down connections to broker for both data and config clients
        """
        try:
            self.dataClient.shutdown()
        except Exception as e:
            self.logger.error('Error shutting down data client', exc_info=e)
	
    @abc.abstractmethod
    def _on_message(self, client, userdata, msg):
        """
        Abstract method

        Define behavior on how to process incoming message
        """
        pass

    @abc.abstractmethod
    def _validate(self):
        """
        Abstract method

        Define behavior in order to validate data members of the class. 
        Should be called at the end of object initialization or during any object data member updates
        """
        pass