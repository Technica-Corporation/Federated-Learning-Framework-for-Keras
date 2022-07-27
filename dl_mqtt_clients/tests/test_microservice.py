from dl_mqtt_clients.func._general_func import simple_logging_format
from dl_mqtt_clients.microservice import microservice
from dl_mqtt_clients import configurations
from dl_mqtt_clients.payload_serializers.JSONSerializer import JSONSerializer
import mock 
import pytest
from pytest_mock import mocker 
import logging
import random, string, json
logging.basicConfig(format=simple_logging_format, level=logging.INFO)
logger = logging.getLogger()

microservice.__abstractmethods__ = frozenset()

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

def test_init(mqtt_config_d):
	"""tests passing None for serialier on init"""
	m = microservice(data_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					update_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					serializer=None)

def test_init_serializer(mqtt_config_d):
	"""tests passing a serializer on init"""
	m = microservice(data_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
						update_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
						serializer=JSONSerializer())

def test_init_non_configuration_obj_1(mqtt_config_d):
	"""tests passing a non MQTTConnectionConfig object to data_mqtt_config param"""
	with pytest.raises(AssertionError):
		m = microservice(data_mqtt_config=mqtt_config_d, 
						update_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
						serializer=None)

def test_init_non_configuration_obj_2(mqtt_config_d):
	"""tests passing a non MQTTConnectionConfig object to update_mqtt_config param"""
	with pytest.raises(AssertionError):
		m = microservice(data_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d),
						update_mqtt_config=mqtt_config_d, 
						serializer=None)

def test_init_logger_name(mqtt_config_d):
	"""tests the init parameter for logger_name"""
	name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
	m = microservice(data_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					update_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					serializer=None,
					logger_name=name)
	assert(name == m.logger.name)

def test_update(mqtt_config_d, mocker):
	"""tests the update mqtt method by generating random port to update"""
	m = microservice(data_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					update_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					serializer=None)
	update_port = random.randint(1000, 9999)
	mocker.patch.object(m.dataClient.client, 'reconnect')
	m._update_mqtt(update_d = {"port": update_port})
	assert(m.dataClient.mqtt_config.port()==update_port)

def test_update_bad_val(mqtt_config_d, mocker):
	"""tests a bad type update"""
	m = microservice(data_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					update_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					serializer=None)
	prev_port = m.dataClient.mqtt_config.port()
	update_port = random.randint(1000, 9999)
	#mocker.patch.object(m.dataClient.client, 'reconnect')
	m._update_mqtt(update_d = {"port": str(update_port)})
	assert(m.dataClient.mqtt_config.port()== prev_port)

def test_on_msg_update(mqtt_config_d, mocker):
	"""tests the update_mqtt call of the microservice class"""
	update_port = random.randint(1000, 9999)
	class msg:
		def __init__(self):
			self.payload = json.dumps({'port': update_port}).encode('utf-8')
			self.topic = "my/sub/topic"
	m = microservice(data_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					update_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					serializer=None)
	myMsg = msg()
	mocker.patch.object(m.dataClient.client, 'reconnect')
	m._on_message_topic_upd(client=None, userdata=None, msg=myMsg)
	assert(m.dataClient.mqtt_config.port()==update_port)

def test_on_msg_update_bad_json(mqtt_config_d, mocker):
	"""tests the on_message_upd method of the microservice class, ensuring it can properly decode utf8 encoded strings"""
	class msg:
		def __init__(self):
			self.payload = "{inval: json".encode('utf-8')
			self.topic = "my/sub/topic"
	m = microservice(data_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					update_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					serializer=None)
	myMsg = msg()
	prev_port = m.dataClient.mqtt_config.port()
	mocker.patch.object(m.dataClient.client, 'reconnect')
	m._on_message_topic_upd(client=None, userdata=None, msg=myMsg)
	assert(prev_port==m.dataClient.mqtt_config.port())

def test_connect_clients(mqtt_config_d, mocker):
	"""tests the logic for connecting clients"""
	m = microservice(data_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					update_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					serializer=None)
	mocker.patch.object(m.dataClient, 'connect_client')
	mocker.patch.object(m.configClient, 'connect_client')
	m.connect_clients()

def test_connect_clients_valid_error(mqtt_config_d, mocker):
	"""tests to see client connecting with a validation error occuring during _validate"""
	m = microservice(data_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					update_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					serializer=None)
	mocker.patch.object(m, '_validate', side_effect=AssertionError)
	with pytest.raises(AssertionError):
		m.connect_clients()

def test_on_message_abstract(mqtt_config_d):
	"""simply tests if on_message method is callable"""
	m = microservice(data_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					update_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					serializer=None)
	m._on_message(client=None, userdata=None, msg=None)

def test_validate(mqtt_config_d):
	"""simply testsw if _validate method is callable"""
	m = microservice(data_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					update_mqtt_config=configurations.MQTTConnectionConfig(mqtt_config_d), 
					serializer=None)
	m._validate()