import sys

from PyQt5.QtWidgets import QWidget
from PyQt5 import uic, QtCore
from ivy.std_api import *
    
recorded_data = None
def null_cb(*a):
    pass


        
class Volet(QWidget):
    def __init__(self, signal_emitter, parent=None):
        super().__init__(parent)
        
        self.signal_emitter = signal_emitter
        
        uic.loadUi("interfacevolet.ui", self) #chargement de l'interface
        self.volet.valueChanged.connect(self.update_posi_from_inside) #connexion du signal valueChanged à la fonction update_posi
        
        self.signal_emitter.signal_update_posi.connect(self.update_posi_from_outside) #connexion du signal signal_update_posi à la fonction update_posi_from_outside

    @QtCore.pyqtSlot()  
    def update_posi_from_inside(self):
        #self.volet.setValue(pos) #mise à jour de la position du volet
        self.signal_emitter.signal_update_posi.emit(self.volet.value()) #emit signal
        IvySendMsg("VoletState=%s" % self.volet.value()) #envoi du message Ivy
        
            
    @QtCore.pyqtSlot(int)   
    def update_posi_from_outside(self, pos):
        self.volet.setValue(pos) #mise à jour de la position du volet

        
    #def update_posi(self,pos):
        #self.update_posi_from_inside() #emission du signal et envoi du message Ivy
    
    