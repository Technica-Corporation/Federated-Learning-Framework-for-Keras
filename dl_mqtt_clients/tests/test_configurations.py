from dl_mqtt_clients import configurations
from dl_mqtt_clients.func._general_func import logging_format
import pytest
import logging
from copy import deepcopy
logging.basicConfig(format=logging_format(), level=logging.INFO)

@pytest.fixture(scope='session')
def mqtt_config_d():
	mqtt_config_d = {'host': 'localhost',
					'port': 1883,
					'sub_topics':['model_update'],
					'pub_topic':'global/model',
					'ssl_protocol': 'tls_12',
					'keepalive': 10,
					'sub_qos': 1,
					'pub_qos': 0,
					'mqtt_protocol': 311}
	return mqtt_config_d

@pytest.mark.config
def test_valid_keras_config():
	d = {'optimizer': 'adadelta',
		'loss': 'binary_crossentropy',
		'train_epochs': 10,
		'train_bs': 32,
		'early_stopping': True,
		'es_patience': 3,
		'es_delta': 0.01, 
		'precision': 8
		}
	k_c = configurations.KerasConfig(d)
	k_c._validate_config()

@pytest.mark.config
def test_valid_mqtt_config():
	d = {'host': 'localhost',
		 'port': 1883,
		 'sub_topics':['model_update'],
		 'pub_topic':'global/model',
		 'ssl_protocol': 'tls_12',
		 'keepalive': 10,
		 'sub_qos': 1,
		 'pub_qos': 0,
		 'mqtt_protocol': 311}
	m_c = configurations.MQTTConnectionConfig(d)
	m_c._validate_config()

@pytest.mark.config
def test_invalid_mqtt_config():
	d = {'host': 'localhost',
		 'port': 'test',
		 'sub_topics':['model_update'],
		 'pub_topic':'global/model',
		 'ssl_protocol': 'tls_12',
		 'keepalive': 10,
		 'sub_qos': 3,
		 'pub_qos': 0,
		 'mqtt_protocol': 311}
	with pytest.raises(AssertionError):
		m_c = configurations.MQTTConnectionConfig(d)


@pytest.mark.config
def test_invalid_mqtt_protocol():
	d = {'host': 'localhost',
		 'port': 3000,
		 'sub_topics':['model_update'],
		 'pub_topic':'global/model',
		 'ssl_protocol': 'tls_12',
		 'keepalive': 10,
		 'sub_qos': 0,
		 'pub_qos': 0,
		 'mqtt_protocol': 300}
	with pytest.raises(AssertionError):
		m_c = configurations.MQTTConnectionConfig(d)

@pytest.mark.config
def test_invalid_ssl_config():
	d = {'host': 'localhost',
		 'port': 3000,
		 'sub_topics':['model_update'],
		 'pub_topic':'global/model',
		 'ssl_protocol': 'tls_20',
		 'keepalive': 10,
		 'sub_qos': 0,
		 'pub_qos': 0,
		 'mqtt_protocol': 311}
	with pytest.raises(AssertionError):
		m_c = configurations.MQTTConnectionConfig(d)

@pytest.mark.config
def test_invalid_type_host(mqtt_config_d):
	d = deepcopy(mqtt_config_d)
	d['host'] = 'localhost'.encode('utf8')
	with pytest.raises(AssertionError):
		configurations.MQTTConnectionConfig(d)

@pytest.mark.config
def test_invalid_type_port(mqtt_config_d):
	d = deepcopy(mqtt_config_d)
	d['port'] = '1883'
	with pytest.raises(AssertionError):
		configurations.MQTTConnectionConfig(d)

@pytest.mark.config
def test_invalid_type_subt(mqtt_config_d):
	d = deepcopy(mqtt_config_d)
	d['sub_topics'] = 'topic/1,topic/2,topic/3'
	with pytest.raises(AssertionError):
		configurations.MQTTConnectionConfig(d)


@pytest.mark.config
def test_invalid_type_pubt(mqtt_config_d):
	d = deepcopy(mqtt_config_d)
	d['pub_topic'] = 'topic/1'.encode('utf8')
	with pytest.raises(AssertionError):
		configurations.MQTTConnectionConfig(d)


@pytest.mark.config
def test_invalid_type_sslproto(mqtt_config_d):
	d = deepcopy(mqtt_config_d)
	d['ssl_protocol'] = 12
	with pytest.raises(AssertionError):
		configurations.MQTTConnectionConfig(d)


@pytest.mark.config
def test_invalid_type_keepalive(mqtt_config_d):
	d = deepcopy(mqtt_config_d)
	d['keepalive'] = '30'
	with pytest.raises(AssertionError):
		configurations.MQTTConnectionConfig(d)


@pytest.mark.config
def test_invalid_type_pubqos(mqtt_config_d):
	d = deepcopy(mqtt_config_d)
	d['pub_qos'] = '3'
	with pytest.raises(AssertionError):
		configurations.MQTTConnectionConfig(d)


@pytest.mark.config
def test_invalid_type_subqos(mqtt_config_d):
	d = deepcopy(mqtt_config_d)
	d['sub_qos'] = '3'
	with pytest.raises(AssertionError):
		configurations.MQTTConnectionConfig(d)

