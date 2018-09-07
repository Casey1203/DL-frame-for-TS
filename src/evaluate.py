# coding: utf-8

from src.wavelet.dwt import dwt
from src.util.datalayer.file_loader import FileLoader




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
	loader = FileLoader()
	begin_date = '20080101'
	end_date = '20180701'
	file_path = '../data/RawData.xlsx'
	raw_data = loader.get_local_csv_file(file_path)

	train_close_index, test_close_index = split_train_test(close_index)
	a, d_vec = dwt(train_close_index, 'db1', level=2)




if __name__ == '__main__':
	main()