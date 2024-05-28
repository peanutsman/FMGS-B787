
import volet as v
import train as t
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSlider
from PyQt5 import QtCore
from PyQt5.QtCore import Qt

class MainView(QWidget):
    
    #signal customisés
    signal_update_posi = QtCore.pyqtSignal(int)
    signal_update_train = QtCore.pyqtSignal(int)
    
    
    def __init__(self):
        super().__init__()
        self.volet = v.Volet(self) #création de l'objet volet
        self.volet.setParent(self)
        self.train = t.Train(self) #création de l'objet train
        self.train.setParent(self)
        self.signal_update_posi.connect(self.volet.update_posi_from_outside) #connexion des signaux
        self.signal_update_train.connect(self.train.update_train_from_outside) #connexion des signaux
        self.init_ui()

        self.signal_update_posi.emit(0) #initialisation de la position du volet
        self.signal_update_train.emit(0) #initialisation de la position du train
        
    
    def init_ui(self):
        hbox = QHBoxLayout() #layout horizontal
        hbox.addWidget(self.volet) #ajout de l'objet volet
        qwid_backg = QWidget()
        qwid_backg.setStyleSheet("background-image: url(:/img/train1.png);")
        qwid_backg.lower()
        hbox.addWidget(qwid_backg)
        self.setLayout(hbox)
        
        
        self.train.show() #ajout de l'objet train
        self.train.move(185,18)
        self.train.raise_()
        self.train.setStyleSheet("background-color: rgb(203, 203, 203);")
        
        
        self.setFixedSize(442, 370) #définition de la taille de la fenêtre
        
        