@pytest.mark.config
def test_invalid_type_mqttpro(mqtt_config_d):
	d = deepcopy(mqtt_config_d)
	d['mqtt_protocol'] = '3'
	with pytest.raises(AssertionError):
		configurations.MQTTConnectionConfig(d)

@pytest.mark.config
def test_invalid_val_pubqos(mqtt_config_d):
	d = deepcopy(mqtt_config_d)
	d['pub_qos'] = 3
	with pytest.raises(AssertionError):
		configurations.MQTTConnectionConfig(d)
	d['pub_qos'] = -1
	with pytest.raises(AssertionError):
		configurations.MQTTConnectionConfig(d)

@pytest.mark.config
def test_invalid_val_subqos(mqtt_config_d):
	d = deepcopy(mqtt_config_d)
	d['sub_qos'] = 3
	with pytest.raises(AssertionError):
		configurations.MQTTConnectionConfig(d)
	d['sub_qos'] = -1
	with pytest.raises(AssertionError):
		configurations.MQTTConnectionConfig(d)

@pytest.mark.config
def test_valid_server_config():
	d = {'precision': 32,
		 'num_rounds': 1,
		 'prod_pub_topic': 'model',
		 'model_cache_size': 100,
		 'merge_ratio': 0.4}
	s_c = configurations.ModelServerConfig(d)
	s_c._validate_config()

@pytest.mark.config
def test_invalid_server_config():
	orig_d = {'precision': 32,
		 'num_rounds': 1,
		 'prod_pub_topic': 'model',
		 'model_cache_size': 100,
		 'merge_ratio': 0.4}
	new_d = orig_d
	new_d['precision'] = 5
	with pytest.raises(AssertionError):
		s_c = configurations.ModelServerConfig(new_d)
	new_d = orig_d
	new_d['num_rounds'] = 0
	with pytest.raises(AssertionError):
		s_c = configurations.ModelServerConfig(new_d)
	new_d = orig_d
	new_d['num_rounds'] = 0.4
	with pytest.raises(AssertionError):
		s_c = configurations.ModelServerConfig(new_d)
	new_d = orig_d
	new_d['model_cache_size'] = -1
	with pytest.raises(AssertionError):
		s_c = configurations.ModelServerConfig(new_d)
	new_d = orig_d
	new_d['model_cache_size'] = 'string'
	with pytest.raises(AssertionError):
		s_c = configurations.ModelServerConfig(new_d)
	new_d = orig_d
	new_d['prod_pub_topic'] = ''
	with pytest.raises(AssertionError):
		s_c = configurations.ModelServerConfig(new_d)

def test_update_config_no_update():
	d = {'host': 'localhost',
		 'port': 11,
		 'sub_topics':['model_update'],
		 'pub_topic':'global/model',
		 'ssl_protocol': 'tls_12',
		 'keepalive': 10,
		 'sub_qos': 2,
		 'pub_qos': 0,
		 'mqtt_protocol': 311}
	m_c = configurations.MQTTConnectionConfig(d)
	update_d = { 'irrel_val': 10 }
	ret = m_c.update_config(update_d)
	assert(not ret)

def test_update_config_update():
	d = {'host': 'localhost',
		 'port': 11,
		 'sub_topics':['model_update'],
		 'pub_topic':'global/model',
		 'ssl_protocol': 'tls_12',
		 'keepalive': 10,
		 'sub_qos': 2,
		 'pub_qos': 0,
		 'mqtt_protocol': 311}
	m_c = configurations.MQTTConnectionConfig(d)
	update_d = { 'pub_topic': 'new/topic/pub' }
	ret = m_c.update_config(update_d)
	assert(ret)
	assert(m_c.pub_topic()==update_d['pub_topic'])

def test_update_config_inval_type():
	d = {'host': 'localhost',
		 'port': 11,
		 'sub_topics':['model_update'],
		 'pub_topic':'global/model',
		 'ssl_protocol': 'tls_12',
		 'keepalive': 10,
		 'sub_qos': 2,
		 'pub_qos': 0,
		 'mqtt_protocol': 311}
	m_c = configurations.MQTTConnectionConfig(d)
	update_d = { 'pub_topic': 11 }
	ret = m_c.update_config(update_d)
	assert(not ret)
	assert(m_c.pub_topic()==d['pub_topic'])

def test_update_config_inval_type2():
	d = {'host': 'localhost',
		 'port': 11,
		 'sub_topics':['model_update'],
		 'pub_topic':'global/model',
		 'ssl_protocol': 'tls_12',
		 'keepalive': 10,
		 'sub_qos': 2,
		 'pub_qos': 0,
		 'mqtt_protocol': 311}
	m_c = configurations.MQTTConnectionConfig(d)
	update_d = { 'port': '11' }
	ret = m_c.update_config(update_d)
	assert(not ret)
	assert(m_c.port()==d['port'])

def test_update_config_inval_val():
	d = {'host': 'localhost',
		 'port': 11,
		 'sub_topics':['model_update'],
		 'pub_topic':'global/model',
		 'ssl_protocol': 'tls_12',
		 'keepalive': 10,
		 'sub_qos': 2,
		 'pub_qos': 0,
		 'mqtt_protocol': 311}
	m_c = configurations.MQTTConnectionConfig(d)
	update_d = { 'mqtt_protcol': 322}
	ret = m_c.update_config(update_d)
	assert(not ret)
	assert(m_c.mqtt_protocol()==d['mqtt_protocol'])