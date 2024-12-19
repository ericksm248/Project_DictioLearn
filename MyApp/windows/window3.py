
import os
import pyttsx3,random
from PyQt5.QtWidgets import QMainWindow,QMessageBox
from PyQt5 import uic
from globals import shared_data
from utils.helpers import *

class ventana3(QMainWindow):
    practice_mode = "E"
    index_data = 0
    help_count = 0
    flag_menu_conf = 0
    aux_save_subpoint = []
    list_aux_index = []
    flag_many_means = 0
    voice_index = 0
    flag_select_hl = 1
    high_low_flag = "L"
    rate_voice = 0
    flag_select_dictio = 1
    def __init__(self,data,set_database):
        super().__init__()
        ruta_ui = os.path.join(os.path.dirname(__file__), '..','resources', 'ui', 'practice_window.ui')
        uic.loadUi(ruta_ui,self)
        self.data= data

        self.engine_sound = pyttsx3.init()
        voices = self.start_voice_engine()
        if not voices:
            print("#no tiene voces instaladas, escondemos los botones de audio.")
            self.play_speech.setVisible(False)
            self.conf_speech.setVisible(False)
        else: 
            self.engine_sound.setProperty('rate', 110)     # setting up new voice rate
            self.engine_sound.setProperty('voice', voices[ventana3.voice_index].id)
            self.play_speech.clicked.connect(self.sound_voice)
            self.conf_speech.clicked.connect(self.show_hide_menu)

        self.mode.clicked.connect(self.toggle_mode)
        self.boton_setdatabase_w1 = set_database
        self.random_p.clicked.connect(self.get_random_word)
        self.check_answer.clicked.connect(self.check_my_answer)
        self.my_word.textChanged.connect(self.new_word)
        
        self.help_p.setVisible(False)
        self.group_irregular_verbs.setVisible(False)
        self.search_text.textChanged.connect(self.search_method)
        self.check_simple.clicked.connect(self.check_simple_ans)
        self.check_participle.clicked.connect(self.check_participle_ans)
        self.group_conf_speech.setVisible(False)
        self.search_list.itemSelectionChanged.connect(self.change_select_word_list)
        self.help_p.clicked.connect(self.help_information)
        self.select_case.currentTextChanged.connect(self.new_mode_select_word)
        self.group_translationN.setVisible(False)
        self.points_H_L.itemSelectionChanged.connect(self.select_item_point)
        self.N_means.currentTextChanged.connect(self.new_Nmean)
        self.select_voice.currentTextChanged.connect(self.change_select_voice)
        self.rate_sound.valueChanged.connect(self.update_speed)
        self.group_irregular_verbs.move(250,120)
        self.High_points.clicked.connect(self.order_high_points)
        self.Low_points.clicked.connect(self.order_low_points)
        self.reset_points.clicked.connect(self.reset_points_question)

    def start_voice_engine(self):
        try:
            voices = self.engine_sound.getProperty('voices')
            if not voices:
                print("No se encontraron voces instaladas en el sistema.")
            else:
                for voice in voices:
                    #print(f"Voz encontrada: {voice.name}") #solo depuracion
                    self.select_voice.addItem(f"{voice.name}") 
        except Exception as e:
            print(f"Error al inicializar el motor de voz: {e}")
            voices = []
        return voices
    
    def reset_points_question(self):
        #comenzamos desde la primera ventana para no cargar los datos nuevamente
        self.stackwid_main.setCurrentIndex(0)
        self.select_case.setCurrentIndex(0)
        self.my_word.setText("")
        self.search_text.setText("")
        qm = QMessageBox
        resp = qm.question(self,'', "Are you sure you want to reset the points?", qm.Yes | qm.No)
        if resp == qm.Yes:
            for item in self.data:
                item["points"]= 0
            save_data(self.data, shared_data["path"])

    def select_item_point(self):
        if ventana3.flag_select_hl:
            selected_items = self.points_H_L.currentItem()
            if selected_items.text():
                cadena_sin_numeros = ''.join([caracter for caracter in selected_items.text() if not caracter.isdigit()])            
                if ventana3.practice_mode == "E": 
                    if cadena_sin_numeros.endswith("-"):
                        cadena_sin_numeros = cadena_sin_numeros[:-2]
                    else: 
                        cadena_sin_numeros = cadena_sin_numeros[:-1]                  
                    ventana3.index_data = get_index(self.data,cadena_sin_numeros)#cadena_sin_numeros
                else:
                    cadena_sin_numeros = cadena_sin_numeros[:-1] #quitamos el espacio
                    ventana3.index_data = ventana3.list_aux_index[self.points_H_L.currentRow()]
                self.my_word.setText(cadena_sin_numeros) #primero entrego el indice luego seteo la palabra para que ya tenga el indice


    def order_high_points(self):
        ventana3.high_low_flag = "H"
        self.points_H_L.clear()
        if ventana3.practice_mode=="E":
            list_get = [(item["points"],item["word"]) for item in self.data]
            list_get.sort()
            list_get.reverse()
            for item in list_get:
                self.points_H_L.addItem(item[1] + " " + str(item[0]))
        else:
            list_get,list_aux = orden_H_L_index(self.data)
            ventana3.list_aux_index = list_aux
            list_get.reverse()
            ventana3.list_aux_index.reverse()
            for item in list_get:
                self.points_H_L.addItem(item[1] + " " + str(item[0]))


    def order_low_points(self):
        ventana3.high_low_flag = "L"
        self.points_H_L.clear()
        if ventana3.practice_mode=="E":
            list_get = [(item["points"],item["word"]) for item in self.data]
            list_get.sort()
            for item in list_get:
                self.points_H_L.addItem(item[1] + " " + str(item[0]))
        else:
            list_get,list_aux = orden_H_L_index(self.data)
            ventana3.list_aux_index = list_aux
            #print(list_aux)  #depuracion
            for item in list_get:
                self.points_H_L.addItem(item[1] + " " + str(item[0]))

    def search_method(self):
        if ventana3.practice_mode == 'E': #solo en modo ingles español
            self.search_list.clear()  # Limpiar la lista para mostrar las nuevas sugerencias
            palabra = self.search_text.text().lower()
            if palabra:  # Si hay texto en el QLineEdit, buscar sugerencias
                palabras_filtradas = [item["word"] for item in self.data if item["word"].startswith(palabra)]
                palabras_filtradas.sort()
                self.search_list.addItems(palabras_filtradas)  # Mostrar las sugerencias en la QListWidget
            else: 
                #si esta vacio, muestra la lista completa
                for item in self.data:
                    self.search_list.addItem(item["word"])
        else:
            self.search_list.clear() 
            palabra = self.search_text.text().lower()
            if palabra:  
                palabras_filtradas = [item["translation"][0] for item in self.data if item["translation"][0].startswith(palabra)]
                ventana3.list_aux_index = [index1 for index1,item in enumerate(self.data) if item["translation"][0].startswith(palabra)]
                self.search_list.addItems(palabras_filtradas) 
            else: 
                for item in self.data:
                    self.search_list.addItem(item["translation"][0])
                #poner indices
                ventana3.list_aux_index = [index1 for index1,item in enumerate(self.data)]

    def check_simple_ans(self):
        if self.try_simple_word.text() == self.data[ventana3.index_data]["past_irregular"]["simple"]:
            self.bien_simple.setVisible(True)
            self.error_simple.setVisible(False)
        else:
            self.error_simple.setVisible(True)
            self.bien_simple.setVisible(False)

    def check_participle_ans(self):
        if self.try_participle_word.text() == self.data[ventana3.index_data]["past_irregular"]["participle"]:
            self.bien_participle.setVisible(True)
            self.error_participle.setVisible(False)
        else:
            self.error_participle.setVisible(True)
            self.bien_participle.setVisible(False)

    def update_speed(self,valor):
        ventana3.rate_voice = valor -40
        if ventana3.rate_voice >= 0:
            self.speed_voice_label.setText(f"Speed + {ventana3.rate_voice}")
        else:
            self.speed_voice_label.setText(f"Speed - {abs(ventana3.rate_voice)}")

    def change_select_voice(self,text):
            ventana3.voice_index = self.select_voice.currentIndex()

    def sound_voice(self):
        if self.my_word.text():
            self.group_conf_speech.setVisible(False)
            self.conf_speech.setEnabled(False)
            ventana3.flag_menu_conf = 0
            self.group_irregular_verbs.move(250,120)
            self.play_speech.setEnabled(False)
            voices = self.engine_sound.getProperty('voices')
            self.engine_sound.setProperty('rate', 110 + ventana3.rate_voice)   
            self.engine_sound.setProperty('voice', voices[ventana3.voice_index].id)  # Cambia el índice según la voz que prefieras
            self.engine_sound.say(self.my_word.text())
            self.engine_sound.runAndWait()
            self.play_speech.setEnabled(True)
            self.conf_speech.setEnabled(True)

    def one_more_point(self,index):
        self.data[index]["points"] += 1
        save_data(self.data, shared_data["path"])

    def one_less_point(self,index):
        self.data[index]["points"] -= 1
        save_data(self.data, shared_data["path"])

    def new_Nmean(self):
        if ventana3.aux_save_subpoint:
            if ventana3.aux_save_subpoint[self.N_means.currentIndex()]:
                self.check_answer.setEnabled(False)
            else:
                self.help_info.clear()
                self.stackwid_result_check.setCurrentIndex(0)
                self.help_p.setVisible(False)
                self.check_answer.setEnabled(True)
                #seteamos el numero de ayuda
                ventana3.help_count = 0

    def show_hide_menu(self):
        if ventana3.flag_menu_conf:
            ventana3.flag_menu_conf = 0
            self.group_conf_speech.setVisible(False)
            self.group_irregular_verbs.move(250,120)
        else:
            ventana3.flag_menu_conf = 1
            self.group_conf_speech.setVisible(True)
            self.group_irregular_verbs.move(250,210)

    def closeEvent(self, event):
        self.boton_setdatabase_w1.setEnabled(True)

    def change_select_word_list(self):
        if ventana3.flag_select_dictio:
            selected_items = self.search_list.currentItem()
            if selected_items:
                if ventana3.practice_mode == "E":
                    ventana3.index_data = get_index(self.data,selected_items.text()) #primero guarda el indice para que la otra funcion lo pueda tomar
                    #print(ventana3.index_data)  #depuracion                  
                else:
                    ventana3.index_data = ventana3.list_aux_index[self.search_list.currentRow()]
                self.my_word.setText(selected_items.text()) #aqui se ejecuta cambio de texto y la funcion vinculada a este evento  

    def new_mode_select_word(self,text):
        if text == "Random":
            self.stackwid_main.setCurrentIndex(0)
        elif text == "Dictionary":
            self.stackwid_main.setCurrentIndex(1)
            ventana3.flag_select_dictio = 0
            self.search_text.clear()
            self.search_list.clear()
            ventana3.flag_select_dictio = 1
            if ventana3.practice_mode == 'E':
                for item in self.data:
                    self.search_list.addItem(item["word"])
            else:
                for item in self.data:
                    self.search_list.addItem(item["translation"][0])
                ventana3.list_aux_index = [index1 for index1,item in enumerate(self.data)]
        else:
            self.stackwid_main.setCurrentIndex(2)
            ventana3.flag_select_hl = 0
            self.points_H_L.clear()
            ventana3.high_low_flag = "L"
            if ventana3.practice_mode == 'E':
                list_get = [(item["points"],item["word"]) for item in self.data]
                list_get.sort()
                for item in list_get:
                    self.points_H_L.addItem(item[1] + " " + str(item[0]))
            else:
                #funcion que me devuelva la lista ordenada de mayor a menor o viceversa
                list_get,list_aux = orden_H_L_index(self.data)
                ventana3.list_aux_index = list_aux
                for item in list_get:
                    self.points_H_L.addItem(item[1] + " " + str(item[0]))
            ventana3.flag_select_hl = 1

    def help_information(self):
        if ventana3.help_count <3:
            my_data = self.data[ventana3.index_data]["word"] if ventana3.practice_mode == "S" else self.data[ventana3.index_data]["translation"][self.N_means.currentIndex()]
            if ventana3.help_count==0:
                aux_count = len(my_data)
                self.help_info.addItem(f"{aux_count} letters")
            elif ventana3.help_count==1:
                aux_letter = my_data[0]
                self.help_info.addItem(f"first: \"{aux_letter}\"")
            elif ventana3.help_count==2:
                aux_answer = my_data
                self.help_info.addItem(f"answer: {aux_answer}")
                self.check_answer.setEnabled(False)
        ventana3.help_count += 1

    def toggle_mode(self):
        self.stackwid_main.setCurrentIndex(0)
        self.select_case.setCurrentIndex(0)
        self.my_word.setText("")
        self.search_text.setText("")
        if self.mode.text()=="English":
            self.mode.setText("Spanish")
            self.mode_label.setText("to English")
            ventana3.practice_mode = "S"
            self.play_speech.setVisible(False)
            self.conf_speech.setVisible(False)
        else:
            self.mode.setText("English")
            self.mode_label.setText("to Spanish")
            ventana3.practice_mode = "E"
            self.play_speech.setVisible(True)
            self.conf_speech.setVisible(True)

    def get_random_word(self):
        random_num = random.randint(0, len(self.data)-1)
        ventana3.index_data = random_num
        if ventana3.practice_mode == "E":
            self.my_word.setText(self.data[random_num]["word"])
        else:
            self.my_word.setText(self.data[random_num]["translation"][0])#solo en este caso de español a ingles , tomamos la primera traduccion

    def check_my_answer(self):
        my_data = self.data[ventana3.index_data]["word"] if ventana3.practice_mode == "S" else self.data[ventana3.index_data]["translation"][self.N_means.currentIndex()]
        if self.try_word.text() and self.my_word.text():
            if self.try_word.text() == my_data:
                if ventana3.flag_many_means:
                    ventana3.aux_save_subpoint[self.N_means.currentIndex()] = 1
                    flag_aux = True
                    for i in ventana3.aux_save_subpoint:
                        if i==0:
                            flag_aux = False
                    if flag_aux:
                        self.one_more_point(ventana3.index_data)
                    #esta en 1 todas las significados? dar 1 punto
                else:
                    self.one_more_point(ventana3.index_data)
                self.stackwid_result_check.setCurrentIndex(2)
                self.check_answer.setDisabled(True)
                self.help_p.setVisible(False)
            else:
                #intenta nuevamente y pierde un punto
                self.one_less_point(ventana3.index_data)
                self.stackwid_result_check.setCurrentIndex(1)
                self.help_info.addItem("Try again")
                self.help_p.setVisible(True)
                self.help_p.setDisabled(False)
            if self.select_case.currentText() == "Low High Points":
                if ventana3.high_low_flag == "H":
                    self.order_high_points()
                else:
                    self.order_low_points()
        else:
            QMessageBox.warning(self, 'Warning', 'Empty fields', QMessageBox.Ok)

    def new_word(self,text):
        #si en random aparece la misma palabra, no se borra lo anterior
        ventana3.help_count = 0
        ventana3.aux_save_subpoint.clear()
        #print(ventana3.index_data)  #depuracion
        if ventana3.practice_mode == "E":
            if self.data[ventana3.index_data]["type"]=="verb" and self.data[ventana3.index_data]["subtype"]=="irregular":
                self.group_irregular_verbs.setVisible(True)
                self.error_simple.setVisible(False)
                self.bien_simple.setVisible(False)
                self.error_participle.setVisible(False)
                self.bien_participle.setVisible(False)
            else: 
                self.group_irregular_verbs.setVisible(False)
            var_translation_n = len(self.data[ventana3.index_data]["translation"])
            if var_translation_n>1:
                ventana3.flag_many_means = 1
                self.group_translationN.setVisible(True)
                self.N_means.clear()
                for j in range(var_translation_n):                 
                    self.N_means.addItem(f"{j+1}")   
                    ventana3.aux_save_subpoint.append(0) #al inicio cada significado tiene 0 puntos
            else:
                self.group_translationN.setVisible(False)
                ventana3.flag_many_means = 0
        else:
            self.group_irregular_verbs.setVisible(False)
            self.group_translationN.setVisible(False)
            ventana3.flag_many_means = 0
        self.help_info.clear()
        self.N_means.setCurrentIndex(0)
        self.stackwid_result_check.setCurrentIndex(0)
        self.help_p.setVisible(False)
        self.check_answer.setDisabled(False)