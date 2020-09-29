# -*- coding: utf-8 -*-
def logger(*selfs):
	"""运行时打印类名，方法名，参数列表，只能用于修饰实例方法
	Args:
		*selfs (str): 需要打印的实例的字段，如对实例obj的方法func使用@logger('a', 'b')修饰，则会打印obj.a，和obj.b
	"""
	def _NeedLogger(f):
		from functools import wraps

		@wraps(f)
		def __NeedLogger(self, *args, **kwargs):
			log = '%s.%s    ' % (self.__class__.__name__, f.__name__)
			for i in selfs:
				log += 'self.%s:%s  ' % (i, getattr(self, i, 'Error'))
			log += '  args:' + str(args)
			log += '    kwargs:' + str(kwargs)
			print(log)
			return f(self, *args, **kwargs)

		return __NeedLogger

	return _NeedLogger


def runningTime(f):
	"""打印这个函数的运行时长，在方法前加@runningTime即可，不需要括号
	"""
	def _runningTime(*args, **kwargs):
		import time
		timeBegin = time.time()
		ret = f(*args, **kwargs)
		timeEnd = time.time()
		print("{} cost {} seconds, args:{}, kwargs:{}".format(f.__name__, timeEnd - timeBegin, str(args), str(kwargs)))
		return ret

	return _runningTime
