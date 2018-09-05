# coding: utf-8

from src.wavelet.dwt import dwt
from src.util.datalayer.data_loader import DataAPILoader




def predict():
	pass


def train():
	pass

def evaluate():
	pass

def split_train_test(x_data, train_ratio=0.7):
	x_data_size = len(x_data)
	train_index_end = x_data_size * train_ratio
	train_x = x_data[:train_index_end]
	test_x = x_data[train_index_end:]
	return train_x, test_x

def main():
	loader = DataAPILoader()
	begin_date = '20080101'
	end_date = '20180701'
	close_index = loader.get_market_index_daily(index_ticker='0003000', begin_date=begin_date, end_date=end_date)
	train_close_index, test_close_index = split_train_test(close_index)



if __name__ == '__main__':
	main()