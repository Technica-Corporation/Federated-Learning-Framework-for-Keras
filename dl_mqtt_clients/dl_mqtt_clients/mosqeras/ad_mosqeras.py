import numpy as np
import time
import threading
import sys
from dl_mqtt_clients.mosqeras import mosqeras
from dl_mqtt_clients.func._nn_func import normalize_data
from dl_mqtt_clients.func._ad_ae_func import reconstr_error

class predict_client(mosqeras.mosqeras):
    """Anomaly detection prediction client. Simply uses trained autoencoder to score incoming instances generating anomaly metric
    """
    def _preprocess(self, data):
        return normalize_data(np.array(data).astype(np.float), self.sk_scaler)

    def _postprocess(self, predicted, expected):
        return reconstr_error(predicted, expected)
	
    def _process_data(self, data):
        prepro_data = self._preprocess(data=data)
        #prepro_data = data
        _start_time = time.time()
        res = self.model.predict(data=prepro_data)
        self.logger.info("Model prediction finished in {} seconds".format(time.time()-_start_time))
        postpro_data = self._postprocess(res, prepro_data)
        #TODO: configurable output field name
        out_msg = self.serializer.serialize(data=postpro_data, output_field_name='anomaly_score')
        self.dataClient.publish_msg(formatted_msg=out_msg)

    def _check_cache(self):
        if len(self.data_cache) < self.cache_sz:            
            return
        self.logger.info("Data cache filled ({}), processing data ...".format(self.cache_sz))
        thread_data = self.data_cache.copy()
        self.data_cache = None
        threading.Thread(target = self._process_data, args = (thread_data,)).start()

    def _validate_configs(self):
        return True

class train_client(mosqeras.mosqeras):
    """Anomaly detection train client. Updates a model based on incoming streamed data. 	
    """
    train_config = None

    def set_train_config(self, c):
        self.train_config = c
	
    def _validate_configs(self):
        if self.train_config == None:
            raise AttributeError("Training Configuration not set, set using set_train_config()")
        self.train_config._validate_config()
	
    def _preprocess(self, data):
        return normalize_data(data=data, scaler=self.sk_scaler)

    def _postprocess(self):
        return

    def _process_data(self, data):
        prepro_data = self._preprocess(data=data)
        self.model.setup_train(early_stopping=self.train_config.early_stopping(), 
                               reduce_lr_on_plateau=self.train_config.reduce_lr_on_plateau(),
                               es_delta=self.train_config.es_delta(), 
                               es_patience=self.train_config.es_patience(),
                               lr_delta=self.train_config.lr_delta(), 
                               lr_patience=self.train_config.lr_patience(),
                               lr_cooldown=self.train_config.lr_cooldown(), 
                               min_lr=self.train_config.min_lr())
        _start_time = time.time()
        self.model.fit_model(train_data=prepro_data, labels=prepro_data, batch_size=self.train_config.train_bs(), epochs=self.train_config.train_epochs(), verbose=2)
        self.logger.info("Training Complete. Time Elapsed: {}s".format(time.time()-_start_time))
        self.dataClient.publish_msg(formatted_msg=self.model.serialize_model_weights(precision=self.train_config.precision()))

    def _check_cache(self):
        if len(self.data_cache) < self.cache_sz:
            return
        self._validate_configs()
        self.logger.info("Data cache filled ({}), processing data ...".format(self.cache_sz))
        thread_data = self.data_cache.copy()
        self.data_cache = None
        threading.Thread(target = self._process_data, args = (thread_data,)).start()