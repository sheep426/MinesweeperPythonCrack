#coding:utf-8
import sys
from PyQt5.QtWidgets import QApplication, QWidget , QPushButton , QMessageBox,QGridLayout,QListWidget,QHBoxLayout
import sys
import psutil
import mine_injector

class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.init_game = False
        self.load_mine_data()

        if not self.init_game:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(u"请先运行winmine.exe")
            msg.setWindowTitle("错误")
            msg.exec_()
        else:
            self.do_layout()
        

    def do_layout(self):
        layout = QGridLayout()
        self.setLayout(layout)
        self.listwidget = QListWidget(self)
        col_count = self.mine_obj.get_col_data()
        row_count = self.mine_obj.get_row_data()
        mine_list = self.mine_obj.get_mine_list()
        row_counter = 0
        for row in range(1,row_count+1):
            for col in range(1,col_count+1):
                if mine_list[row][col]:
                    self.listwidget.insertItem(row_counter,u"第%s行 第%s列 为雷" %( row,col))
                    row_counter=row_counter+1
        
        self.auto_play_button = QPushButton(self)
        self.auto_play_button.setText(u"一件扫雷")
        self.auto_play_button.clicked.connect(self.click_auto_play)

        self.revert_time_button = QPushButton(self)
        self.revert_time_button.setText(u"时间归0")
        self.revert_time_button.clicked.connect(self.click_revert_time)
        

        self.stop_time_button = QPushButton(self)
        self.stop_time_button.setText(u"暂停计时")
        self.stop_time_button.clicked.connect(self.click_stop_time)
 
        self.disable_bome_button = QPushButton(self)
        self.disable_bome_button.setText(u"遇雷不失败")
        self.disable_bome_button.clicked.connect(self.click_disable_bome)


        layout.addWidget(self.listwidget,0,0,1,2)
        layout.addWidget(self.auto_play_button,1,0)
        layout.addWidget(self.stop_time_button,1,1)
        layout.addWidget(self.revert_time_button,2,0)
        layout.addWidget(self.disable_bome_button,2,1)

    def click_auto_play(self):
        self.mine_obj.auto_play()

    def click_revert_time(self):
        self.mine_obj.revert_time()

    def click_stop_time(self):
        self.mine_obj.stop_time()

    def click_disable_bome(self):
        self.mine_obj.disable_bome()

    def load_mine_data(self):
        pid_list = psutil.pids()
        found = False
        for pid  in pid_list:
            process_data = psutil.Process(pid)
            if process_data.name() == "winmine.exe":
                found = True
                break
        if found:
            self.mine_obj = mine_injector.mine_obj(pid)
            self.init_game = True
        else:
            self.init_game = False



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()

    w.resize(640,480)
    w.setWindowTitle("扫雷外挂")

    if w.init_game:
        print ("now show")
        w.show()
    sys.exit(app.exec_())