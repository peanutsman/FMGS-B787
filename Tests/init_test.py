import matplotlib.pyplot as plt
from math import sqrt

SUCCESS = 1

class Test_init:
    def __init__(self, name):
        self.name = name
        self.x = []
        self.y = []
    
    def create_test_file(self, success):
        self.file_name = "txt " +  self.name
        self.test_file = open(self.file_name, 'w')
        if len(self.x) != len(self.y):
            raise ValueError("Les résultats et le temps ne sont pas en phase.")
        if success == 0:
            self.test_file.write("***Erreur de success***")
        else:
            for item_x, item_y in zip(self.x, self.y):
                self.test_file.write(f"A {item_x}, le résultat obtenu est : {item_y}\n")
        self.test_file.close()

    def show_graph_test_xy(self, x_label, y_label):
        plt.plot(self.y, self.x)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.show()


"""
test = Test_init("1")
test.create_test_file()
fichier = open(test.file_name, "r")
fichier.read()
fichier.close()
"""

class Test(Test_init):
    def __init__(self, name, duration):
        super().__init__(name)
        self.duration = duration
    
    def timer(self, f, t_x):
        if len(t_x) == self.duration:
            f()
        


class StateVector:
    def __init__(self, x, y, z, Vp, fpa, psi, phi):
        self.x = x
        self.y = y
        self.z = z
        self.Vp = Vp
        self.fpa = fpa
        self.psi = psi
        self.phi = phi

    def __str__(self) -> str:
        return f"StateVector\r\nx={self.x}, y={self.y}, z={self.z}\r\nVp={self.Vp}, fpa={self.fpa}\r\npsi={self.psi}, phi={self.phi}"

    def __format__(self) -> str:
        return self.__str__()
    
class Point2D:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    
    def distance_horizontale(self, other):
        return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
class WayPoint(Point2D):
    def __init__(self, x, y, z, name, bool_fly):
        super().__init__(x, y)
        self.z = z
        self.name = name
        bool_fly = bool_fly

def get_flightplan(path):
    fp = []
    with open(path, "r") as f:
        for line in f:
            t = line.rstrip().split(',')
            fp.append(WayPoint(t[0], t[1], t[2], t[3], t[4]))
    return fp