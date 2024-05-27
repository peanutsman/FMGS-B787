
from PyQt5.QtWidgets import QWidget
from PyQt5 import uic, QtCore
from ivy.std_api import *
    
recorded_data = None
def null_cb(*a):
    pass


class Train(QWidget):
    def __init__(self, signal_emitter, parent=None):
        super().__init__(parent)
        
        self.signal_emitter = signal_emitter
        
        uic.loadUi("interfacetrain.ui", self) #chargement de l'interface
        self.train.valueChanged.connect(self.update_train_from_inside) #connexion du signal valueChanged à la fonction update_train
        
        self.signal_emitter.signal_update_train.connect(self.update_train_from_outside) #connexion du signal signal_update_train à la fonction update_train_from_outside
        
    @QtCore.pyqtSlot()    
    def update_train_from_inside(self):
        #self.train.setValue(posi) #mise à jour de la position du train
        IvySendMsg("LandingGearState=%s" % self.train.value()) #envoi du message Ivy
        self.signal_emitter.signal_update_train.emit(self.train.value()) #emit signal
        
        
    @QtCore.pyqtSlot(int)
    def update_train_from_outside(self, posi):
        self.train.setValue(posi) #mise à jour de la position du train
        
    #def update_train(self,posi):
         #mise à jour de la position du train
        #self.update_train_from_inside() #emission du signal et envoi du message Ivy
            

    
