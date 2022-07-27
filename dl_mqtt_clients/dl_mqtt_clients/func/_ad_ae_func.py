import numpy as np

def reconstr_error(predicted, expected):
    assert(predicted.shape==expected.shape)
    return np.linalg.norm(predicted-expected, axis=1)