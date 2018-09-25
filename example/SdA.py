# coding: utf-8

class SdA(object):
	def __init__(self, n_visible, hidden_layer_size, n_outs):
		self.sigmoid_layers = []
		self.dA_layers = []

		self.n_layers = len(hidden_layer_size)

		assert self.n_layers

		for i in xrange(self.n_layers):
			if i == 0:
				layer_input =