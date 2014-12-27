#!-*-coding:utf-8-*-
import serial
import time
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
class X305ThRead(QThread):
    msgProgress = pyqtSignal(str)
    SZUProgress = pyqtSignal(str)
    stopRun=False
    def __init__(self,port, Item305):
        QThread.__init__(self)
        self.port= port
        self.Item305=Item305
    def Stop(self):
        self.stopRun=True
    def msgRead(self,data):
        self.msgProgress.emit(('<b><font color=green>{}</font>').format(data))
    def msgWrite(self,data):
        self.msgProgress.emit(('<b><font color=#900000>{}</font>').format(data))
    def getSZU(self,data):
        if(data[0]!=0x10): return
        if(data[1]!=0x03): return
        if(data[2]==0x01):
            self.SZUProgress.emit('background-color: red;')
            print('szu.ON')
        if(data[2]==0x02):
            print('szu.OFF')
            self.SZUProgress.emit('')
    def formData(self,data):
        dataW=[0]*7
        if data[0]!=0x10: return bytes(dataW);
        if data[1]!=0x04 : return bytes(dataW);
        dataW[0]=data[0]
        dataW[1]=data[1]
        dataW[2]=data[2]
        rs=0
        ri=0
        for iInChannel in range(0,8):
            if(self.Item305[iInChannel][0].isChecked()):
                rs=rs|(1<<iInChannel)
            else:
                rs=rs|(0<<iInChannel)
            if(self.Item305[iInChannel][1].isChecked()):
                ri=ri|(1<<iInChannel)
            else:
                ri=ri|(0<<iInChannel)

        dataW[3]=0x02
        dataW[4]=rs
        dataW[5]=ri
        dataW[6]=0xda

        return bytes(dataW)
    def run(self):
        ser = serial.Serial(self.port,19200)
        ser.open()
        print('PortOpen=',ser.isOpen())

        while not self.stopRun:


            data=ser.read()
            time.sleep(0.01)
            dataLeft=ser.inWaiting()
            data += ser.readline(dataLeft)
            #print(data)
            self.msgRead(data)
            self.getSZU(data)
            dr=self.formData(data)
            self.getSZU(data)
            self.msgWrite(dr)
            ser.write(dr)
        port.close()
        print('runClose')

    def __del__(self):
        print('delThReadPort')
class emulICPDAS(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        ports=['AD0|NEK1- Место хр.k.',
               'AD1|РВ1- Место хр.к.',
               'AD2|РВ2- Трав.ванны',
               'AD3|РВ3- Трав.ванны',
               'AD4|NEK2- Трав.ванны',
               'AD5|SSS-903 - Level1',
               'AD6|SSS-903 - Level2',
               'DI0|SSS-903 - FAULT|',
               'DO0|Светавое табло']

        vSpacer = QSpacerItem(1,1,QSizePolicy.Ignored,QSizePolicy.Expanding)

        gbPort= QGroupBox('Settings')
        gbX305= QGroupBox('X305')


        grid0=QGridLayout(self)
        grid0.addWidget(gbPort,0,0)
        grid0.addWidget(gbX305,1,0,2,1)

        grid0.addItem(vSpacer,3,0)

        gridPort=QGridLayout(gbPort)
        gridX305 = QGridLayout(gbX305)
        self.linePort=QLineEdit('/dev/COM7')
        self.linePort.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed)
        label = QLabel('Port:')
        label.setAlignment(Qt.AlignRight)
        self.bPort = QPushButton('Open')
        self.bPort.setCheckable(True)
        self.bPort.clicked.connect(self.bStart)
        self.textEdit= QPlainTextEdit()
        self.textEdit.setMaximumBlockCount(100)
        self.textEdit.setStyleSheet("background-color: rgb(0, 0, 100);")
        gridPort.addWidget(label,0,0)
        gridPort.addWidget(self.linePort,0,1)
        gridPort.addWidget(self.bPort,0,2)
        grid0.addWidget(self.textEdit,0,1,0,1)
        i=0
        color=['','background-color: rgb(255, 0, 0)'];
        self.Items=[]
        for p in ports:
            subItem=[]
            a=p.split('|')
            cb1= QCheckBox(a[0])
            cb1.setLayoutDirection(Qt.RightToLeft)


            line = QLineEdit(a[1])
            line.setFixedWidth(150)
            line.setReadOnly(True)
            line.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed)
            cb2= QCheckBox()
            gridX305.addWidget(cb1,i,0)
            gridX305.addWidget(line,i,1)
            gridX305.addWidget(cb2,i,2)
            subItem.append(cb1)
            subItem.append(cb2)
            subItem.append(line)
            self.Items.append(subItem)
            i+=1

    def bStart(self):
        if not self.bPort.isChecked():
            self.bPort.setText('Open')
            print('ClosePort')
            self.Items[0][1].setChecked(False)
            self.writeMessage('PortClose')
            self.a.Stop()
            self.a.terminate()
            del self.a
        else:
            self.bPort.setText('Close')

            print('OpenPort')
            self.writeMessage('PortOpen')
            self.a= X305ThRead(self.linePort.text(),self.Items)
            self.a.msgProgress.connect(self.writeMessage)
            self.a.SZUProgress.connect(self.Items[8][2].setStyleSheet)
            self.a.start()
    def writeMessage(self, msg):
        txt=('<font color=gray>[{}]</font>: {}').format(QTime.currentTime().toString(),msg)
        self.textEdit.appendHtml (txt)


        pass
    def __del__(self):
        pass












