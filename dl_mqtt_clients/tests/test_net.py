from tensorflow import keras
from dl_mqtt_clients import KerasNN
import numpy as np
import pytest
import logging

INPUT_DATA_SHAPE = 24

def build_model():
	input_layer = keras.layers.Input(shape=(INPUT_DATA_SHAPE,))
	encoded = keras.layers.Dense(12, activation='relu')(input_layer)
	encoded = keras.layers.Dense(8, activation='relu')(encoded)
	encoded = keras.layers.Dense(4, activation='relu')(encoded)
	decoded = keras.layers.Dense(8, activation='relu')(encoded)
	decoded = keras.layers.Dense(12, activation='relu')(encoded)
	decoded = decoded = keras.layers.Dense(INPUT_DATA_SHAPE, activation='sigmoid')(decoded)
	autoencoder = keras.models.Model(input_layer, decoded)
	autoencoder.compile(optimizer='adam', loss='mae')
	return autoencoder

@pytest.mark.serialize
def test_serialize_net():
	model = build_model()
	kNN = KerasNN()
	kNN.set_model(keras_model=model)
	orig_weights = kNN.model.get_weights()
	weights = kNN.serialize_model_weights(precision=8)
	assert(type(weights)==str)

@pytest.mark.serialize
def test_deserialize_8bit():
	model = build_model()
	kNN = KerasNN()
	kNN.set_model(keras_model=model)
	orig_weights = kNN.model.get_weights()
	weights = kNN.serialize_model_weights(precision=8)
	ds_weights = kNN.deserialize_json_weights(json_msg=weights)
	assert(len(ds_weights)==len(orig_weights))

@pytest.mark.serialize
def test_deserialize_float():
	model = build_model()
	kNN = KerasNN()
	kNN.set_model(keras_model=model)
	orig_weights = kNN.model.get_weights()
	weights = kNN.serialize_model_weights(precision=32)
	ds_weights = kNN.deserialize_json_weights(json_msg=weights)
	assert(len(ds_weights)==len(orig_weights))
	for i in range(len(ds_weights)):
		assert(ds_weights[i].all()==orig_weights[i].all())

@pytest.mark.init
def test_set_model():
	batch_size = 124
	model = build_model()
	kNN = KerasNN()
	kNN.set_model(keras_model=model)
	data = np.random.randn(batch_size, INPUT_DATA_SHAPE)
	kNN.predict(data)

@pytest.mark.init
def test_fit_model():
	batch_size = 124
	model = build_model()
	kNN = KerasNN()
	kNN.set_model(keras_model=model)
	data = np.random.randn(batch_size, INPUT_DATA_SHAPE)
	kNN.fit_model(train_data=data, labels=data, batch_size=4, epochs=10, verbose=0)

@pytest.mark.init
def test_update_weights():
	model = build_model()
	kNN = KerasNN()
	kNN.set_model(keras_model=model)

	new_weights = [np.random.randn(3, 10) for i in range(7)]
	assert(not kNN.update_weights(new_weights))
	new_weights = [np.random.randn(*i.shape) for i in model.get_weights()]
	assert(kNN.update_weights(new_weights))