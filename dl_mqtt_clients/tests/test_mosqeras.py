import pytest
from dl_mqtt_clients import ad_mosqeras
from dl_mqtt_clients import KerasNN
from dl_mqtt_clients import configurations
import logging

mqtt_data_d = {'host': 'localhost','port': 1883,'sub_topics':['test'],'pub_topic':'output','ssl_protocol': 'tls_12','keepalive': 10,'sub_qos': 1,'pub_qos': 0,'mqtt_protocol': 311}
mqtt_config_d = {'host': 'localhost','port': 1883,'sub_topics':['update'],'pub_topic': '','ssl_protocol': 'tls_12','keepalive': 10,'pub_qos': 0,'sub_qos': 2,'mqtt_protocol': 311}
train_config_d = {'train_epochs': 3, 'train_bs': 4, 'early_stopping': False,'precision': 32}
def test_mosqeras():
	data_mqtt_c = configurations.MQTTConnectionConfig(c=mqtt_data_d)
	upd_mqtt_c = configurations.MQTTConnectionConfig(c=mqtt_config_d)
	k = KerasNN()
	m = ad_mosqeras.train_client(model = k, 
								   sk_scaler = None, 
								   data_mqtt_config = data_mqtt_c,
								   update_mqtt_config = upd_mqtt_c, 
								   serializer = None,
								   model_update_topic = 'update',
								   cache_sz = 5)

def test_train_update_config():
	data_mqtt_c = configurations.MQTTConnectionConfig(c=mqtt_data_d)
	upd_mqtt_c = configurations.MQTTConnectionConfig(c=mqtt_config_d)
	k_c = configurations.KerasConfig(c=train_config_d)
	n = KerasNN()
	m = ad_mosqeras.train_client(model = n, 
								sk_scaler = None, 
								data_mqtt_config = data_mqtt_c,
								update_mqtt_config = upd_mqtt_c, 
								serializer = None,
								model_update_topic = 'update',
								cache_sz = 5)
	m.set_train_config(k_c)
	sample_update_config = {'train_bs': 10}
	m._update_mqtt(sample_update_config)
	assert(m.train_config.train_bs()==10)