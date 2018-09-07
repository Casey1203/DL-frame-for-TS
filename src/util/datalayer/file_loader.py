# coding: utf-8

import pandas as pd


class FileLoader:
	def __init__(self):
		pass

	def get_local_csv_file(self, file_path, dtype=None):
		if dtype is None:
			dtype = {}
		df = pd.read_csv(file_path, dtype=dtype)
		return df

	def get_local_xls_file(self, file_path, dtype=None):
		if dtype is None:
			dtype = {}
		df = pd.read_excel(file_path, dtype=dtype)
		return df

