"""
configurations.py

This file is where configurations and validation checks are defined. Configurations are coupled together based on relevancy and stored as a python dictionary.
Makes for easy translation from a JSON formatted file using the json.dumps/loads methods. 
"""
import abc
import logging

from copy import deepcopy
from dl_mqtt_clients.func._general_func import _translate_mosq_protocol, _translate_ssl_protocol

class Config(metaclass=abc.ABCMeta):
		
    @property
    def _config():
        pass

    def __init__(self, c):
        self._config = {**self._config, **c}

    def _validate_config(self):
        pass

    def get_property(self, prop_name):
        return self._config.get(prop_name)
	
    def output_config(self):
        self._logger.info(self.__class__.__name__)
        for prop, val in self._config.items():
            self._logger.info('{}: {} ({})'.format(prop, val, type(val)))

class MQTTConnectionConfig(Config):
    _config = {'host': None,
               'port': None,
               'sub_topics': [None],
               'pub_topic': None,
               'ssl_protocol': None,
               'keepalive': None,
               'pub_qos': None,
               'mqtt_protocol': None,
               'ssl_cert_path': None
               }
    def __init__(self, c):
        super().__init__(c=c)
        self._logger = logging.getLogger(self.__class__.__name__) 
        if not self._validate_config():
            raise AssertionError
			
    def host(self):
        return self.get_property('host')
	
    def port(self):
        return self.get_property('port')
	
    def sub_topics(self):
        return self.get_property('sub_topics')
	
    def pub_topic(self):
        return self.get_property('pub_topic')
	
    def sslProto(self):
        return self.get_property('ssl_protocol')
	
    def keepalive(self):
        return self.get_property('keepalive')
	
    def subQos(self):
        return self.get_property('sub_qos')
		
    def pubQos(self):
        return self.get_property('pub_qos')
	
    def mqtt_protocol(self):
        return self.get_property('mqtt_protocol')

    def ssl_cert_path(self):
        return self.get_property('ssl_cert_path')

    def _validate_config(self):
        any_errors = False
        #type validation
        if not type(self.host())==str:
            self._logger.error("Invalid Type for Host Config")
            any_errors=True
        if not type(self.port())==int:
            self._logger.error("Invalid Type for Port")
            any_errors=True
        if not type(self.sub_topics())==list:
            self._logger.error("Invalid Type for sub_topics")
            any_errors=True
        if not type(self.pub_topic())==str:
            self._logger.error("Invalid Type for pub_topic")
            any_errors=True
        if not type(self.sslProto())==str:
            self._logger.error("Invalid Type for ssl_protocol")
            any_errors=True
        if not type(self.keepalive())==int:
            self._logger.error("Invalid Type for keepalive")
            any_errors=True
        if not type(self.pubQos())==int:
            self._logger.error("Invalid Type for pub_qos")
            any_errors=True
        if not type(self.subQos())==int:
            self._logger.error("Invalid Type for pub_qos")
            any_errors=True
        if not type(self.mqtt_protocol())==int:
            self._logger.error("Invalid Type for mqtt_protocol")
            any_errors=True	
        if any_errors:
            return not any_errors
		
        #value validation
        if not (self.pubQos()<=2 and self.pubQos()>=0):
            self._logger.error("Invalid value for pub_qos. Must be one of 0, 1, 2")
            any_errors=True
        if not (self.subQos()<=2 and self.subQos()>=0):
            self._logger.error("Invalid value for sub_qos. Must be one of 0, 1, 2")
            any_errors=True
        if not _translate_ssl_protocol(self.sslProto()):
            self._logger.error("Invalid value for SSL Protocol")
            any_errors=True
        if not _translate_mosq_protocol(self.mqtt_protocol()):
            self._logger.error("Invalid value for MQTT Protocol")
            any_errors=True
        return not any_errors

