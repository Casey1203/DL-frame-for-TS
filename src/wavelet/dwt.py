import pywt
from src.util.exception import AlgoError

def dwt(x, wavelet, mode='symmetric'):
	if wavelet not in pywt.wavelist():
		msg = 'input wavelet %s is not supported' % wavelet
		raise AlgoError(message=msg)
	cA, cD = pywt.dwt(x, wavelet, mode)