# coding: utf-8
from da import dA
from LogisticRegression import LogisticRegression

class SdA(object):
	def __init__(self, n_visible, hidden_layer_size, n_outs):
		self.sigmoid_layers = []
		self.dA_layers = []

		self.n_layers = len(hidden_layer_size)

		assert self.n_layers

		for i in xrange(self.n_layers):
			# layer size
			if i == 0:
				layer_size = n_visible
			else:
				layer_size = hidden_layer_size[i - 1]
			# layer input
			dA_layer = dA(n_visible=layer_size, n_hidden=hidden_layer_size[i])
			self.dA_layers.append(dA_layer)

		self.log_layer = LogisticRegression(hidden_layer_size[-1], n_outs)

	def pretrain(self, train_x, corruption_level=0.3, epochs=100):
		for dA in self.dA_layers:
			dA.train(input=train_x, corruption=corruption_level, epochs=epochs)

	def finetune(self, x_train, y_train, epochs=100):
		self.log_layer.train(x_train=x_train, y_train=y_train, epochs=epochs)

	def predict(self, x):
		for i in x(self.n_layers):
			self.dA_layers[i].