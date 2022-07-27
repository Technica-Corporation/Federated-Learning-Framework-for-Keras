from dl_mqtt_clients.func._general_func import simple_logging_format
from dl_mqtt_clients.clients import _mosq_client
from dl_mqtt_clients import configurations
import mock 
import pytest
from pytest_mock import mocker 
import logging
logging.basicConfig(format=simple_logging_format, level=logging.INFO)
logger = logging.getLogger()


@pytest.fixture(scope='session')
def mqtt_config_d():
	mqtt_config_d = {'host': 'localhost',
					'port': 1883,
					'sub_topics':['topic/1', 'topic/2', 'topic/3'],
					'pub_topic':'global/model',
					'ssl_protocol': 'tls_12',
					'keepalive': 10,
					'sub_qos': 1,
					'pub_qos': 0,
					'mqtt_protocol': 311}
	return mqtt_config_d

def test_init(mqtt_config_d):
	mqtt_config = configurations.MQTTConnectionConfig(mqtt_config_d)
	client = _mosq_client(config=mqtt_config)

def test_init_bad_type(mqtt_config_d):
	mqtt_config = configurations.MQTTConnectionConfig(mqtt_config_d)
	with pytest.raises(AssertionError):
		client = _mosq_client(config={})

def test_status(mqtt_config_d):
	mqtt_config = configurations.MQTTConnectionConfig(mqtt_config_d)
	client = _mosq_client(config=mqtt_config)
	client.status()

def test_on_connect(mqtt_config_d, mocker):
	mqtt_config = configurations.MQTTConnectionConfig(mqtt_config_d)
	client = _mosq_client(config=mqtt_config)
	mocker.patch.object(client.client, 'connect_async', return_value=True)
	client.connect_client()

def test_on_connect_connnect_refuse(mqtt_config_d, mocker):
	mqtt_config = configurations.MQTTConnectionConfig(mqtt_config_d)
	client = _mosq_client(config=mqtt_config)
	mocker.patch.object(client.client, 'connect_async', side_effect=ConnectionRefusedError)
	with pytest.raises(ConnectionRefusedError):
		client.connect_client()

def test_on_connect_callback(mqtt_config_d, mocker):
	mqtt_config = configurations.MQTTConnectionConfig(mqtt_config_d)
	client = _mosq_client(config=mqtt_config)
	mocker.patch.object(client.client, 'subscribe')
	client._on_connect(client=None, userdata=None, flags=None, rc=0)
	same_vals = set(client.topic_callback_map.keys()) & set(mqtt_config_d['sub_topics'])
	assert(len(same_vals)==len(mqtt_config_d['sub_topics']))

def test_on_connect_callback_error_subscribe(mqtt_config_d, mocker):
	mqtt_config = configurations.MQTTConnectionConfig(mqtt_config_d)
	client = _mosq_client(config=mqtt_config)
	mocker.patch.object(client.client, 'subscribe', side_effect=[Exception, None, None])
	client._on_connect(client=None, userdata=None, flags=None, rc=0)
	same_vals = set(client.topic_callback_map.keys()) & set(mqtt_config_d['sub_topics'])
	assert(len(same_vals)+1==len(mqtt_config_d['sub_topics']))

def test_set_default_callback(mqtt_config_d):
	mqtt_config = configurations.MQTTConnectionConfig(mqtt_config_d)
	def my_function(client, userdata, msg):
		return True
	client = _mosq_client(config=mqtt_config)
	client._set_default_callback(my_function)
	assert(client.client.on_message.__name__=='my_function')

def test_update_config(mqtt_config_d, mocker):
	mqtt_config = configurations.MQTTConnectionConfig(mqtt_config_d)
	client = _mosq_client(config=mqtt_config)
	mocker.patch.object(client.client, 'reconnect', return_value=True)
	client.update_config(config={'port': 3333})
	assert(client.mqtt_config.port()==3333)

def test_update_inval_type(mqtt_config_d):
	mqtt_config = configurations.MQTTConnectionConfig(mqtt_config_d)
	client = _mosq_client(config=mqtt_config)
	client.update_config(config={'port': '3334'})
	client.mqtt_config.output_config()
	assert(client.mqtt_config.port()==mqtt_config_d['port'])


def test_update_config_error_reconnect(mqtt_config_d, mocker):
	mqtt_config = configurations.MQTTConnectionConfig(mqtt_config_d)
	client = _mosq_client(config=mqtt_config)
	mocked_reconn = mocker.patch.object(client.client, 'reconnect', side_effect=Exception)
	mocked_reconn.assert_any_call
	client.update_config(config={'port': 3333})

	
def test_publish_msg(mqtt_config_d, mocker):
	mqtt_config = configurations.MQTTConnectionConfig(mqtt_config_d)
	client = _mosq_client(config=mqtt_config)
	mocker.patch.object(client.client, 'publish', return_value=True)
	client.publish_msg(formatted_msg='{test:value}', pub_topic='test')