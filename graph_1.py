import sys
import numpy as np
from PyQt5 import QtWidgets
import pyqtgraph as pg
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog
from qtgraph_test import Ui_MainWindow
import Functions as Func


class MyGraphWindow(QtWidgets.QMainWindow, Ui_MainWindow):

	def __init__(self):
		super(MyGraphWindow, self).__init__()
		self.data = self.LoadFile
		self.setupUi(self)  # 初始化窗口
		self.p1, self.win = self.set_graph_ui()
		# self.p2 = self.set_graph_ui()
		self.Button_LoadFile.clicked.connect(self.LoadFile)  # 加载文件按钮
		self.Button_Clear.clicked.connect(self.clear)  # 清屏按钮
		self.Button_xf.clicked.connect(self.Pu_XF)  # 寻峰按钮
		self.Button_PuGH.clicked.connect(self.Pu_GH)  # 谱光滑按钮
		global data
		global Peak_info
		data = 0
		Peak_info = '0'
		global Functions
		global Ep
		global Elp
		Ep = None
		Elp = None

	def set_graph_ui(self):
		pg.setConfigOptions(antialias=True)  # pg全局变量设置函数，antialias=True开启曲线抗锯齿
		win = pg.GraphicsLayoutWidget()  # 创建pg layout，可实现数据界面布局自动管理
		self.verticalLayout_2.addWidget(win)
		self.pin_label = pg.TextItem()
		self.fun_label = pg.TextItem()
		self.vLine = pg.InfiniteLine(angle=90, movable=False, )
		self.hLine = pg.InfiniteLine(angle=0, movable=False, )
		p1 = win.addPlot(title="能谱图像")  # 添加第一个绘图窗口
		# p1 = win.
		self.move_slot = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=self.print_slot)
		p1.setLabel('left', text='count', color='#6F7276')  # y轴设置函数
		p1.showGrid(x=True, y=True)  # 栅格设置函数
		p1.setLogMode(x=False, y=False)  # False代表线性坐标轴，True代表对数坐标轴
		p1.setLabel('bottom', text='chn', units='')  # x轴设置函数
		self.region = pg.LinearRegionItem(bounds=[0, 1024], swapMode='push')  # 添加选择区域
		self.region.setZValue(100)
		self.region.setRegion([351, 391])  # 设置为第一个峰的范围，第二条峰的范围为[481,515]

		return p1, win

	def clear(self):
		self.p1.clear()
		self.setWindowTitle('能谱软件V1.0')
		self.label_File_Info.setText('')
		self.label_Region_Info.setText('')

	def print_slot(self, event=None):
		global data
		global Peak_info
		if event is None:
			print("事件为空")
		else:
			pos = event[0]  # 获取事件的鼠标位置
			try:
				# 如果鼠标位置在绘图部件中
				if self.p1.sceneBoundingRect().contains(pos):
					mousePoint = self.p1.vb.mapSceneToView(pos)  # 转换鼠标坐标
					index = int(mousePoint.x())  # 鼠标所处的X轴坐标
					self.vLine.setPos(mousePoint.x())
					self.hLine.setPos(mousePoint.y())
					if -1 < index < 1025:
						self.pin_label.setHtml(
							"<span>Chn:{0}</span><br><span>Count:{1}</span>".format(index, data[index]))
						self.pin_label.setPos(mousePoint.x() + 15, mousePoint.y() + 15)  # 设置label的位置
					self.p1.sigRangeChanged.connect(self.Up_Region(Peak_info))
			except Exception as e:
				print(end='')

	def LoadFile(self):
		global data
		global Src_data
		dialog = QFileDialog()
		my_file_path = dialog.getOpenFileName(self, "打开文件", "./", "*.mca")
		self.Draw_Spec(my_file_path, 0)

	def Pu_GH(self):
		global data
		try:
			if data == 0:
				QMessageBox.information(self, '警告', '未加载能谱文件！', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
				return 0
		except ValueError:
			step = ['3', '5']
			chn_n = QInputDialog.getItem(self, '平均移动法', '请选择移动点数', step)
			if chn_n[1]:
				Data = Func.Pu_GH(data, chn_n[0])
				self.Draw_Spec([], Data)

	def Pu_XF(self):
		global Peak_info
		global Src_data
		global T_Feng
		global A_Feng
		global Ep
		global Elp

		T_Feng = []
		A_Feng = []
		zuo, you = self.region.getRegion()
		step = ['5', '7', '9', '11']
		chn_n = QInputDialog.getItem(self, '一阶导数法', '请选择点数', step)
		if chn_n[1]:
			Fwhm = QInputDialog.getInt(self, '设置半高宽', 'FWHM:', value=10)
			if Fwhm[1]:
				Feng, num = Func.Pu_Xf(Src_data[int(zuo): int(you + 1)], int(chn_n[0]), Fwhm[0])
				if num == 0:
					QMessageBox.information(self, '识别失败', '当前选区过小或没有符合条件的峰，请修改选区再试！', QMessageBox.Yes | QMessageBox.No,
					                        QMessageBox.Yes)
				else:
					for F in range(len(Feng)):
						if F % 3 == 0:
							self.p1.plot([Feng[F] + int(zuo), Feng[F] + int(zuo)],
							             [0, Src_data[int(zuo) + Feng[F + 1]]], pen='y')
						elif (F + 1) % 3 == 0:
							self.p1.plot([Feng[F] + int(zuo), Feng[F] + int(zuo)],
							             [0, Src_data[int(zuo) + Feng[F - 1]]], pen='y')
						else:
							self.p1.plot([Feng[F - 1] + int(zuo), Feng[F + 1] + int(zuo)],
							             [Src_data[int(zuo) + Feng[F]], Src_data[int(zuo) + Feng[F]]], pen='y')
				Peak_info = '''
				<b>选区信息</b><br>
				起始:<font color='red'>%d</font><br>
				结束:<font color='red'>%d</font><br>
				峰数:<font color='red'>%d</font>
				''' % (int(zuo), int(you), num)
				if Ep is None:
					dialog = QFileDialog()
					Ep = dialog.getOpenFileName(self, "加载刻度文件", "./", "*.cal")[0]
				if Elp is None:
					dialog = QFileDialog()
					Elp = dialog.getOpenFileName(self, "加载元素数据库", './', '*.lib')[0]
				for F in range(0, len(Feng), 3):
					t_Feng, a_Feng = Func.Pu_Mj(Src_data[Feng[F] + int(zuo):Feng[F + 2] + int(zuo)], Feng[F + 1], 12)
					Eng, Elm = Func.Pu_Sb(Ep, Elp, (Feng[F+1] + int(zuo)))
					Feng_label = pg.TextItem()
					Feng_label.setText('峰面积:%.2f\n净峰面积:%.2f\n元素:%s' % (t_Feng, a_Feng, Elm), color='red')
					Feng_label.setPos(Feng[F+2] + int(zuo), Src_data[Feng[F + 1] + int(zuo)])
					self.p1.addItem(Feng_label)
					T_Feng.append(t_Feng)
					A_Feng.append(a_Feng)

	def Up_Region(self, Peak_info):
		if Peak_info == '0':
			Peak_info = '''<b>选区信息</b><br>
			起始:<font color='red'>%d</font><br>
			结束:<font color='red'>%d</font>''' % (self.region.getRegion())
		self.label_Region_Info.setText(Peak_info)

	def Draw_Spec(self, path, Data):
		global data
		global Src_data
		try:
			if path[0] != "":  # 防止空操作报错
				# chn = ['1024', '2048']
				# chn_n = QInputDialog.getItem(self, '道址', '请选择数据文件道址数', chn)
				data = np.fromfile(path[0], dtype=np.int32, offset=230)  # 跳过文件开头的32个信息字节
				Time = np.fromfile(path[0], dtype=np.int32, offset=68)
				# print(Time[:6])  #  八位数据分别为，LiveTime,RealTime,DeadTime,能量刻度系数a,b,总道数
				Live_time = Time[0]
				Real_time = Time[1]
				Dead_time = Time[2]
				chn_n = Time[5]
				Src_data = data[:chn_n]
				self.setWindowTitle('能谱软件V1.0  Load File:' + path[0])
				if Data == 0:
					File_info = '''<b>File Info</b><br>
活时间:%d<br>
真时间:%d<br>
死时间:%d<br>
道址数:%d''' % (Live_time, Real_time, Dead_time, chn_n)
					self.label_File_Info.setText(File_info)
				x = np.arange(0, chn_n, 1)
				self.p1.setXRange(-1, chn_n, padding=0)
				self.p1.setYRange(0, max(data), padding=0)
				self.p1.plot(x, data[:chn_n], pen='g', name=path[0], clear=True)
				# self.p1.addItem(pg.BarGraphItem(x=x, height=data[:chn_n], weight=0.5, bursh='r'))
				self.p1.addItem(self.vLine, ignoreBounds=True)
				self.p1.addItem(self.hLine, ignoreBounds=True)
				self.p1.addItem(self.pin_label)
				self.p1.addItem(self.region)
		except IndexError:
			chn_n = len(Data)
			self.p1.setYRange(-1, max(Data), padding=0)
			self.p1.setXRange(0, chn_n, padding=0)
			Flag = QMessageBox.information(self, '提示', '是否保留原始谱线?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
			# print(Flag)
			if Flag == 16384:  # 选择Yes的返回值
				cl = 0
			elif Flag == 65536:
				cl = 1
			self.p1.plot(range(0, chn_n), Data, pen='r', name='平滑谱线', clear=cl)
			self.p1.addItem(self.vLine, ignoreBounds=True)
			self.p1.addItem(self.hLine, ignoreBounds=True)
			self.p1.addItem(self.pin_label)
			self.p1.addItem(self.region)


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	myWin = MyGraphWindow()
	myWin.show()
	sys.exit(app.exec_())
