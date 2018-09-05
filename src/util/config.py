# coding: utf-8



INDEX_NAME_MAPPING = {
	"sz50": "000016",
	"hs300": "000300",
	"zz500": "000905",
	"tlqa": "DY0001",
	"zz800": "000906",
	'qzzs': "000013" # 企债指数
}

FACTOR_ORDER = [
    'BETA', 'MOMENTUM', 'SIZE', 'EARNYILD', 'RESVOL', 'GROWTH', 'BTOP',
    'LEVERAGE', 'LIQUIDTY', 'SIZENL', 'Bank', 'RealEstate', 'Health',
    'Transportation', 'Mining', 'NonFerMetal', 'HouseApp', 'LeiService',
    'MachiEquip', 'BuildDeco', 'CommeTrade', 'CONMAT', 'Auto', 'Textile',
    'FoodBever', 'Electronics', 'Computer', 'LightIndus', 'Utilities',
    'Telecom', 'AgriForest', 'CHEM', 'Media', 'IronSteel', 'NonBankFinan',
    'ELECEQP', 'AERODEF', 'Conglomerates', 'COUNTRY'
]