import conversion as c

VMO = 350
MMO = 0.90
VMO_LG = 240
MMO_LG = 240/600

nz_max_volets = {'0': 2.5,
                 '1': 2.3,
                 '2': 1.8,
                 '3': 1.5}
nz_min_volets = {'0': -1.5,
                 '1': -1.2,
                 '2': -1.0,
                 '3': -1.0}
nx_max_volets = {'0': 0.5,
                 '1': 0.5,
                 '2': 0.3,
                 '3': 0.25}

#en entrée : volets et train rentré ou sorti
#en sortie : dictionnaire des performances de l'avion
def perfos_avion(volets: str, landing_gear: int):
    if landing_gear==1:
        nz_max = nz_max_volets[volets]-0.2
        nz_min = nz_min_volets[volets]+0.2
        nx_max = nx_max_volets[volets]
        VNE= VMO_LG
        NEM = MMO_LG
    else:
        nz_max = nz_max_volets[volets]
        nz_min = nz_min_volets[volets]
        nx_max = nx_max_volets[volets]
        VNE = VMO
        NEM = MMO
    perfos = {"NxMax": nx_max,
              "NxMin": -1.0,
              "NzMax": nz_max,
              "NzMin": nz_min,
              "PMax": 0.7,
              "PMin": -0.7,
              "AlphaMax": c.deg_to_rad(15),
              "AlphaMin": c.deg_to_rad(-5),
              "PhiMaxManuel": c.deg_to_rad(66),
              "PhiMaxAutomatique": c.deg_to_rad(30),
              "GammaMax": c.deg_to_rad(10),
              "GammaMin": c.deg_to_rad(-5),
              "MagneticDeclination": 0.22654374,
              "VMO": c.knots_to_ms(VNE),
              "MMO": NEM,
              "V2": c.knots_to_ms(150),
              "MinMach": c.ias_to_tas(150,0)/600
              }     
    return perfos