from dl_mqtt_clients.clients import _mosq_client
from dl_mqtt_clients.net.net import SerializableWeights
from dl_mqtt_clients.func._nn_func import getMinMaxVals, compress_keras_weights, inflate_keras_weights, is_weight_list_same_dim, merge_models
import logging
import numpy as np
import json
import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy
import time
import threading
from typing import List, Set, Dict, Tuple, Optional
jsonpickle_numpy.register_handlers()

logger = logging.getLogger(__name__)

class ModelAggregator():
    """
    MQTT Application that reads Keras Weights over MQTT then aggregates them based on class parameters

    Attributes
        weight_cache (list): cached weights that trigger behavior when filled (e.g. >= server_config.model_cache_size())

    Args:
        mqtt_config (MQTTConnectionConfig): MQTT Connection info parameters. See configurations.py
        server_config (ServerConfig): Server configuration parameters. See configurations.py
    """
    def __init__(self, model, mqtt_config, server_config, status_update_topic):
        self.server_config = server_config
        self.mqtt_config = mqtt_config
        self.status_update_topic = status_update_topic	
        self.model = model
        self.model_client = _mosq_client(config=mqtt_config, on_message_callb=self.on_message_model)
		
        #data struct
        self.weight_cache = []
        self._round_counter = 0
        self._time_last_model_received = time.time()

    def _publish_status_update(self, json_d: Dict):
        if self.status_update_topic:
            logger.debug('sending status update to topic: {}'.format(self.status_update_topic))
            self.model_client.publish_msg(formatted_msg=json.dumps(json_d), pub_topic=self.status_update_topic)
        else:
            logger.warning('status_update_topic not set ({}) no messages will be sent'.format(self.status_update_topic))
        return

    def _run_merge_models(self):
        """
        Merges a ratio of models from the model cache 
        """	
        _nModelsMerge = round(self.server_config.merge_ratio() * len(self.weight_cache))
        _index = np.random.choice(len(self.weight_cache), _nModelsMerge, replace=False)
        _merged_model = merge_models(weights=[self.weight_cache[i] for i in _index])
        logger.debug("Running merge models on indexes: {}".format(_index))
        return _merged_model
		
    def check_cache(self):
        """
        Runs everytime a message is processed and cached. Checks to see if cache size is sufficient enough to begin processing
        """
        _pubModel = None
        #check cache fill
        if self.server_config.model_cache_size() <= len(self.weight_cache):
            _pubModel = self._run_merge_models()
            self._publish_status_update(json_d={'mode': 3, 'color': 'yellow', 'percent': 0})
            logger.debug("Serializing model weights")
            _min, _max = getMinMaxVals(_pubModel)
            s = SerializableWeights(keras_weights=_pubModel, precision=self.server_config.precision(), minV=_min, maxV=_max)
            logger.info("Publishing model weights and clearing weight cache (round {} of {})".format(self._round_counter+1, self.server_config.num_rounds()))
            self._round_counter += 1
            if self._round_counter >= self.server_config.num_rounds():
                self.model_client.publish_msg(formatted_msg=jsonpickle.encode(s), pub_topic=self.server_config.prod_pub_topic())
                self._publish_status_update(json_d={'mode': 3, 'color': 'all', 'percent': 0})
                self._round_counter = 0
            else:
                self.model_client.publish_msg(formatted_msg=jsonpickle.encode(s))
                self._publish_status_update(json_d={'mode': 3, 'color': 'green', 'percent': 0})
                
                _weights = []
                for layer in _pubModel:
                    _weights.append(np.copy(layer).astype('float32'))
                   
                logger.info("Updating Server Model Weights")
                try:
                    self.model.update_weights(weights=_weights)
                except Exception as e:
                    logger.info(e)
            self.weight_cache = []
        else:
            logger.debug('Checked cache: cache not filled yet')
        return
		
    def _validate_configs(self):
        pass

    def connect_clients(self):
        try:
            self._validate_configs()
        except AttributeError:
            logger.error("Error with validating configurations, client will not connect")
            raise
        self.model_client.connect_client()

    def shutdown(self):
        self.model_client.shutdown()

    def on_message_model(self, client, userdata, msg):
        """
        Defines behavior when messages are received; expects update
        """
        logger.info("Message (sz: {}) received on topic: {}".format(len(msg.payload), msg.topic))
        logger.debug("Msg: {}".format(str(msg.payload)))
        _serialW = jsonpickle.decode(msg.payload.decode('utf8'))
        if not isinstance(_serialW, SerializableWeights):
            raise TypeError("Deserialized object is not of instance Serializable Weights: {}".format(type(_serialW)))
        try:
            _serialW._validate()
        except AssertionError:
            raise TypeError("Error validating deserialized weight types")
        if _serialW.precision != 32:
            _weights = inflate_keras_weights(keras_weights=_serialW.weights, minV=_serialW.minV, maxV=_serialW.maxV, base_precision=_serialW.precision)
        else:
            _weights = _serialW.weights
        self.weight_cache.append(_weights)
        percent_complete = (len(self.weight_cache)/(self.server_config.model_cache_size()))*100
        logger.info("Weights deserialized and cached. Current Cache: {}. Max:{}".format(len(self.weight_cache), self.server_config.model_cache_size()))
        self._publish_status_update(json_d={'mode': 2, 'color': 'red', 'percent': percent_complete})
        threading.Thread(target=self.check_cache()).start()
