
import os
from PyQt5.QtWidgets import QMainWindow,QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from globals import shared_data
from utils.helpers import *

class ventana2(QMainWindow):
    # Definir una señal que enviará datos
    signal_update_data = pyqtSignal()
    #signal_delete_data = pyqtSignal(str) # solo con una señal se puede hacer ambas acciones y enviar el dato no es necesario, se actualiza toda la tabla
    save_index = -1
    save_examples_count = 0
    flag_no_change = 0
    def __init__(self,data,practice_main):
        super().__init__()
        ruta_ui = os.path.join(os.path.dirname(__file__), '..','resources', 'ui', 'crud_window.ui')
        uic.loadUi(ruta_ui,self)
        self.data= data
        self.word.setPlaceholderText("word")
        self.boton_practice_w1 = practice_main
        self.subtype_box.setVisible(False)
        self.subtype_label.setVisible(False)
        self.irregular_label.setVisible(False)
        self.simple_label.setVisible(False)
        self.participle_label.setVisible(False)
        self.simple_p.setVisible(False)
        self.participle_p.setVisible(False)
        self.translation.setPlaceholderText("translation")
        self.example_2.setVisible(False)
        self.example_3.setVisible(False)
        self.example_4.setVisible(False)
        self.example_5.setVisible(False)
        self.example_list = [self.example_1,self.example_2,self.example_3,self.example_4,self.example_5]
        self.word.textChanged.connect(self.show_suggestions)  # Conectar la señal textChanged a la función
        self.add_buttton.clicked.connect(self.add_item)
        self.edit_button.clicked.connect(self.modify_item)
        self.clear_button.clicked.connect(self.init_mode)
        self.type_box.currentTextChanged.connect(self.type_box_changed)
        self.subtype_box.currentTextChanged.connect(self.type_verb)
        self.database_list.itemSelectionChanged.connect(self.database_select_changed)# cambia de seleccion
        self.delete_button.clicked.connect(self.delete_item)
        self.more_examples.clicked.connect(self.more_exa)
        self.less_examples.clicked.connect(self.less_exa)
        self.show_database()
        self.database_list.itemDoubleClicked.connect(self.read_data)

    def closeEvent(self, event):
        self.boton_practice_w1.setEnabled(True)

    def show_database(self):
        for item in self.data:
            self.database_list.addItem(item["word"])

    def more_exa(self):
        if ventana2.save_examples_count <=3:
            ventana2.save_examples_count += 1
            self.example_list[ventana2.save_examples_count].setVisible(True)

    def less_exa(self):
        if ventana2.save_examples_count >0:
            self.example_list[ventana2.save_examples_count].setText("")
            self.example_list[ventana2.save_examples_count].setVisible(False)
            ventana2.save_examples_count -= 1

    def type_verb(self, text):
        if text == "irregular":
            self.irregular_label.setVisible(True)
            self.simple_label.setVisible(True)
            self.participle_label.setVisible(True)
            self.simple_p.setVisible(True)
            self.participle_p.setVisible(True)
        else:
            self.hide_more_options()

    def type_box_changed(self,text):
        if text == "verb":
            self.subtype_box.setVisible(True)
            self.subtype_label.setVisible(True)
            if self.subtype_box.currentText() == "irregular":
                self.irregular_label.setVisible(True)
                self.simple_label.setVisible(True)
                self.participle_label.setVisible(True)
                self.simple_p.setVisible(True)
                self.participle_p.setVisible(True)
        else:
            self.subtype_box.setVisible(False)
            self.subtype_label.setVisible(False)
            self.hide_more_options()
    
    def hide_more_options(self):
        self.irregular_label.setVisible(False)
        self.simple_label.setVisible(False)
        self.participle_label.setVisible(False)
        self.simple_p.setVisible(False)
        self.participle_p.setVisible(False)
        self.simple_p.setText("")
        self.participle_p.setText("")

    def show_suggestions(self):
        if ventana2.flag_no_change == 0:
            self.database_list.clear()  # Limpiar la lista para mostrar las nuevas sugerencias
            palabra = self.word.text().lower()
            if palabra:  # Si hay texto en el QLineEdit, buscar sugerencias
                palabras_filtradas = [item["word"] for item in self.data if item["word"].startswith(palabra)]
                palabras_filtradas.sort()
                self.database_list.addItems(palabras_filtradas)  # Mostrar las sugerencias en la QListWidget
            else: 
                #si esta vacio, muestra la lista completa
                for item in self.data:
                    self.database_list.addItem(item["word"])
    
    def database_select_changed(self):
        selected_items = self.database_list.selectedItems()
        if not selected_items:
            print("No hay elementos seleccionados")
            self.delete_button.setDisabled(True)
        else:
            self.delete_button.setDisabled(False)
            self.edit_button.setDisabled(True)          

    def add_item(self):
        nombre = self.word.text().lower()
        significado = self.translation.text()
        words_data = [item["word"] for item in  self.data]
        if significado and nombre and (nombre not in words_data):  
            significado = significado.split(',')
            significado = [item.strip() for item in significado]            
            tipo = self.type_box.currentText()
            ejemplos = []
            for i in range(5):
                if self.example_list[i].text() != "":
                    ejemplos.append(self.example_list[i].text())
            nueva_palabra = {
                "word": nombre,
                "translation": significado,
                "type": tipo
            }
            if tipo == "verb":
                nueva_palabra["subtype"] = self.subtype_box.currentText()
                if self.subtype_box.currentText() == "irregular":
                    nueva_palabra["past_irregular"] = {
                         "simple": self.simple_p.text(),
                         "participle": self.participle_p.text()
                        }
            if ejemplos !=[]:
                nueva_palabra["examples"] = ejemplos
            nueva_palabra["points"] = 0
            self.data.append(nueva_palabra)
            save_data(self.data, shared_data["path"])
            self.signal_update_data.emit() 
            QMessageBox.information(self, 'Info', 'New word added.', QMessageBox.Ok)
            self.init_mode()
        elif not (nombre and significado):
            QMessageBox.warning(self, 'Warning', 'Empty fields.', QMessageBox.Ok)
        else:
            QMessageBox.warning(self, 'Warning', 'The word is already in the database.', QMessageBox.Ok)

    def read_data(self,item):
        selected_item = item
        self.edit_button.setDisabled(False)
        item.setSelected(True)
        print("mi dato es " ,selected_item.text())
        if selected_item is not None:
            index = get_index(self.data,selected_item.text())
            ventana2.save_index = index
            ventana2.flag_no_change = 1
            self.word.setText(self.data[index]["word"])
            ventana2.flag_no_change = 0
            my_translation_string = ", ".join(self.data[index]["translation"])
            self.translation.setText(my_translation_string)
            self.type_box.setCurrentText(self.data[index]["type"])
            if(self.data[index]["type"] == "verb"):
                self.subtype_box.setVisible(True)
                self.subtype_label.setVisible(True)
                self.subtype_box.setCurrentText(self.data[index]["subtype"])
                if(self.data[index]["subtype"] == "irregular"):
                    self.irregular_label.setVisible(True)
                    self.simple_label.setVisible(True)
                    self.participle_label.setVisible(True)
                    self.simple_p.setVisible(True)
                    self.participle_p.setVisible(True)
                    self.simple_p.setText(self.data[index]["past_irregular"]["simple"])
                    self.participle_p.setText(self.data[index]["past_irregular"]["participle"])
            k=0
            #existe la categoria?
            if "examples" in self.data[index]:
                for i in self.data[index]["examples"]:
                    self.example_list[k].setText(i)
                    self.example_list[k].setVisible(True)
                    k+=1
            ventana2.save_examples_count= max(0,k-1)
            for j in range(k,5):
                self.example_list[j].setText("")
                self.example_list[j].setVisible(False)
            self.example_1.setVisible(True)

    def modify_item(self):
        index = ventana2.save_index
        nombre = self.word.text().lower()  
        significado = self.translation.text()      
        words_data = [item["word"] for item in  self.data]
        words_data.remove(self.data[index]["word"])
        if significado and nombre and (nombre not in words_data): 
            self.data[index]["word"] = nombre #el nombre es unico // que pasa si me equivoque en una letra del word?
            significado = significado.split(',')
            significado = [item.strip() for item in significado]    
            self.data[index]["translation"] = significado
            self.data[index]["type"] = self.type_box.currentText()
            #el orden inicial se mantiene, pero el siguiente cambia dependiendo si existen o no
            ejemplos = []
            puntos = self.data[index].pop("points",None)#eliminamos el campo points , lo vamos a poner al final, todos los items tienen este campo
            self.data[index].pop("examples", None)#eliminamos los campos para acomodar los nuevos cambios en orden
            self.data[index].pop("past_irregular", None) 
            self.data[index].pop("subtype", None)
            for i in range(5):
                if self.example_list[i].text() != "":
                    ejemplos.append(self.example_list[i].text())
            if self.type_box.currentText() == "verb":
                self.data[index]["subtype"] = self.subtype_box.currentText()
                if self.subtype_box.currentText() == "irregular":
                    self.data[index]["past_irregular"] = {
                            "simple": self.simple_p.text(),
                            "participle": self.participle_p.text()
                        }
            if ejemplos !=[]:
                self.data[index]["examples"] = ejemplos
            self.data[index]["points"] = puntos
            save_data(self.data, shared_data["path"]) 
            QMessageBox.information(self, 'Info', 'Informacion actualizada.', QMessageBox.Ok)
            self.init_mode()
        elif not (nombre and significado):
            QMessageBox.warning(self, 'Warning', 'Empty fields.', QMessageBox.Ok)
        else:
            QMessageBox.warning(self, 'Warning', 'The word is already in the database.', QMessageBox.Ok)

    def delete_item(self):     
        selected_item = self.database_list.currentItem()        
        if selected_item:
            #eliminar de la lista new_words de la ventana1
            index = get_index(self.data,selected_item.text())
            qm = QMessageBox
            resp = qm.question(self,'', "Are you sure you want to delete this data?", qm.Yes | qm.No)

            if resp == qm.Yes:
                self.data.pop(index)
                save_data(self.data, shared_data["path"]) #antes de emitir la accion primero debo guardar el archivo para que funcione el emit correctamente   
                self.signal_update_data.emit()
                self.init_mode()
                palabra = self.word.text()

                self.database_list.clear()
                for item in self.data:
                    self.database_list.addItem(item["word"])

    def init_mode(self):
        ventana2.save_index = -1
        ventana2.save_examples_count = 0
        self.word.setText("") #cuando se borra este campo, por funcion, se llena la listwidget con toda la data
        self.edit_button.setDisabled(True)
        self.word.setReadOnly(False)
        self.translation.setText("")
        self.translation.setReadOnly(False)
        self.type_box.setCurrentText("noun")
        self.type_box.setEnabled(True)
        self.subtype_box.setCurrentText("regular")
        self.subtype_box.setEnabled(True)
        for i in range(5):
            self.example_list[i].setText("")
            self.example_list[i].setVisible(False)
            self.example_list[i].setReadOnly(False)
        self.example_1.setVisible(True)
        self.more_examples.setDisabled(False)
        self.less_examples.setDisabled(False)
