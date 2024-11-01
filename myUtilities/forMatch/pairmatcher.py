import re
import os
import inspect
import numpy as np
from typing import Union, Literal, Callable, TypeVar

class PairMatcher:
	# T = TypeVar('T')
	s = ''
	bl = '('
	br = ')'
	ofst = 1
	parter = {'(': ')', ')': '(','[': ']', ']': '[', '{': '}', '}': '{', '<': '>', '>': '<'}

	def __init__(self, s:str, bl:str, br_inbl:str|bool=False, identical:bool=False)->None:	# 双下划线开头来定义私有方法
		if not (isinstance(s, str) or isinstance(bl, str) or 
		  (isinstance(br, str) or isinstance(br, bool)) or 
		  isinstance(identical, bool)): raise TypeError
		if (not s) or (not bl) or br_inbl == '': raise ValueError('s, bl, br cannot be empty string')
		self.s = s
		self.setParter(bl, br_inbl, identical=identical)

	# def _isValid_initProcess(self, func: Callable[..., T], *args, **kwargs)->T:
	# 	# 获取接收函数的参数签名
	# 	sig = inspect.signature(func)
	# 	params = sig.parameters

	# 	# 检查传入的位置参数和关键字参数
	# 	bound_args = sig.bind(*args, **kwargs)
	# 	bound_args.apply_defaults()

	# 	# 检查参数类型是否符合要求
	# 	for param_name, param_value in bound_args.arguments.items():
	# 		param_type = params[param_name].annotation

	# 		# 检查参数是否为空值
	# 		if param_value is None:
	# 			raise ValueError(f"Parameter '{param_name}' cannot be None.")
			
	# 		# 检查参数类型是否符合要求
	# 		if not isinstance(param_value, param_type):
	# 			raise TypeError(f"Parameter '{param_name}' must be of type '{param_type}'")
			
	# 	return func(*args, **kwargs)

	def isPaired(self, ddict:dict={'L':[], 'R': []})-> bool:
		l = len(ddict['L'])
		r = len(ddict['R'])
		return False if (l != r) or (l == 0 and r == 0) else True

	def isOneCh(self, ch:str)->bool:
		if len(ch) != 1: self.setOffset(ch); return False
		else: return True

	def setOffset(self, ch:str)->None:
		if len(ch) != 1:self.ofst = len(ch) - 1

	def setParter(self, bl:str, br_inbl:str|bool=True, identical:bool=False)->None:
		self.bl = bl
		if isinstance(br_inbl, str): 
			assert bl == self.getParter(br_inbl, identical=identical), "ERROR: unmatchable pairs."
			self.br = br_inbl
			return
		if isinstance(br_inbl, bool) and br_inbl:
			assert not self.isOneCh(bl), "ERROR: cannot find another pair in bl."
			self.bl = bl[:int(len(bl) / 2)]
			assert self.bl == self.getParter(bl[int(len(bl) / 2):], identical=identical), "ERROR: unmatchable pairs."
			self.br = bl[int(len(bl) / 2):]
			return
		# assert self.br == self.getParter(bl, identical=identical), "ERROR: unmatchable pairs."
		self.br = self.getParter(bl, identical=identical)


	def getParter(self, m:str, identical:bool=False)->str:
		if not identical:
			parterr = re.findall(r'[(){}[\]<>]', m)
			if parterr:
				for i in parterr:
					m = re.sub('\\'+i, self.parter[i], m, count=1)
		return m[::-1]

	def getChIdx(self, s:str, ch:str)->list:
		idxs = []
		idx = -1
		self.setOffset(ch)
		while True: 
			idx = s.find(ch, idx + self.ofst)
			if idx == -1: break
			idxs.append(idx)
		return idxs

	def getBktIdx(self, s:str, bl:str, br:str) -> dict:
		if bl is None and lr is None: bl = self.bl; br = self.br
		return {'L': self.getChIdx(s=s, ch=bl), 'R': self.getChIdx(s=s, ch=br)}

	def getPair(self, s:str|None=None, 
			 bl:str|None=None, 
			 br:str|None=None, 
			 out:Literal['default', 'sorted']='default', 
			 f:str|None=None, 
			 quietly:bool=True)-> Union[list[tuple], list[int]]:
		f = open(os.devnull, 'w') if quietly else (open(f, 'w') if f else None)
		pair = []
		if s is None: s = self.s
		if bl is None and br is None: br = self.br; bl = self.bl
		print(50 * '-' + f"\nSTART Getting pair...\nSTRING:\t\t{s}\n" + f"MATCHING PAIRS:\t{bl}...{br}", file=f)
		if bl == br: 
			idxs = self.getChIdx(s, bl)
			if len(idxs) == 0: print("Cannot find the pair", file=f); return pair
			if len(idxs) % 2 == 1: print('ERR: Upaired Braket.', file=f); return pair	# isPaired()
			print("\n......\tDONE\n" + "-" * 50, file=f)
			if out == 'sorted': return idxs
			else:
				for i in range(0, len(idxs), 2):
					pair.append((idxs[i], idxs[i + 1]))
				return pair
		"""
		这个函数用于找到一个字符串中所有字符对的索引对
		原理：
		i.g.
		a = [1, 3, 5]		b = [2, 4, 6]
				1	2	3
		   a	1	3	5
		b
	1   2	    1  -1  -3
	2   4		3   1  -1
	3   6		5   3   1
			从最里边的左括号开始，匹配对应的右括号(即找到最邻近右括号，找到后其他dist舍弃)"""
		idxs = self.getBktIdx(s, bl, br)
		if not self.isPaired(idxs): print('ERR: Upaired Braket.', file=f); return pair
		lt_rv = np.array(idxs['L'][::-1])
		rt = np.array(idxs['R'])
		dist = np.subtract.outer(rt, lt_rv).astype(float)	# 得到括号间的字符距离(右括号 - 左括号)
		dist[dist <= 0] = np.inf							# 舍弃负值
		for i in range(rt.size):							# 返回每个左括号最近的右括号(距离最小的右括号)
			min_dist_idx_row = int(np.argmin(dist[i, :]))
			pair.append((int(lt_rv[min_dist_idx_row]), int(rt[i])))
			#pair.append(int(lt_rv[min_dist_idx_row])); pair.append(int(rt[i]))
			dist[:, min_dist_idx_row] = np.inf
		print("\n......\tDONE\n" + "-" * 50, file=f)
		if out == 'sorted': return sorted([item for pairr in pair for item in pairr])
		return pair

