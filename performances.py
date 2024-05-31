import conversion as c
from math import acos
VMO = 350
MMO = 0.90
VMO_LG = 240
MMO_LG = 240/600
LGDOWN, LGUP = 0, 1
FLAPS0, FLAPS5, FLAPS20, FLAPS30 = '0', '1', '2', '3'

nz_max_volets = {FLAPS0: 2.5,
                 FLAPS5: 2.3,
                 FLAPS20: 1.8,
                 FLAPS30: 1.5}
nz_min_volets = {FLAPS0: -1.5,
                 FLAPS5: -1.2,
                 FLAPS20: -1.0,
                 FLAPS30: -1.0}
nx_max_volets = {FLAPS0: 0.5,
                 FLAPS5: 0.5,
                 FLAPS20: 0.3,
                 FLAPS30: 0.25}

nx_min_volets = {FLAPS0: -0.8,
                 FLAPS5: -0.7,
                 FLAPS20: -0.6,
                 FLAPS30: -0.5}

#en entrée : volets et train rentré ou sorti
#en sortie : dictionnaire des performances de l'avion
def perfos_avion(volets: str, landing_gear: int, alt=float):
    if int(alt) in range(0, 12000):
        red = 0.5*alt/10000 #plus l'altitude est grand, plus on réduit le nzmax
    else:
        red = 0.5
    if landing_gear==LGDOWN:
        nz_max = nz_max_volets[volets]-0.2-red
        nz_min = nz_min_volets[volets]+0.2+red
        nx_max = nx_max_volets[volets]-0.1-(red/4)
        nx_min = nx_min_volets[volets]+0.1+red
        VNE= VMO_LG
        NEM = MMO_LG
        if acos(1/nz_max) > c.deg_to_rad(30):
            phimax = c.deg_to_rad(30)
        else:
            phimax = acos(1/nz_max)
    else:
        nz_max = nz_max_volets[volets]-red
        nz_min = nz_min_volets[volets]
        nx_max = nx_max_volets[volets]
        nx_min = nx_min_volets[volets]
        VNE = VMO
        NEM = MMO
        if acos(1/nz_max) > c.deg_to_rad(30):
            phimax = c.deg_to_rad(30)
        else:
            phimax = acos(1/nz_max)
    perfos = {"NxMax": nx_max,
              "NxMin": nx_min,
              "NzMax": nz_max,
              "NzMin": nz_min,
              "PMax": 0.7,
              "PMin": -0.7,
              "AlphaMax": c.deg_to_rad(15),
              "AlphaMin": c.deg_to_rad(-5),
              "PhiMaxManuel": c.deg_to_rad(66),
              "PhiMaxAutomatique": phimax,
              "GammaMax": c.deg_to_rad(10),
              "GammaMin": c.deg_to_rad(-5),
              "MagneticDeclination": 0.22654374,
              "VMO": c.knots_to_ms(VNE),
              "MMO": NEM,
              "V2": c.knots_to_ms(150),
              "MinMach": c.ias_to_tas(150,0)/600
              }     
    return perfos