class KerasConfig(Config):
    _config = {'optimizer': None,
               'loss': None,
               'train_epochs': None,
               'train_bs': None,
               'early_stopping': None,
               'es_patience': None,
               'es_delta': None,
               'precision': None,
               'reduce_lr_on_plateau': None,
               'lr_patience': None,
               'lr_delta': None,
               'lr_cooldown': None,
               'min_lr': None
               }
    def __init__(self, c):
        super().__init__(c=c)
        self._logger = logging.getLogger(self.__class__.__name__) 
        if not self._validate_config():
            raise AssertionError("Error validating configuration")
			
    def optimizer(self):
        return self.get_property('optimizer')
    def loss(self):
        return self.get_property('loss')
    def train_epochs(self):
        return self.get_property('train_epochs')
    def train_bs(self): 
        return self.get_property('train_bs')
    def early_stopping(self):
        return self.get_property('early_stopping')
    def es_patience(self):
        return self.get_property('es_patience')
    def es_delta(self):
        return self.get_property('es_delta')
    def precision(self):
        return self.get_property('precision')
    def early_stopping(self):
        return self.get_property('reduce_lr_on_plateau')
    def reduce_lr_on_plateau(self):
        return self.get_property('reduce_lr_on_plateau')
    def lr_patience(self):
        return self.get_property('lr_patience')
    def lr_delta(self):
        return self.get_property('lr_delta')
    def lr_cooldown(self):
        return self.get_property('lr_cooldown')
    def min_lr(self):
        return self.get_property('min_lr')
    def _validate_config(self):
        any_errors = False
        #type checks
        if self.optimizer(): #optional
            if type(self.optimizer())!=str:
                self._logger.error("Optimizer must be of type str")
                any_errors=True
        if self.loss(): #optional
            if type(self.loss())!=str:
                self._logger.error("Loss must be of type str")
                any_errors=True
        if not type(self.train_epochs())==int:
            self._logger.error("Train epochs must be of type int")
            any_errors=True
        if not type(self.train_bs())==int:
            self._logger.error("Train batch size must be of type int")
            any_errors=True
        if not type(self.early_stopping())==bool:
            self._logger.error("Early stopping must be of type bool")
            any_errors=True
        if self.early_stopping() and type(self.es_patience())!=int:
            self._logger.error("Early stopping patience must be of type int")
            any_errors=True
        if self.early_stopping() and type(self.es_delta())!=float:
            self._logger.error("ES Delta must be of type float")
            any_errors=True
        if not type(self.precision())==int:
            self._logger.error("Precision must be of type int")
            any_errors=True
        if not type(self.reduce_lr_on_plateau())==bool:
            self._logger.error("Reduce Learning Rate on Plateau must be of type bool")
            any_errors=True
        if self.reduce_lr_on_plateau() and type(self.lr_patience())!=int:
            self._logger.error("Reduce Learaning Rate on Plateau Delta must be of type float")
            any_errors=True
        if self.reduce_lr_on_plateau() and type(self.lr_delta())!=float:
            self._logger.error("Learning Rate Delta must be of type float")
            any_errors=True
        if self.reduce_lr_on_plateau() and type(self.lr_cooldown())!=int:
            self._logger.error("Reduce Learaning Rate on Plateau Delta must be of type int")
            any_errors=True
        if self.reduce_lr_on_plateau() and type(self.min_lr())!=float:
            self._logger.error("Reduce Learaning Rate on Plateau minimum Learning Rate must be of type float")
            any_errors=True
        if any_errors:
            return not any_errors
        #value checks
        if self.precision() not in [4, 8, 16, 32]:
            self._logger.error("Precision parameter must be one of [4, 8, 16, 32]")
            any_errors=True
        if self.early_stopping():
            if self.es_patience() > self.train_epochs():
                self._logger.error("ES patience must be less than train epochs parameter")
                any_errors=True
        if self.train_bs() <= 0:
            self._logger.error("Batch size must be greater than zero")
            any_errors=True
		#TODO: check optimizer / loss
        return (not any_errors)

class ModelServerConfig(Config):
    _config = {'precision': None,
               'num_rounds': None,
               'prod_pub_topic': None,
               'model_cache_size': None,
               'merge_ratio': None}

    def __init__(self, c):
        super().__init__(c=c)
        self._logger = logging.getLogger(self.__class__.__name__)
        if not self._validate_config():
            raise AssertionError("Error validating configuration")

    def _validate_config(self):
        any_errors = False

        #type validation
        if type(self.precision()) != int:
            self._logger.error("Precision of incorrect type; required: int")
            any_errors = True
        if type(self.num_rounds()) != int:
            self._logger.error("Num rounds of incorret type; required: int")
            any_errors = True
        if type(self.prod_pub_topic()) != str:
            self._logger.error("prod_pub_topic incorrect type; required: str")
            any_errors = True
        if type(self.model_cache_size()) != int:
            self._logger.error("model_cache_size incorrect type; required: int")
            any_errors = True
        if type(self.merge_ratio()) != float:
            self._logger.error("merge_ratio incorrect type; required: float")
            any_errors = True
        if any_errors:
            return not any_errors

        #value check
        if self.num_rounds() < 1:
            self._logger.error("num_rounds param must be >= 1")
            any_errors = True
        if len(self.prod_pub_topic()) == 0:
            self._logger.error("prod_pub_topic must be non-empty str")
            any_errors = True
        if self.merge_ratio() > 1.0:
            self._logger.error("merge_ratio must fall in (0.0, 1.0]")
            any_errors= True
        if self.merge_ratio() <= 0.0:
            self._logger.error("merge_ratio must fall in (0.0, 1.0]")
            any_errors= True
        if self.model_cache_size() <= 0:
            self._logger.error("model_cache_size must be greater than 0")
            any_errors= True
        if self.precision() not in [4, 8, 16, 32]:
            self._logger.error("Precision parameter must be one of [4, 8, 16, 32]")
            any_errors=True

        return not any_errors
		
    def precision(self):
        return self.get_property('precision')

    def num_rounds(self):
        return self.get_property('num_rounds')
	
    def prod_pub_topic(self):
        return self.get_property('prod_pub_topic')

    def model_cache_size(self):
        return self.get_property('model_cache_size')
		
    def merge_ratio(self):
        return self.get_property('merge_ratio')