# coding: utf-8
from keras.models import Sequential
from keras.layers import Dense


class LogisticRegression(object):
	def __init__(self, n_in, n_out):
		self.n_in = n_in
		self.n_out = n_out

		self.model = Sequential()
		self.model.add(Dense(n_out, input_dim=self.n_in, activation='sigmoid'))

		self.model.compile(optimizer='sgd',loss='categorical_crossentropy', metrics=['accuracy'])

	def train(self, x_train, y_train, epochs=100):
		self.model.fit(x=x_train, y=y_train, batch_size=50, epochs=epochs, verbose=True, validation_split=0.2)

	def evaluate(self, x_test, y_test):
		self.model.evaluate(x_test, y_test, verbose=True)

	def predict(self, x):
		self.model.predict(x)
