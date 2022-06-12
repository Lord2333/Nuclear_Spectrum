def Pu_GH(data, step):
	"""
	算术滑动平均法谱光滑函数

	:param data:能谱计数数组
	:param step:光滑点数1 or 2
	:return:光滑后数组
	"""
	Temp_data = []  # 临时数组用于储存光滑变化后的结果
	if step == 1:  # 根据输入的step点数选择不同的计算公式
		for i in range(len(data)):
			if i == 0 or i == len(data) - 1:
				Temp_data.append(data[i])  # 输入数据处于开头和最后则直接将源数据存入数组
				continue
			bar_data = (data[i - 1] + data[i] + data[i + 1]) / 3
			Temp_data.append(bar_data)
	else:
		for i in range(len(data)):
			if i <= 1 or i >= len(data) - 2:
				Temp_data.append(data[i])
				continue
			bar_data = (data[i - 2] + data[i - 1] + data[i] + data[i + 1] + data[i + 2]) / 5
			Temp_data.append(bar_data)
	return Temp_data #  返回临时数组，包含了光滑后的能谱数据


def Pu_Xf(Data, step, fwhm):
	'''
	能谱寻峰，一阶导数寻峰算法
	:param Data: 能谱数据
	:param step: 寻峰点数取值范围：5,7,9,11
	:param fwhm: 半高宽，实测取10时寻峰效果最佳
	:return : res_Feng: 寻得峰及峰边界，每三个数字为一组数据[左边界,峰顶,右边界]；num: 寻得峰个数
	'''
	Temp_data = []
	zuo = 0
	you = 0
	zhong = 0
	Feng = []
	res_Feng = []
	if step == 5:
		for i in range(len(Data)):
			if i <= 1 or i >= len(Data) - 2:
				Temp_data.append(0)
				continue
			bar_data = (Data[i - 2] - 8 * Data[i - 1] + 8 * Data[i + 1] - Data[i + 2]) / 12
			Temp_data.append(bar_data)
	elif step == 7:
		for i in range(len(Data)):
			if i <= 2 or i >= len(Data) - 3:
				Temp_data.append(0)
				continue
			bar_data = (22 * Data[i - 3] - 67 * Data[i - 2] - 58 * Data[i - 1] + 58 * Data[i + 1] + 67 * Data[
				i + 2] - 22 * Data[i + 3]) / 252
			Temp_data.append(bar_data)
	elif step == 9:
		for i in range(len(Data)):
			if i <= 3 or i >= len(Data) - 4:
				Temp_data.append(0)
				continue
			bar_data = (86 * Data[i - 4] - 142 * Data[i - 3] - 193 * Data[i - 2] - 126 * Data[i - 1] + 126 * Data[
				i + 1] + 193 * Data[i + 2] + 142 * Data[i + 3] - 86 * Data[i + 4]) / 1188
			Temp_data.append(bar_data)
	elif step == 11:
		for i in range(len(Data)):
			if i <= 4 or i >= len(Data) - 5:
				Temp_data.append(0)
				continue
			bar_data = (300 * Data[i - 5] - 294 * Data[i - 4] - 532 * Data[i - 3] - 503 * Data[i - 2] - 296 * Data[
				i - 1] + 296 * Data[i + 1] + 503 * Data[i + 2] + 532 * Data[i + 3] + 294 * Data[i + 4] - 300 * Data[
				            i + 5]) / 5148
			Temp_data.append(bar_data)
	flag = 0
	for F in range(0, len(Temp_data)):
		if flag == 0 and ((Temp_data[F] < 0 and Temp_data[F + 1] > 0) or (Temp_data[F - 1] < 0 and Temp_data[F] > 0)):
			zuo = F + 1
			flag = 1
		elif flag == 1 and Temp_data[F] > 0 and Temp_data[F + 1] < 0:
			zhong = F + 1
			flag = 2
		elif flag == 2 and Temp_data[F] < 0 and Temp_data[F + 1] > 0:
			you = F + 1
			flag = 0
			Feng.append(zuo)
			Feng.append(zhong)
			Feng.append(you)
	for F_c in range(0, len(Feng), 3):
		# temp_feng = Temp_data[F_c]
		try:
			zuo = Feng[F_c]
			you = Feng[F_c + 2]
			for i in range(len(Temp_data[zuo:you])):
				if Temp_data[zuo + i] == max(Temp_data[zuo:you]):
					Lb = i
				elif Temp_data[zuo + i] == min(Temp_data[zuo:you]):
					Rb = i
					break
			N = Rb - Lb
			if 0.8 * fwhm <= N <= 3 * fwhm:
				res_Feng.append(Feng[F_c])
				res_Feng.append(Feng[F_c + 1])
				res_Feng.append(Feng[F_c + 2])
		except IndexError:
			break
	# print(res_Feng)
	num = len(res_Feng) / 3
	return res_Feng, num


def Pu_Mj(Data, Feng, n):
	"""
	峰面积函数，使用瓦森算法计算峰面积
	:param Data:待求峰能量，起始值分别为峰边界的值
	:param Feng:待求峰峰顶坐标
	:param n: 窄峰的减小道数
	:return: sum: 总峰面积，A：净峰面积
	"""
	b_fn = (Data[-1] - Data[0]) / len(Data) * (Feng - n) + Data[0]
	b_n = (Data[-1] - Data[0]) / len(Data) * (Feng + n) + Data[0]
	B = (b_fn + b_n) * (n + 0.5)
	A = sum(Data) - B
	return sum(Data), A


def Pu_Sb(F_path, Eng_path, Src_eng):
	'''
	核素识别，默认误差范围为5%
	:param F_path:
	:param Eng_path:
	:param Src_eng:
	:return:
	'''
	Eng = []
	Elm = 'None!'
	with open(F_path, 'r') as Fp:
		Fun = Fp.readline().split('\t')
		A = float(Fun[0])
		B = float(Fun[1][:-1])
	Real_eng = Src_eng * B + A
	with open(Eng_path, 'r') as Ep:
		for line in Ep.readlines():
			Eng.append(line.replace('\n', '').split(','))
	for eng in Eng:
		if float(eng[0]) * 0.95 <= Real_eng <= float(eng[0]) * 1.05:
			Elm = eng[1]
			break
	return Real_eng, Elm


if __name__ == '__main__':
	# fwhm = 10  # 目测得半高宽为24
	# step = 11
	# data = np.fromfile('./data/Gss5-6.mca', dtype=np.int32, offset=230)[:1024]
	# GH_data, num = Pu_Xf(data[340:410], step, fwhm)
	# plt.figure(figsize=(16, 9))
	# plt.title('FWHM=%d, Step=%d' % (fwhm, step))
	# plt.plot(range(1, 71), data[340:410], 'r')
	# plt.plot(GH_data, data[GH_data], 'b*')
	# plt.show()
	# Data = data[354:393]
	# Feng = GH_data[1] - GH_data[0]
	# n = 12
	# plt.figure(figsize=(16, 9))
	# plt.plot(Data, 'b')
	# plt.plot([0, 38], [Data[0], Data[-1]], 'r')
	# plt.plot([Feng - n, Feng - n], [0, Data[Feng - n]], 'r')
	# plt.plot([Feng + n, Feng + n], [0, Data[Feng + n]], 'r')
	# plt.show()
	# print(Pu_Mj(Data, Feng, n))
	print(Pu_Sb('data/energy.cal', 'data/element.lib', 410))
