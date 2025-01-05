import sys,os
from PyQt5.QtWidgets import QMainWindow,QWidget, QVBoxLayout,QScrollArea,QMessageBox,QTextBrowser
from PyQt5 import uic, QtWidgets
from windows.window2 import ventana2
from windows.window3 import ventana3
from globals import shared_data
from utils.helpers import *

my_dictionary = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
len_dictionary = len(my_dictionary)
config_path = os.path.join(os.path.dirname(__file__),'..', '..','config.json')
data_file = load_data(config_path)

class ventana1(QMainWindow):
    file_addr = ""
    def __init__(self):
        super().__init__()
        ruta_ui = os.path.join(os.path.dirname(__file__), '..','resources', 'ui', 'main_window.ui')
        uic.loadUi(ruta_ui,self)
        self.set_database.clicked.connect(self.link_crud_window)
        self.practice_main.clicked.connect(self.link_practice_window)
        self.update_tab.clicked.connect(self.update_tab_main)
        self.actionSavefile.setEnabled(False)
        self.actionFilePath.setEnabled(False)
        self.actionOpenfile.triggered.connect(self.openJSON)
        self.actionNewFile.triggered.connect(self.createJSON)
        self.actionSavefile.triggered.connect(self.saveJSON)
        self.actionFilePath.triggered.connect(self.show_filepaht)
        self.actionAbout.triggered.connect(self.show_info_program)
        self.load_file_if_upload_path()

    def load_file_if_upload_path(self):
        try:
            file_path_data = data_file["default_path"]
            if file_path_data!="":
                print("path establecido, cargamos los datos")
                self.data = load_data(file_path_data)
                shared_data["path"] = file_path_data
                self.update_list_word()
                self.update_tab_main()        
                self.file_data_json_uploaded()
            else:
                print("sin ruta por defecto")
        except:
            QMessageBox.warning(self, 'Warning', 'Error uploading file "config.json"', QMessageBox.Ok)
            sys.exit(1)

    def show_info_program(self):
        QMessageBox.information(self, 'Info', f"       <font color='red'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>DictioLearn v1.6</font><br><br>Python version: {sys.version.split()[0]} <br>GUI: PyQt5 and QtDesigner<br>Text-to-speech library: Pyttsx3", QMessageBox.Ok)

    def file_data_json_uploaded(self):
        if hasattr(self,"ventana_aux"):#si existe, primero cerramos las otras ventanas y eliminamos
            self.crud_database_window.close()
            self.crud_database_window.deleteLater()
            self.practice_database_window.close()
            self.practice_database_window.deleteLater()
        self.crud_database_window = ventana2(self.data,self.practice_main) #evitar cargar los datos nuevamente porque se puede desincronizar
        self.practice_database_window = ventana3(self.data,self.set_database)  #tambien enviamos el widget de esta ventana que usaremos en las otras ventanas
        self.set_database.setEnabled(True)
        self.practice_main.setEnabled(True)
        self.update_tab.setEnabled(True)
        self.actionFilePath.setEnabled(True)
        self.actionSavefile.setEnabled(True)
        self.crud_database_window.signal_update_data.connect(self.update_list_word)

    def openJSON(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/',"JSON files (*.json)")
        if filePath != "":
            shared_data["path"] = filePath
            self.data = load_data(filePath)
            self.update_list_word()
            self.update_tab_main()        
            self.file_data_json_uploaded()
            data_file["default_path"] = filePath
            save_data(data_file,config_path)
            QMessageBox.information(self, 'Info', 'New file uploaded!', QMessageBox.Ok)


    def show_filepaht(self):
        QMessageBox.information(self, 'File Path', f'{shared_data["path"]} ', QMessageBox.Ok)

    def saveJSON(self):
        filePath, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', '/dictio', "JSON files (*.json)")
        if filePath != "":
            save_data(self.data,filePath)
            QMessageBox.information(self, 'Info', "File saved successfully.", QMessageBox.Ok)

    def createJSON(self):
        filePath, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', '/dictio', "JSON files (*.json)")
        if filePath != "":
            shared_data["path"] = filePath
            self.data = []
            save_data(self.data,filePath)
            #borramos las tablas, ya que es un archivo nuevo
            self.last_five_words.clear()
            self.tab_main.clear()
            self.file_data_json_uploaded()
            data_file["default_path"] = filePath
            save_data(data_file,config_path)
            QMessageBox.information(self, 'Info', "New file created successfully.", QMessageBox.Ok)

    def update_list_word(self):
        self.last_five_words.clear()
        #print("update list") #depuración
        i = len(self.data) + 1
        for K in range(1,min(6,i),1):
            self.last_five_words.addItem(self.data[-K]["word"])

    def update_tab_main(self):
        self.label_tab.setText(f"Dictionary {len(self.data)} + Points")
        self.tab_main.clear()

        # Crear las pestañas dinámicamente
        for i,letter in enumerate(my_dictionary):
            tab_pri = QWidget()
            layout2 = QVBoxLayout(tab_pri)

            # Filtrar los datos por la letra actual
            resultados, cantidad = filter_by_letter(self.data, letter)
            list4 = QTextBrowser()

            if cantidad > 0:
                for item in resultados:
                    color = get_color(item["points"])
                    format_one = '<span style="color:' + color+';">{}</span>'
                    aux_text = item["word"] +"  " + str(item["points"])
                    list4.append(format_one.format(aux_text))

            # Crear un área de desplazamiento para el QLabel
            scrollArea2 = QScrollArea()
            scrollArea2.setWidget(list4)#label2
            scrollArea2.setWidgetResizable(True)
            layout2.addWidget(scrollArea2)

            tab_pri.setLayout(layout2)
            self.tab_main.addTab(tab_pri, f"{letter}\n{cantidad}") 


    def link_crud_window(self):
        self.practice_main.setEnabled(False)
        self.crud_database_window.show()

    def link_practice_window(self):
        if not self.data:
            QMessageBox.warning(self, 'Warning', 'First, you need to create data.', QMessageBox.Ok)
        else:
            self.set_database.setEnabled(False)

            self.practice_database_window.select_case.setCurrentIndex(0)
            self.practice_database_window.my_word.setText("")
            self.practice_database_window.show()