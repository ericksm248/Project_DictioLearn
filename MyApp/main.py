import sys
from PyQt5 import QtWidgets

from windows.window1 import ventana1

if __name__ == "__main__":
    app =  QtWidgets.QApplication(sys.argv)
    window = ventana1()
    window.show()
    sys.exit(app.exec_())