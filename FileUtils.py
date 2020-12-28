# -*- coding: utf-8 -*-

import codecs
import json
import os
import sys
import traceback


def readJson(filePath):
	try:
		return json.load(open(filePath, 'r', encoding="utf-8"))
	except Exception:
		traceback.print_exc()
	return None


def writeJson(filePath, data):
	try:
		with codecs.open(filePath, 'w', encoding="utf-8") as f:
			json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)
		return True
	except Exception:
		print('Error in writeJson: filePath=%s data=%s' % (filePath, data))
		traceback.print_exc()
		return False


def readPython(filePath, filterKeys=None):
	if filterKeys is None:
		filterKeys = ['__name__', '__doc__', '__package__', '__loader__', '__spec__', '__file__', '__cached__', '__builtins__']
	if not os.path.isfile(filePath):
		return {}
	ret = {}
	folderPath = os.path.dirname(filePath)
	fileName = os.path.basename(filePath)
	moduleName = os.path.splitext(fileName)[0]
	existFlag = False
	if folderPath in sys.path:
		existFlag = True
	if not existFlag:
		sys.path.append(folderPath)
	try:
		configModule = __import__(moduleName)
		ret = configModule.__dict__.copy()
	except Exception:
		traceback.print_exc()
		return None

	if not existFlag and folderPath in sys.path:
		sys.path.remove(folderPath)

	if ret and filterKeys:
		for key in filterKeys:
			if key in ret:
				del ret[key]

	if moduleName in sys.modules:
		del sys.modules[moduleName]

	return ret


def valueToStr(value, indent=0, continuous=False):
	prefix = '\t' * indent
	if not continuous:
		ret = str(prefix)
	else:
		ret = ''
	if isinstance(value, list):
		if not value:
			return '[]'
		ret += '[\n'
		tag = False
		for i in value:
			if tag:
				ret += ',\n'
			tag = True
			ret += valueToStr(i, indent + 1)
		ret += '\n' + prefix + ']'
	elif isinstance(value, tuple):
		if not value:
			return '()'
		ret += '(\n'
		tag = False
		for i in value:
			if tag:
				ret += ',\n'
			tag = True
			ret += valueToStr(i, indent + 1)
		ret += '\n' + prefix + ')'
	elif isinstance(value, dict):
		if not value:
			return '{}'
		ret += '{\n'
		tag = False
		for k in sorted(value.keys()):
			v = value[k]
			if tag:
				ret += ',\n'
			tag = True
			ret += valueToStr(k, indent + 1) + ': ' + valueToStr(v, indent + 1, True)
		ret += '\n' + prefix + '}'
	elif isinstance(value, str):
		ret += repr(value)
	elif isinstance(value, int) or isinstance(value, float):
		ret += str(value)
	elif value is None:
		ret = 'None'
	else:
		ret += repr(value)
	return ret


def writePython(filePath, data):
	saveStr = "# -*- coding: utf-8 -*-\n"
	for k in sorted(data.keys()):
		v = data[k]
		saveStr += "{} = {}\n".format(k, valueToStr(v))
	try:
		with open(filePath, 'w', encoding='utf-8') as fp:
			fp.write(saveStr)
		return True
	except Exception:
		traceback.print_exc()
		return False


def readFile(filePath):
	if not os.path.isfile(filePath):
		return {}
	fileType = os.path.splitext(filePath)[-1]
	if fileType == '.json':
		return readJson(filePath)
	elif fileType == '.py':
		return readPython(filePath)
	return {}


def writeFile(filePath, data: dict, fileType=None) -> bool:
	if not data:
		return False
	folderPath = os.path.dirname(filePath)
	if not os.path.exists(folderPath):
		os.makedirs(folderPath)
	if fileType is None:
		fileType = os.path.splitext(filePath)[-1]
	if fileType == '.json':
		return writeJson(filePath, data)
	elif fileType == '.py':
		return writePython(filePath, data)
	return False
