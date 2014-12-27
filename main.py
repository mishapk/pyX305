
import sys
from PyQt4 import QtCore, QtGui  
import x305

 
def main():
    app = QtGui.QApplication(sys.argv)  
    form = x305.emulICPDAS()
    form.show()

    app.exec()  
 
if __name__ == "__main__":
    sys.exit(main())