# coding=utf-8


import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class BaseError(Exception):
    def __init__(self, message=''):
        Exception.__init__(self, '%s' % message)


# 算法中的一段逻辑报错(比如一个函数)
class AlgoError(BaseError):
    def __init__(self, message=''):
        BaseError.__init__(self, message)


# 输入到算法的数据出错，因为从外部输入数据到算法曾
class PreprocessError(BaseError):
    def __init__(self, message=''):
        BaseError.__init__(self, message)


# 参数验证错误
class InputParameterError(BaseError):
    def __init__(self, message='invalid input parameter'):
        BaseError.__init__(self, message)


class RequestError(BaseError):
    pass
