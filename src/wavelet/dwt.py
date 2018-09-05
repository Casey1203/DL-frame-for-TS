# coding: utf-8


import pywt, numpy as np
from src.util.exception import AlgoError


def dwt(x, wavelet, level=1, mode='symmetric'):
	if wavelet not in pywt.wavelist():
		msg = 'input wavelet %s is not supported' % wavelet
		raise AlgoError(message=msg)
	coef = np.array(pywt.wavedec(x, wavelet, mode, level))
	a = coef[0]
	d_vec = coef[1:]
	return a, d_vec
