import numpy as np
from typing import Union, Literal

class PairMatcher:

	s = ''
	bl = ''
	br = ''


	def __init__(self, s:str='', bl:str='(', br:str=')'):	# 双下划线开头来定义私有方法
		self.s = s
		self.bl = bl
		self.br = br
	


	def getChIdx(self, s:str, ch:str)->list:
		idxs = []
		idx = -1
		while True:
			idx = s.find(ch, idx + 1)
			if idx == -1: break
			idxs.append(idx)
		return idxs



	def getBktIdx(self, s:str, bl:str, br:str) -> dict:
		if bl is None and lr is None: bl = self.bl; br = self.br
		return {'L': self.getChIdx(s=s, ch=bl), 'R': self.getChIdx(s=s, ch=br)}
	



	def checkPaired(self, ddict:dict={'L':[], 'R': []})-> bool:
		l = len(ddict['L'])
		r = len(ddict['R'])
		return False if (l != r) or (l == 0 and r == 0) else True




	def getPair(self, s:str=None, bl:str=None, br:str=None, out:Literal['default', 'sorted']='default')-> Union[list[tuple], list[int]]:
		pair = []
		if s is None: s = self.s
		if bl is None and br is None: br = self.br; bl = self.bl
		if bl == br: 
			print(s)
			idxs = self.getChIdx(s, bl)
			print(idxs)
			if len(idxs) % 2 == 1: print('ERR: Upaired Braket.'); exit(1)
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
		if not self.checkPaired(idxs): print('ERR: Upaired Braket.'); exit(1)
		lt_rv = np.array(idxs['L'][::-1])
		rt = np.array(idxs['R'])
		dist = np.subtract.outer(rt, lt_rv).astype(float)					# 得到括号间的字符距离(右括号 - 左括号)
		dist[dist <= 0] = np.inf							# 舍弃负值
		for i in range(rt.size):							# 返回每个左括号最近的右括号(距离最小的右括号)
			min_dist_idx_row = int(np.argmin(dist[i, :]))
			pair.append((int(lt_rv[min_dist_idx_row]), int(rt[i])))
			#pair.append(int(lt_rv[min_dist_idx_row])); pair.append(int(rt[i]))
			dist[:, min_dist_idx_row] = np.inf
		if out == 'sorted': return sorted([item for pairr in pair for item in pairr])
		return pair




if __name__ == '__main__':
	ss = 'fasfdsa() ()(()(fa(fa)fa()((asdf)fdas)))'
	yy = PairMatcher(ss)
	print(yy.getPair(out='sorted'))
	print(' '.join([ss[i] for i in yy.getPair(out='sorted')]))

	ss = 'fasfdsa"hello" "wofada"  " "'
	yy = PairMatcher(ss, bl='"', br ='"')
	print(yy.getPair())
	print(' '.join([ss[i] for i in yy.getPair(out='sorted')]))

