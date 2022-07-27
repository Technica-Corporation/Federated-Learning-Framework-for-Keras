import abc
import json

class SerializerBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def deserialize(self, input):
        """Parses data (bytearray)
        return an appropriate formatted object representing the data"""
    @abc.abstractmethod
    def serialize(self, data):
        """Serializes data to json output byte string"""