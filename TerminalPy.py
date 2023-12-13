import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QStyleFactory, QApplication, QDockWidget, QVBoxLayout


class SerialPort(QtWidgets.QMainWindow):
    def __init__(self):
        super(SerialPort, self).__init__()
        self.setWindowTitle("TerminalPy")
        QApplication.setStyle(QStyleFactory.create('Windows'))
        QApplication.setPalette(QApplication.style().standardPalette())

        self.port = QSerialPort()
        self.journal = Journal(self)
        self.send_data_menu = SendDataView(self)

        self.setCentralWidget(QtWidgets.QWidget(self))

        layout = QtWidgets.QVBoxLayout(self.centralWidget())
        layout.addWidget(self.journal)
        layout.addWidget(self.send_data_menu)

        self.toolbar = SettingsPort(self)
        self.left_menu = QDockWidget("Settings")
        self.left_menu.setWidget(self.toolbar)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.left_menu)

        self.toolbar.connect_button.clicked.connect(self.open_port)
        self.toolbar.rescan_button.clicked.connect(self.toolbar.update_list_ports)
        self.send_data_menu.send_serial_data_signal.connect(self.send_from_port)
        self.port.readyRead.connect(self.read_from_port)

    def open_port(self):
        if self.toolbar.connect_button.isChecked():
            try:
                self.port.setPortName(self.toolbar.current_port_name())
                self.port.setBaudRate(self.toolbar.current_baud_rate())
                self.port.setDataBits(self.toolbar.current_data_bits())
                self.port.setParity(self.toolbar.current_parity_bit())
                self.port.setStopBits(self.toolbar.current_stop_bit())
                self.port.setFlowControl(self.toolbar.current_flow_control())

                result_opening = self.port.open(QtCore.QIODevice.ReadWrite)
                self.toolbar.connect_button.setChecked(True)
            except:
                print("Error opening COM port: ", sys.exc_info()[0])
        else:
            self.port.close()
            self.toolbar.connect_button.setChecked(False)

    def read_from_port(self):
        serial_data = self.port.readAll()
        if len(serial_data) > 0:
            self.journal.show_data(QtCore.QTextStream(serial_data).readAll())

    def send_from_port(self, text):
        self.port.write(text.encode())
        self.journal.show_data(text)


class Journal(QtWidgets.QWidget):
    def __init__(self, parent):
        super(Journal, self).__init__(parent)
        self.serial_data = QtWidgets.QTextEdit(self)
        self.serial_data.setReadOnly(True)
        self.serial_data.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.setLayout(QtWidgets.QHBoxLayout(self))
        self.layout().addWidget(self.serial_data)

    def show_data(self, data):
        self.serial_data.moveCursor(QtGui.QTextCursor.End)
        self.serial_data.setFontFamily('Courier New')
        self.serial_data.setTextColor(QtGui.QColor(0, 0, 0))
        self.serial_data.insertPlainText(data)
        self.serial_data.moveCursor(QtGui.QTextCursor.End)


class SendDataView(QtWidgets.QWidget):
    send_serial_data_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super(SendDataView, self).__init__(parent)
        self.send_data = QtWidgets.QTextEdit(self)
        self.send_data.setAcceptRichText(False)
        self.send_data.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

        self.send_data_button = QtWidgets.QPushButton("Send")
        self.send_data_button.clicked.connect(self.send_button_clicked)

        self.setLayout(QtWidgets.QHBoxLayout(self))
        self.layout().addWidget(self.send_data)
        self.layout().addWidget(self.send_data_button)

    def send_button_clicked(self):
        self.send_serial_data_signal.emit(self.send_data.toPlainText())


class SettingsPort(QtWidgets.QWidget):

    def __init__(self, parent):
        super(SettingsPort, self).__init__(parent)

        self.connect_button = QtWidgets.QPushButton("Connect")
        self.connect_button.setCheckable(True)
        self.connect_button.setChecked(False)

        self.rescan_button = QtWidgets.QPushButton("Rescan")

        self.name_port = QtWidgets.QComboBox(self)
        self.name_port.addItems([port.portName() for port in QSerialPortInfo().availablePorts()])

        self.baud_rates = QtWidgets.QComboBox(self)
        self.baud_rates.addItems(['57600', '76800', '115200', '128000'])
        self.baud_rates.setCurrentText('115200')

        self.data_bits = QtWidgets.QComboBox(self)
        self.data_bits.addItems(['5 bit', '6 bit', '7 bit', '8 bit'])
        self.data_bits.setCurrentIndex(3)

        self.parity_bit = QtWidgets.QComboBox(self)
        self.parity_bit.addItems([
            'No Parity', 'Even Parity', 'Odd Parity', 'Space Parity', 'Mark Parity'
        ])
        self.parity_bit.setCurrentIndex(0)
        self.parity_dict = {
            'No Parity': 0, 'Even Parity': 2, 'Odd Parity': 3, 'Space Parity': 4, 'Mark Parity': 5
        }

        self.stop_bit = QtWidgets.QComboBox(self)
        self.stop_bit.addItems(['One Stop', 'One And Half Stop', 'Two Stop'])
        self.stop_bit.setCurrentIndex(0)
        self.stop_bit_dict = {'One Stop': 1, 'One And Half Stop': 3, 'Two Stop': 2}

        self.flow_control = QtWidgets.QComboBox(self)
        self.flow_control.addItems(['No Flow Control', 'Hardware Control', 'Software Control'])
        self.flow_control.setCurrentIndex(0)

        self.settings_layout = QVBoxLayout()
        self.settings_layout.addWidget(self.connect_button)
        self.settings_layout.addWidget(self.rescan_button)
        self.settings_layout.addWidget(self.name_port)
        self.settings_layout.addWidget(self.baud_rates)
        self.settings_layout.addWidget(self.data_bits)
        self.settings_layout.addWidget(self.parity_bit)
        self.settings_layout.addWidget(self.flow_control)
        self.settings_layout.addWidget(self.stop_bit)
        self.settings_layout.addStretch(1)
        self.setLayout(self.settings_layout)

    def update_list_ports(self):
        self.name_port.clear()
        self.name_port.addItems([port.portName() for port in QSerialPortInfo().availablePorts()])

    def current_port_name(self):
        return self.name_port.currentText()

    def current_baud_rate(self):
        return int(self.baud_rates.currentText())

    def current_data_bits(self):
        return int(self.data_bits.currentIndex() + 5)

    def current_parity_bit(self):
        return int(self.parity_dict.get(self.parity_bit.currentText()))

    def current_stop_bit(self):
        return int(self.stop_bit_dict.get(self.stop_bit.currentText()))

    def current_flow_control(self):
        return int(self.flow_control.currentIndex())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SerialPort()
    window.show()
    app.exec()

