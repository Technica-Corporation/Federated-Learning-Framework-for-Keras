import json
import logging
import numpy as np
from dl_mqtt_clients.payload_serializers.serializer import SerializerBase
from dl_mqtt_clients.func._general_func import get_time_unix
from dl_mqtt_clients.func._serializer_func import decode_bytestr_to_json

class JSONSerializer(SerializerBase):
    def __init__(self):
        self.schema = None
        self.logger = logging.getLogger(__name__)
        self.has_warned = False
        self.logger.info("Serializer initialized")
	
    def load_schema(self, file):
        self.logger.info('Loading validation schema')
        try:
            with open(file, 'r') as f:
                schema_data = f.read()
            self.schema = json.loads(schema_data)
            self.logger.info('Schema loaded')
        except FileNotFoundError:
            self.logger.error("JSON Schema File not Found: {}".format(file))
            raise
        except json.decoder.JSONDecodeError:
            self.logger.error("Error with JSON Schema File Format")
            raise
      
    def deserialize(self, input):
        try: 
            output = decode_bytestr_to_json(value=input)
        except json.decoder.JSONDecodeError:
            raise 
        return output
		
    def serialize(self, data, output_field_name):
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return json.JSONEncoder.default(self, obj)
        return json.dumps({'timestamp': get_time_unix(), output_field_name: data}, cls=NumpyEncoder)