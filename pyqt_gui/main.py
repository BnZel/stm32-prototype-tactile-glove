from __init__ import *

class SerialThread(QThread):
    data_received = pyqtSignal(str)             # in init_serial(response) then processed to format_serial_data()
    exception = pyqtSignal(str,str)             # for custom_dialog(title,message)

    def __init__(self,port="/dev/ttyACM0",baudrate="9600",timeout=1):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.running = False

    def run(self):
        self.running = True
        try:
            with serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout) as self.ser:
                while self.running:
                    response = self.ser.readline().decode("utf-8").strip()
                    if response:
                        # in format_serial_data()
                        self.data_received.emit(response)

        # in custom_dialog()
        except serial.SerialException as e:
            self.exception.emit(f"SERIAL ERROR", str(e))
        except FileNotFoundError:
            self.exception.emit("CONNECTION ERROR","Port not found, check device connection...")
        except PermissionError:
            self.exception.emit("PERMISSION DENIED","Permission denied, remember to add yourself to dialout group...")

    def stop(self):
        self.running = False
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GUI Sensor Glove V3")

        # non-blocking thread for reading
        # microcontrollers serial output
        self.serial_thread = SerialThread()

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        self.init_ui()

        main_layout.addLayout(self.serial_layout,1)

        # NOTE: POSTPONED FOR ACCURATE FSR SENSORS
        # main_layout.addLayout(self.heatmap_layout,2)

        main_layout.addLayout(self.grams_layout,2)
        main_layout.addLayout(self.pots_layout,2)
        self.setCentralWidget(central_widget)


    def custom_dialog(self,title,message):
        self.stop_serial()
        dialog = QMessageBox.information(None,title,message,QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if dialog == QMessageBox.StandardButton.Yes:
            self.init_serial()
        elif dialog == QMessageBox.StandardButton.No:
            self.stop_serial()

    def format_serial_data(self,response):
        try:
            data = response.split(",")
            if len(data) == 8:
                self.end_time = time.time()
                self.elapsed_time = self.end_time - self.start_time
                self.pot1_angle, self.pot2_angle, self.grams_dp, self.status_dp, self.grams_mp, self.status_mp, self.grams_pp, self.status_pp = data
                self.plot()
                self.serial_textarea.appendPlainText(response)
                self.serial_textarea.moveCursor(QTextCursor.MoveOperation.End)
            else:
                data = f"Incomplete Data Transmission... {response}"
                self.serial_textarea.appendPlainText(data)
                self.serial_textarea.moveCursor(QTextCursor.MoveOperation.End)

        except csv.Error as e:
            self.custom_dialog("CSV ERROR",str(e))
        except Exception as e:
            self.custom_dialog("UNEXPECTED ERROR",str(e))

    def clear_plot(self):
        # once serial connection stops
        # clear plot data 
        # and wait for replotting when restarting
        self.g_dp.clear()
        self.g_mp.clear()
        self.g_pp.clear()

        self.pot1.clear()
        self.pot2.clear()

    def stop_serial(self):
        self.button_start_serial.setDisabled(False) 
        self.button_stop_serial.setDisabled(True)
        self.serial_textarea.clear()
        self.clear_plot()

        if self.serial_thread and self.serial_thread.isRunning():
            self.serial_thread.stop()

    def init_serial(self):
        self.button_start_serial.setDisabled(True) 
        self.button_stop_serial.setDisabled(False)

        # signal thread worker to process
        # raw serial output in the background
        # and dialog display
        if self.serial_thread is None or not self.serial_thread.isRunning():
            self.start_time = time.time()
            self.serial_thread = SerialThread()
            self.serial_thread.data_received.connect(self.format_serial_data)
            self.serial_thread.exception.connect(self.custom_dialog)

            self.serial_thread.start()

    # on program close
    # make sure thread is completely closed
    # and serial port is closed
    def closeEvent(self,event):
        self.stop_serial()
        event.accept()

    def init_ui(self):
        self.serial_layout = QVBoxLayout()
        self.heatmap_layout = QVBoxLayout()
        self.grams_layout = QVBoxLayout()
        self.pots_layout = QVBoxLayout()
        
        self.button_start_serial = QPushButton("CONNECT Serial")
        self.button_start_serial.setCheckable(True)
        self.button_start_serial.clicked.connect(self.init_serial)

        self.button_stop_serial = QPushButton("STOP Serial")
        self.button_stop_serial.setCheckable(False)
        self.button_stop_serial.setDisabled(True)
        self.button_stop_serial.clicked.connect(self.stop_serial)

        self.serial_textarea = QPlainTextEdit()
        self.serial_textarea.setReadOnly(True)

        self.serial_layout.addWidget(self.button_start_serial)
        self.serial_layout.addWidget(self.button_stop_serial)
        self.serial_layout.addWidget(self.serial_textarea)

        # NOTE: POSTPONED FOR ACCURATE FSR SENSORS
        # label_heatmap = QLabel("HEATMAP")
        # label_heatmap.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        # self.heatmap_layout.addWidget(label_heatmap)
        # self.hm_dp, self.left_label_hm_dp, self.bottom_label_hm_dp = self.create_live_plots("DISTAL PHALANGES",1,100,"h")
        # self.hm_mp, self.left_label_hm_mp, self.bottom_label_hm_mp  = self.create_live_plots("MIDDLE PHALANGES",1,100,"h",resolution=1)
        # self.hm_pp, self.left_label_hm_pp, self.bottom_label_hm_pp = self.create_live_plots("PROXIMAL PHALANGES",1,100,"h")

        label_grams = QLabel("GRAMS - y:GRAMS | x:time")
        label_grams.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.grams_layout.addWidget(label_grams)
        self.g_dp, self.title_g_dp = self.create_live_plots("DISTAL PHALANGES",5000,100,"g")
        self.g_mp, self.title_g_mp = self.create_live_plots("MIDDLE PHALANGES",5000,100,"g")
        self.g_pp, self.title_g_pp = self.create_live_plots("PROXIMAL PHALANGES",5000,100,"g")

        label_pots = QLabel("POTENTIOMETERS - [y:ANGLE (DEG) | x:time]")
        label_pots.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.pots_layout.addWidget(label_pots)
        self.pot1 = self.create_live_plots("DISTAL PHALANGES",330,100,"p")
        self.pot2 = self.create_live_plots("MIDDLE PHALANGES",330,100,"p")

    def plot(self):
        # updates on all liveplot widgets dataconnector
        if self.serial_thread and self.serial_thread.isRunning():
            # grams
            self.title_g_dp.setTitle(f"DISTAL PHALANGES - {self.status_dp}")
            self.title_g_mp.setTitle(f"MIDDLE PHALANGES - {self.status_mp}")
            self.title_g_pp.setTitle(f"PROXIMAL PHALANGES - {self.status_pp}")
            
            self.g_dp.cb_append_data_point(y=float(self.grams_dp),x=self.elapsed_time)
            self.g_mp.cb_append_data_point(y=float(self.grams_mp),x=self.elapsed_time)
            self.g_pp.cb_append_data_point(y=float(self.grams_pp),x=self.elapsed_time)

            # potentiometer
            self.pot1.cb_append_data_point(y=float(self.pot1_angle),x=self.elapsed_time)
            self.pot2.cb_append_data_point(y=float(self.pot2_angle),x=self.elapsed_time)
            

    def create_live_plots(self,name,max_points,update_rate,g_h_p,resolution=3):

        # depending what g_h_p (grams heatmap potentiometer) 
        # is passed, it returns the plot widget
        # so the title can be self updating
        # to provide status (see plot function)
        # and to clear data (through data_connector)
        if g_h_p == "g":
            plot_widget = LivePlotWidget(title=name)
            plot_curve = LiveLinePlot()
            plot_widget.addItem(plot_curve)
            data_connector = DataConnector(plot_curve,max_points,update_rate)
            self.grams_layout.addWidget(plot_widget) 

            return data_connector, plot_widget
        
        elif g_h_p == "p":
            plot_widget = LivePlotWidget(title=name)
            plot_curve = LiveLinePlot()
            plot_widget.addItem(plot_curve)
            data_connector = DataConnector(plot_curve,max_points,update_rate)
            self.pots_layout.addWidget(plot_widget)

            return data_connector

        # NOTE: POSTPONED FOR ACCURATE FSR SENSORS
        # elif g_h_p == "h":
        #     plot_heatmap = LiveHeatMap(pg.colormap.get("CET-D1"), grid_pen=pg.mkPen("red"), counts_pen=pg.mkPen("white"))
        #     left_labels = [f"Y{y}" for y in range(resolution)]
        #     bottom_labels = [f"X{x}" for x in range(resolution)]

        #     left_axis = LiveAxis("left",tick_angle=0,**{Axis.TICK_FORMAT: Axis.CATEGORY, Axis.CATEGORIES: left_labels, Axis.SHOW_ALL_CATEGORIES: True})
        #     right_axis = LiveAxis("right",tick_angle=0,**{Axis.TICK_FORMAT: Axis.CATEGORY, Axis.CATEGORIES: left_labels, Axis.SHOW_ALL_CATEGORIES: False})

        #     top_axis = LiveAxis("top", tick_angle=0, **{Axis.TICK_FORMAT: Axis.CATEGORY, Axis.CATEGORIES: bottom_labels, Axis.SHOW_ALL_CATEGORIES: True})
        #     bottom_axis = LiveAxis("bottom", tick_angle=0, **{Axis.TICK_FORMAT: Axis.CATEGORY, Axis.CATEGORIES: bottom_labels, Axis.SHOW_ALL_CATEGORIES: False})

        #     plot_widget = LivePlotWidget(title=name,axisItems={"top": top_axis, "bottom": bottom_axis, "left": left_axis, "right": right_axis})

        #     plot_widget.addItem(plot_heatmap)
        #     data_connector = DataConnector(plot_heatmap,max_points,update_rate)
        #     self.heatmap_layout.addWidget(plot_widget)
            
        #     return data_connector, left_labels, bottom_labels
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
