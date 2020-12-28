# -*- coding: utf-8 -*-
from typing import List, Union
import re


def recursiveUpdate(src, dst, typeRestriction=False, filterKeys=[]):
	assert isinstance(src, dict) and isinstance(dst, dict), "Src and Dst must be dict"
	for k in src.keys():
		if k in filterKeys:
			continue
		if k in dst and isinstance(src[k], dict) and isinstance(dst[k], dict):
			recursiveUpdate(src[k], dst[k])
		else:
			if not typeRestriction or k not in dst or isinstance(src[k], type(dst[k])):
				dst[k] = src[k]


def recursiveSetDefault(src, dst):
	assert isinstance(src, dict) and isinstance(dst, dict), "Src and Dst must be dict"
	for k in src.keys():
		if k not in dst:
			dst[k] = src[k]
		elif isinstance(src[k], dict) and isinstance(dst[k], dict):
			recursiveSetDefault(src[k], dst[k])


def _dotPath(dotPath: Union[None, str, List[str]]) -> List[str]:
	if dotPath is None or dotPath == '' or dotPath == []:
		return []
	if isinstance(dotPath, str):
		keys = dotPath.split('.')
	elif isinstance(dotPath, list):
		keys = dotPath
	elif isinstance(dotPath, tuple):
		keys = list(dotPath)
	else:
		raise TypeError('dotPath must be string or list')
	return keys


def query(source, dotPath, default=None):
	keys = _dotPath(dotPath)
	value = source
	try:
		for key in keys:
			if isinstance(value, (list, tuple)):
				key = int(key)
			value = value[key]
		return value
	except (ValueError, IndexError, KeyError):
		return default


def update(source, dotPath, value, requireExists=False):  # TODO：路径中存在list，tuple未处理
	keys = _dotPath(dotPath)
	temp = source
	if not keys:
		return False
	for key in keys[:-1]:
		if not isinstance(temp, dict):
			return False
		if key not in temp:
			if requireExists:
				return False
			else:
				temp[key] = {}
		temp = temp[key]
	if keys[-1] not in temp:
		if requireExists:
			return False
	temp[keys[-1]] = value
	return True


def exists(source, dotPath):
	keys = _dotPath(dotPath)
	value = source
	try:
		for key in keys:
			if isinstance(value, (list, tuple)):
				key = int(key)
			value = value[key]
		return True
	except (ValueError, IndexError, KeyError):
		return False


def getKey(source, pattern):
	ret = []
	for k in source.keys():
		if re.match(pattern, k):
			ret.append(k)
	return ret

