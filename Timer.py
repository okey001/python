# -*- coding:utf-8 -*-

index = 0


class TimerProxy(object):
	def __init__(self, timerId, delay, func, isRepeat, *args, **kwargs):
		self.delay = delay
		self.func = func
		self.args = args
		self.kwargs = kwargs
		self.timerId = timerId
		self.isRepeat = isRepeat

	def Call(self):
		if self.func:
			self.func(*self.args, **self.kwargs)
			return True
		return False

	def Cancel(self):
		self.func = None
		self.isRepeat = False


class TimerCycle(object):
	def __init__(self, length, base=1):
		"""一个时间轮
		
		Args:
			length (int): 时间轮的长度
			base (int, optional): 移动一格代表的tick次数. Defaults to 1.
		"""
		self.pos = 0  # 当前指针位置
		self.prev = None  # 较小的时间轮
		self.next = None  # 较大的时间轮
		self.base = base
		self.length = length
		self.bucket = []  # 一个bucket表示一个格子
		self.posInfo = {}  # 当timer移动到这里的时候的位置
		for _ in range(length):
			self.bucket.append({})

	def Insert(self, timer, add=0):
		"""插入一个Timer，这个方法可能会调用下一个时间轮的Insert方法
		
		Args:
			timer (TimerProxy): 定时器
			add (int, optional): 当前以及所有较小的时间轮的偏移. Defaults to 0.
		"""
		delay = timer.delay
		if delay >= self.base * self.length:  # 延时超过了这个轮子的最大值
			if self.next is None:  # 没有下一个时间轮了
				raise Exception("delay is too long!")
			posDelta = (delay + add) // self.base % self.length  # 插入位置相对目前位置的偏移
			self.posInfo[timer.timerId] = (self.pos + posDelta) % self.length  # 因为这个定时器要先放到较大的时间轮上，先保存这个定时器的位置信息，等从较大时间轮退回时，放到对应的位置上
			self.next.Insert(timer, add + self.pos * self.base)  # 将这个定时器放到下一个较大的时间轮上
		else:  # 插入此时间轮的bucket格子中
			pos = ((delay + add) // self.base + self.pos) % self.length  # delay + add 除以每格的大小 再加上当前位置
			self.bucket[pos][timer.timerId] = timer  # 放置上去

	def Add(self, timer):
		"""从较大的时间轮上退回一个定时器
		
		Args:
			timer (TimerProxy): 退回的定时器
		"""
		timerId = timer.timerId
		self.bucket[self.posInfo[timerId]][timerId] = timer
		del self.posInfo[timerId]

	def Call(self):
		"""触发时间轮的当前位置所有定时器，只有最小的时间轮才会触发，较大的时间轮触发时只是把定时器退回到较小的时间轮中
		"""
		timerList = list(self.bucket[self.pos].values())
		self.bucket[self.pos].clear()
		for timer in timerList:
			flag = timer.Call()
			if flag and timer.isRepeat:  # 重复定时器则重新插入
				Timer.Insert(timer)
			else:
				del Timer.timer[timer.timerId]  # 清除这个定时器的记录

	def Move(self):
		"""时间轮移动一格，当较小的时间轮移动一圈时，会触发下一个较大的时间轮的Move
		"""		
		self.pos = (1 + self.pos) % self.length  # 移动一格
		if self.pos == 0:  # 移动了一圈
			if self.next:  
				self.next.Move()
		if self.prev:  # 表示这个时间轮不是最小的那个，需要把当前格子中的定时器退回到较小的定时器中，并分布到各个格子中，
			for timer in self.bucket[self.pos].values():
				self.prev.Add(timer)

			self.bucket[self.pos].clear()
		else:  # 这个时间轮是最小的，触发当前格子中的所有定时器
			self.Call()

class Timer(object):

	baseId = 0
	maxId = 0x7fffffff

	@staticmethod
	def init(precision=0.001, cycleCount=4, cycleLength=1000):
		"""初始化相关参数
		
		Args:
			precision (float, optional): 每一次tick的时间间隔，目前没什么用. Defaults to 0.001.
			cycleCount (int, optional): 时间轮个数. Defaults to 4.
			cycleLength (int, optional): 每个时间轮的格子数. Defaults to 1000.
		"""		
		Timer.precision = precision
		Timer.cycleCount = cycleCount
		Timer.cycleLength = cycleLength
		Timer.baseId = 0
		Timer.cycle = []
		Timer.timer = {}
		base = 1
		for _ in range(cycleCount):
			Timer.cycle.append(TimerCycle(cycleLength, base))
			base *= cycleLength
		for i in range(cycleCount):
			if i > 0:
				Timer.cycle[i].prev = Timer.cycle[i - 1]
			if i < cycleCount - 1:
				Timer.cycle[i].next = Timer.cycle[i + 1]

	@staticmethod
	def Insert(timer):
		Timer.cycle[0].Insert(timer)

	@staticmethod
	def GenerateId():
		Timer.baseId += 1
		return Timer.baseId

	@staticmethod
	def AddTimer(delay, func, *args, **kwargs):
		timerId = Timer.GenerateId()
		timer = TimerProxy(timerId, delay, func, False, *args, **kwargs)
		Timer.timer[timerId] = timer
		Timer.cycle[0].Insert(timer)

	@staticmethod
	def AddRepeatTimer(delay, func, *args, **kwargs):
		timerId = Timer.GenerateId()
		timer = TimerProxy(timerId, delay, func, True, *args, **kwargs)
		Timer.timer[timerId] = timer
		Timer.cycle[0].Insert(timer)

	@staticmethod
	def Cancel(timerId):
		Timer.timer[timerId].func.cancel()

	@staticmethod
	def Tick():
		Timer.cycle[0].Move()


length = 1000000
output = []
index = 0


def f():
	# 测试函数
	global index
	output.append(index)


def test1():
	input = []
	Timer.init()
	global index
	if True:
		import random
		import time
		start = time.time()
		for i in range(length):
			if i + 100 <= length:
				t = random.randint(1, 9999)
				repeat = random.randint(0, 1)
				if repeat == 1 and False:
					Timer.AddRepeatTimer(t, f)
					ii = i
					while ii + t <= length:
						ii = ii + t
						input.append(ii)
				else:
					if i + t <= length:
						input.append(i + t)
					Timer.AddTimer(t, f)
			index += 1
			Timer.Tick()
		end = time.time()
		print(end - start)
		input.sort()
		#print(input)
		#print(output)
		print(input == output)
		


class A(object):
	def __init__(self):
		super(A, self).__init__()

	def test(self, *args, **kwargs):
		print("test")
		print(self)
		print(args)
		print(kwargs)

	@staticmethod
	def testStatic(*args, **kwargs):
		print('testStatic')
		print(args)
		print(kwargs)


def test2():
	# 实例方法，静态方法测试
	Timer.init()
	a = A()
	Timer.AddRepeatTimer(10, a.test, 1, 2, k=3)
	Timer.AddRepeatTimer(10, A.testStatic, 1, 2, k=3)
	for _ in range(20):
		Timer.Tick()


if __name__ == '__main__':
	test1()
	
