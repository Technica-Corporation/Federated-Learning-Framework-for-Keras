from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.externals import joblib
import numpy as np
import copy
import pickle

def normalize_data(data, scaler):
    return np.array(scaler.transform(data))

def load_scaler(h5_path):
    return joblib.load(h5_path)

def compress(values, min_value, max_value, max_comp_value):
    """Function that takes a NumPy array and maps its values to points 
        along linear spaced points from [0, max_comp_value]

        Args:
            values (numpy/float):
            min_value (float): minimum value in possibly range of floats
            max_value (float): maximum value in possible range of floats
            max_comp_value (int): max value of point to map to, typically 255 to represent uint 8-bit values
        Returns:
            rounded_values (numpy/float): new compressed representation of input array, rounded to nearest integer val
    """
    rounded_values = np.copy(values)
    rounded_values -= min_value
    rounded_values /= (max_value - min_value)
    rounded_values *= max_comp_value
    rounded_values = np.round(rounded_values)
    assert(rounded_values.all() <= max_comp_value)
    return rounded_values

def inflate(values, min_value, max_value, precision):
    """Function that takes a NumPy array and inflatse its values back to float
        Args:
            values (numpy/float): 
            min_value (float): minimum value in possibly range of floats
            max_value (float): maximum value in possible range of floats
            precision (int): theoretical precision (e.g. 8, 16, 32)
        Returns:
            inflated_values (numpy/float): new float value approximation
    """
    inflated_values = np.copy(values).astype('float32')
    max_compressed_value = 2**precision - 1
    inflated_values /= max_compressed_value
    inflated_values *= (max_value - min_value)
    inflated_values += min_value
    return inflated_values

def bits_to_dtype(x):
    """Function that an integer valued precision and returns the NumPy data type. 
        Convenience function to move between data types. 
        Args:
            x (int): precision
        Returns:
            string: data type
    """
    return {
        8: 'uint8',
        16: 'float16',
        32: 'float',
        64: 'float64'
        }[x]

def getMinMaxVals(keras_weights):
    """Function that gets the minimum vaue from a list of numpy arrays

        Args:
            keras_weights (list of numpy): Representative of a models weights, generated from model.get_weights()

        Returns:
            minV (float): minimum float value 
            maxV (float): maximum float value
    """
    minV, maxV = 100, -100
    for layer in keras_weights:
        localMin, localMax = np.min(layer), np.max(layer)
        if localMin < minV:
            minV = localMin
        if localMax > maxV:
            maxV = localMax
    return minV, maxV

def getMinMaxModelWeights(weight_list):
    """Function that generates the minimum and maximum weight value in a list of weights (e.g. list of list of NumPy)

        Args:
            weight_list (float): series of weights where each index represents a different models set of weights generated from keras

        Returns:
            minW (float): minimum float value 
            maxW (float): maximum float value
    """
    minW, maxW = 100, -100
    for model_weight in weight_list:
        locMin, locMax = getMinMaxVals(model_weight)
        if locMin < minW: 
            minW = locMin
        if locMax > maxW:
            maxW = locMax
    return float(minW), float(maxW)

def compress_keras_weights(keras_weights, precision, minW, maxW):
    """Rounds a set of weights generated from Keras' model.get_weights() function to a certain integer precision
        Iterates through each layer of the 
        Args:
            keras_weights (float): list of numpy. generated from model.get_weights()
            precision (int): integer precision to compress to. must be one of [8, 16, 32]
            minW (float): minimum float value 
            maxW (float): maximum float value
        Returns:
            compressed_weights (list): list of numpy arrays as dtype determiend by 'precision' argument
    """
    max_comp_value = 2**precision-1
    dtype = bits_to_dtype(precision)
    assert(len(keras_weights) > 0)
    compressed_weights = [compress(layer, minW, maxW, max_comp_value).astype(dtype) for layer in keras_weights]
    return compressed_weights

def inflate_keras_weights(keras_weights, minV, maxV, base_precision):
    """  
        Args:
            keras_weights (list):
            minV (float):
            maxV (float):
            base_precision (float):
        Returns:
            inflated_weights (list):
    """
    inflated_weights = [inflate(layer, minV, maxV, base_precision).astype(np.float32) for layer in keras_weights]
    return inflated_weights

def is_weight_list_same_dim(weightList1, weightList2):
    if type(weightList1) != list or type(weightList2) != list:
        raise TypeError("Function expecting of type list")
    if len(weightList1) != len(weightList2):
        return False
    if not all(isinstance(x, np.ndarray) for x in weightList1):
        raise TypeError("Must contain types of only np.ndarray")
    if not all(isinstance(x, np.ndarray) for x in weightList2):
        raise TypeError("Must contain types of only np.ndarray")
    for i in range(len(weightList1)):
        if weightList1[i].shape != weightList2[i].shape:
            return False
    return True

def merge_models(weights):
    """Given a list of Keras models, takes the weights and returns the weights averaged 
    Args:
        models (list): list of Keras models
    Returns:
        new_weights (float): list of float32 NumPy array representative of the new weights
                             can be used to set the weights via model.set_weights(new_weights)
    """
    #average the weights
    new_weights = list()
    for weights_list_tuple in zip(*weights):
        new_weights.append([np.array(weights_).mean(axis=0) for weights_ in zip(*weights_list_tuple)])
    return new_weights
		
