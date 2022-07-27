import pytest
import logging
import numpy as np
import pickle
from dl_mqtt_clients.func._general_func import logging_format
import dl_mqtt_clients.func._nn_func as nn_f

logging.basicConfig(format=logging_format(), level=logging.DEBUG)
serialize_logger= logging.getLogger('foo')

def generate_weights_array(nLayers):
    test_data = []
    for i in range(nLayers):
        test_data.append(np.random.rand(4, 7))
    return test_data

@pytest.mark.compression
def test_compress():
    precision = 8
    expected_dtype = np.uint8
    test_data = generate_weights_array(10)
    compress_data = nn_f.compress_keras_weights(test_data, precision, 0.0, 1.0)
    assert(len(test_data)==len(compress_data))
    for l in compress_data:
        assert(type(l)==np.ndarray)
        assert(l.dtype==expected_dtype)
    return

@pytest.mark.compression
def test_inflate_8bit():
    precision = 8
    expected_dtype = np.uint8
    test_data = generate_weights_array(10)
    wMin, wMax = nn_f.getMinMaxVals(test_data)
    compress_data = nn_f.compress_keras_weights(test_data, precision, wMin, wMax)
    inflated_data = nn_f.inflate_keras_weights(compress_data, wMin, wMax, precision)
    for l in range(1):
        #atol param sets absolute tolerance. we set it to 2 decimal places
        assert(np.allclose(inflated_data[l], test_data[l], atol=1e-2))
    return

@pytest.mark.compression
def test_inflate_16bit():
    precision = 16
    expected_dtype = np.uint8
    test_data = generate_weights_array(10)
    wMin, wMax = nn_f.getMinMaxVals(test_data)
    compress_data = nn_f.compress_keras_weights(test_data, precision, wMin, wMax)
    inflated_data = nn_f.inflate_keras_weights(compress_data, wMin, wMax, precision)
    for l in range(1):
        #atol param sets absolute tolerance. we set it to 2 decimal places
        assert(np.allclose(inflated_data[l], test_data[l], atol=1e-2))
    return

@pytest.mark.compression
def test_inflate_32bit():
    precision = 32
    expected_dtype = np.uint8
    test_data = generate_weights_array(10)
    wMin, wMax = nn_f.getMinMaxVals(test_data)
    compress_data = nn_f.compress_keras_weights(test_data, precision, wMin, wMax)
    inflated_data = nn_f.inflate_keras_weights(compress_data, wMin, wMax, precision)
    for l in range(1):
        #atol param sets absolute tolerance. we set it to 8 decimal places
        assert(np.allclose(inflated_data[l], test_data[l], atol=1e-8))
    return



@pytest.mark.generalfunc
def test_weight_list_same_dim():
    test_data1 = generate_weights_array(10)
    test_data2 = generate_weights_array(10)
    assert(nn_f.is_weight_list_same_dim(test_data1, test_data2))
    test_data2 = generate_weights_array(5)
    assert(not nn_f.is_weight_list_same_dim(test_data1, test_data2))
    test_data2 = None
    with pytest.raises(TypeError) as exc_info:
        nn_f.is_weight_list_same_dim(test_data1, test_data2)
    exception_raised = exc_info.value
    assert(exception_raised)