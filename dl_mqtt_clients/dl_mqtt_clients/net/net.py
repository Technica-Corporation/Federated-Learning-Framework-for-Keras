from tensorflow import keras
import tensorflow as tf
import numpy as np
import logging
import threading
import sys
import abc
from dl_mqtt_clients.func._nn_func import getMinMaxVals, compress_keras_weights, inflate_keras_weights, is_weight_list_same_dim
import logging

import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy
jsonpickle_numpy.register_handlers()

def print_keras_model_summary(model):
    model.summary()
    print("Inputs: {}".format(model.input_shape))
    print("Outputs: {}".format(model.output_shape))
    return

class SerializableWeights():
    def __init__(self, keras_weights, precision, minV, maxV):
        self.weights = keras_weights
        self.precision = precision
        self.minV = minV
        self.maxV = maxV
        self._validate()

    def _validate(self):
        if type(self.weights) != list:
            raise TypeError("Weights type not valid")
        if type(self.precision)!=int:
            raise TypeError("Precision type not valid")
        if type(self.minV)!= (np.float32 or float):
            raise TypeError("min type not valid")
        if type(self.maxV)!= (np.float32 or float):
            raise TypeError("max type not valid")
        return True

class NeuralNet(metaclass=abc.ABCMeta):
    def __init__(self):
        pass

    @property
    def model(self):
        """Neural Network Model, typically of shape (batch_size, dimension1, dimensions2, etc.)"""
        pass
    @property
    def logger(self):
        pass
    @property
    def inputShape(self):
        pass
    def outputShape(self):
        pass

    @abc.abstractmethod
    def load_model(self):
        pass
    @abc.abstractmethod
    def predict(self, data):
        pass


class KerasNN(NeuralNet):
    model = None
    logger = logging.getLogger(__name__)
    inputShape = None
    outputShape = None
    _callbacks_list = []
    lock = None

    def __init__(self):
        self.lock = threading.Lock()
		
	
    def load_model(self, hdf5_filename):
        try: 
            self.model = keras.models.load_model(hdf5_filename)
            self.inputShape, self.outputShape = self.model.input_shape, self.model.output_shape
            self.logger.info('Input Shape: {}, Output Shape: {}'.format(self.inputShape, self.outputShape))
            self.logger.info('Loaded model from disk')
            self.model.make_predict_function()
        except OSError:
            self.logger.error('Cannot load file: {}'.format(hdf5_filename))
            sys.exit(1)

    def update_weights(self, weights):
        self.logger.info("Starting to update weights!")
        if is_weight_list_same_dim(self.model.get_weights(), weights):	
            try:
                self.model.set_weights(weights)	
                return True
            except Exception as e:
                self.logger.info(e)
            try:
                self.model.set_weights(weights[0])	
                return True
            except Exception as e:
                self.logger.info(e)
        else:
            self.logger.error("On updating weights: dimensions do not match")
            return False
		
    def set_model(self, keras_model):
        self.model = keras_model
        self.inputShape, self.outputShape = self.model.input_shape, self.model.output_shape
        self.logger.info('Input Shape: {}, Output Shape: {}'.format(self.inputShape, self.outputShape))
        self.model.make_predict_function()

    def serialize_model_weights(self, precision):		
        _min, _max = getMinMaxVals(self.model.get_weights())
        if precision != 32:
            _weights = compress_keras_weights(keras_weights=self.model.get_weights(), precision=precision, minW=_min, maxW=_max)
        else:
           _weights = []
           for layer in self.model.get_weights():
               _weights.append(np.copy(layer).astype('float32'))
        serialW = SerializableWeights(keras_weights=_weights, precision=precision, minV=_min, maxV=_max)
        encoded = jsonpickle.encode(serialW)
        return encoded
	
    def deserialize_json_weights(self, json_msg):
        _serialW = jsonpickle.decode(json_msg)
        if not isinstance(_serialW, SerializableWeights):
            raise TypeError("Deserialized object is not of instance Serializable Weights: {}".format(type(_serialW)))
        try:
            _serialW._validate()
        except AssertionError:
            raise TypeError("Error validating deserialized weight types")
        if _serialW.precision != 32:
            _infaltedW = inflate_keras_weights(keras_weights=_serialW.weights, minV=_serialW.minV, maxV=_serialW.maxV, base_precision=_serialW.precision)
            return _infaltedW
        else:
            normalized_weights = []
            for layer in _serialW.weights:
                normalized_weights.append(np.copy(layer).astype('float32'))
            return normalized_weights
		
    def predict(self, data):
        if not data.shape[1:]==self.inputShape[1:]:
            raise ValueError("Data shape doesn't match networks expected input shape: {}, {}".format(data.shape[1:], self.inputShape[1:]))
        self.lock.acquire()
        results = self.model.predict(data, batch_size=32)
        self.lock.release()
        return results
	
    def setup_train(self, 
                    early_stopping, 
                    reduce_lr_on_plateau,
                    es_delta=None, 
                    es_patience=None,
                    lr_patience=None,
                    lr_delta=None,
                    lr_cooldown=None,
                    min_lr=None):
                    
        if early_stopping:
            es_callback = keras.callbacks.EarlyStopping(monitor='loss', min_delta=es_delta, patience=es_patience, verbose=0, mode='auto')           
            self._callbacks_list.append(es_callback)
        if reduce_lr_on_plateau:
            reduce_lr_callback = keras.callbacks.ReduceLROnPlateau(monitor='loss', min_delta=lr_delta, patience=lr_patience, cooldown=lr_cooldown, min_lr=min_lr, mode='auto')
            self._callbacks_list.append(reduce_lr_callback)
        return None
	
    def fit_model(self, train_data, labels, batch_size, epochs, verbose):
        if not train_data.shape[1:]==self.inputShape[1:]:
            raise ValueError("Data shape doesn't match networks expected input shape: {}, {}".format(train_data.shape[1:], self.inputShape[1:]))
        if not labels.shape[1:]==self.outputShape[1:]:
            raise ValueError("Data shape doesn't match networks expected input shape: {}, {}".format(labels.shape[1:], self.outputShape[1:]))
        self.lock.acquire()
        self.logger.info(self.model.fit(train_data, labels, batch_size=batch_size, epochs=epochs, verbose=verbose, callbacks=self._callbacks_list))
        self.logger.info('Done fitting model to data')
        self.lock.release()
        
    def save_model(self, filePath):
        self.model.save(f"{filePath}/model.h5")
		
