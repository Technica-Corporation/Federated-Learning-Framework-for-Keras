import json
import pytest
from dl_mqtt_clients.payload_serializers.JSONSerializer import JSONSerializer
from dl_mqtt_clients.func._general_func import logging_format
import logging
import random, string
logging.basicConfig(format=logging_format(), level=logging.INFO)


@pytest.fixture(scope='session')
def schema(tmpdir_factory):
    schema = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "title": "log",
        "type": "object",
        "properties": { "data": {"type": "array", "items": {"type":"number"}, "minItems": 1, "maxItems": 1} }
    }
    fn = tmpdir_factory.mktemp("data").join("schema.json")
    with open(str(fn), 'w') as outfile:  
        json.dump(schema, outfile)
    return str(fn)

@pytest.fixture(scope='session')
def inval_schema(tmpdir_factory):
    schema = "not json"
    fn = tmpdir_factory.mktemp("data").join("schema.json")
    with open(str(fn), 'w') as outfile:  
        outfile.write(schema)
    return str(fn)

@pytest.fixture(scope='session')
def json_payload():
    return '{"data": [0.21]}'.encode('utf8')

@pytest.fixture(scope='session')
def inval_json_payload():
    return '{"data": [0.21}'.encode('utf8')

@pytest.fixture(scope='session')
def invalid_dims_json_payload():
    return '{"data": [0.21, 0.22]}'.encode('utf8')

def test_deserialize():
    j = JSONSerializer()
    j_str = '{"data": [0.21, 0.21, 0.21, 0.21, 0.21, 0.21]}'.encode('utf8')
    j.deserialize(j_str)

def test_serialize():
    j = JSONSerializer()
    data= [0.21, 0.21, 0.21, 0.21]
    j.serialize(data, output_field_name='test')

def test_json_schema_load(schema):
    j = JSONSerializer()
    j.load_schema(schema)

def test_json_schema_load_inval(inval_schema):
    j = JSONSerializer()
    with pytest.raises(json.decoder.JSONDecodeError):
        j.load_schema(inval_schema)

def test_json_schema_file_dne():
    j = JSONSerializer()
    with pytest.raises(FileNotFoundError):
        j.load_schema('/tmp/' +''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)))

def test_json_schema_validate(schema, json_payload):
    j = JSONSerializer()
    j.load_schema(schema)
    j.deserialize(json_payload)

def test_deserialize_err(inval_json_payload):
    j = JSONSerializer()
    with pytest.raises(json.decoder.JSONDecodeError):
        j.deserialize(inval_json_payload)

def test_validate_warning(json_payload, schema):
    """tests whether warning is set for when _validate is called without schema set"""
    data = json.loads(json_payload.decode('utf8'))
    j = JSONSerializer()
    j._validate(json_data=data)
    assert(j.has_warned)