if __name__ == '__main__':
	ss = 'fasfdsa() ()(()(fa(fa)fa()((asdf)fdas)))'
	yy = PairMatcher(ss, bl='((', br_inbl=False)
	print(yy.getPair(out='sorted', quietly=True))
	print(' '.join([ss[i] for i in yy.getPair(out='sorted')]))

	yy3 = PairMatcher(ss, bl='()')
	print(yy3.getPair(out='sorted', quietly=True))
	print(' '.join([ss[i] for i in yy3.getPair(out='sorted')]))

	ss = 'fasfdsa "" "" "hello" "wofada"  " "'
	yy1 = PairMatcher(ss, bl='"', identical=True)
	print(yy1.getPair())
	print(' '.join([ss[i] for i in yy1.getPair(out='sorted')]))

	ss= 'fasdaf(fadsa( fadaf(fffff('
	yy2 = PairMatcher(ss, bl='""',identical=True)
	print(yy2.getPair(quietly=False))
	print(' '.join([ss[i] for i in yy2.getPair(out='sorted')]))

	ss= 'fasdaf(fadsa( fadaf(fffff('
	yy4 = PairMatcher(ss, bl='(',identical=True)
	print(yy4.getPair())
	print(' '.join([ss[i] for i in yy4.getPair(out='sorted')]))