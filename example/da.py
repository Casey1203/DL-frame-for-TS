# coding: utf-8
from keras.layers import Input, Dense
from keras.models import Model
import numpy as np

class dA(object): # one hidden layer denoise
	def __init__(self, n_visible, n_hidden, rng=None):
		self.n_visible = n_visible
		self.n_hidden = n_hidden
		if rng is None:
			rng = np.random.RandomState(1234)
		self.rng = rng

		self.input = Input(shape=(n_visible,)) # placeholder

		encoded = self.get_hidden_values(self.input)
		decoded = self.get_recontructed_input(encoded)

		self.autoencoder = Model(self.input, decoded)
		self.autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')

	# encode
	def get_hidden_values(self, input):
		return Dense(self.n_hidden, activation='sigmoid')(input)

	def get_recontructed_input(self, hidden):
		return Dense(self.n_visible, activation='sigmoid')(hidden)

	def get_corrupted_input(self, input, corruption_level): # add noise
		assert corruption_level < 1

		return self.rng.binomial(
			size=input.shape, n=1, p=1-corruption_level) * input

	def train(self, lr=0.1, corruption=0.3, epochs=50, input=None):
		tilde_x = self.get_corrupted_input(input, corruption) # noised input
		self.autoencoder.fit(tilde_x, input, epochs=epochs, shuffle=True)


	def recontruct(self, x):
		return self.autoencoder.predict(x, verbose=True)



def test_dA():
	data = np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0]])

	n_visible = data.shape[1]
	n_hidden = 5
	rng = np.random.RandomState(123)
	da = dA(n_visible=n_visible, n_hidden=n_hidden, rng=rng)

	da.train(input=data, epochs=1000)

	x = np.array([[1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
                     [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0]])

	print da.recontruct(x)


if __name__ == '__main__':
	test_dA()