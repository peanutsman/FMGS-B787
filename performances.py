import math

nz_max_volets = {0: 2.5,
                 1: 2.3,
                 2: 1.8,
                 3: 1.5}
nz_min_volets = {0: -1.5,
                 1: -1.2,
                 2: -1.0,
                 3: -1.0}
nx_max_volets = {0: 0.5,
                 1: 0.5,
                 2: 0.3,
                 3: 0.25}

def deg_to_rad(deg: float):
    return deg * math.pi / 180

def perfos_avion(statevector : list, volets, landing_gear):
    if landing_gear==1:
        nz_max = nz_max_volets[volets]-0.2
        nz_min = nz_min_volets[volets]+0.2
        nx_max = nx_max_volets[volets]
    else:
        nz_max = nz_max_volets[volets]
        nz_min = nz_min_volets[volets]
        nx_max = nx_max_volets[volets]
    perfos = {"NxMax": nx_max,
              "NxMin": -1.0,
              "NzMax": nz_max,
              "NzMin": nz_min,
              "PMax": 0.7,
              "AlphaMax": deg_to_rad(15),
              "AlphaMin": deg_to_rad(-5),
              "PhiMaxManuel": deg_to_rad(66),
              "PhiMaxAutomatique": deg_to_rad(30),
              "GammaMax": deg_to_rad(10),
              "GammaMin": deg_to_rad(-5),
              "MagneticDeclination": 0.22654374,
              "VMO": 350,
              "MMO": 0.90,
              "V2": 150,
              "MinMach": 150/600
              }     
    return perfos