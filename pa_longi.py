from ivy.std_api import *
import time
import numpy as np
import math

# Conversion constants
rad2deg = 180 / np.pi
deg2rad = 1 / rad2deg
ms2kts = 1.9438452
kts2ms = 1 / ms2kts
ft2m = 0.3048
m2ft = 1 / ft2m
ft_min2m_s = ft2m / 60
ft2FL = 1 / 100
g = 9.81

# Global variables
z = 0
VicSelected = 1
Vp = 1
fpa = 0
phi = 0

fpa_max = 0.1
fpa_min = -fpa_max

hcFCU = 0
hcManaged = 0

altitude_diff = hcFCU - z


FCUVitesseManage = 1
FCUModeVitesse = "Speed"
VpConsigne = 0

FCUSelectedAltitude = 0
FCU_ModeVS = 1
FCU_ModeFPA = 2
FCUManagedAltitude = 3
modeFCUVertical = FCUManagedAltitude

tauv = 1  # sec
taugamma = 1  # sec
tauh = 3  # sec

# PID parameters
Kp = 0.5
Ki = 0.1
Kd = 0.05

# Initialize PID terms
integral = 0
previous_error = 0
previous_time = time.time()


def onFCU(agent, *larg):
    print("FCU push button activated or desactivated")

# State vector update
def State_vector(agent, *larg):
    global z, Vp, fpa, phi
    z = float(larg[2])
    Vp = float(larg[3])
    fpa = float(larg[4])
    phi = float(larg[6])

# FCU Speed Mach update
def onFCUSpeedMsg(agent, *larg):
    global FCUVitesseManage, FCUModeVitesse, VpConsigne

    if larg[0] == "Managed":
        FCUVitesseManage = 1
    elif larg[0] == "SelectedMach":
        FCUVitesseManage = 0
        FCUModeVitesse = "Mach"
        mach_value = float(larg[1])
        if mach_value == 0:
            mach_value = 0.0001  # Une très petite valeur pour éviter la division par zéro
        VpConsigne = mach_value * 600 * kts2ms
    else:
        FCUVitesseManage = 0
        FCUModeVitesse = "Speed"
        speed_value = float(larg[1])
        if speed_value == 0:
            speed_value = 0.0001  # Une très petite valeur pour éviter la division par zéro
        VpConsigne = (speed_value + z * m2ft * ft2FL / 2) * kts2ms

    print("FCUVitesseManage={}, FCUModeVitesse={}, Vp consigne={}".format(FCUVitesseManage, FCUModeVitesse, VpConsigne))


# calcul nx par défaut, léger depassement de 5kt
def calcul_nx():
    global VpConsigne
    
    if VpConsigne == 0:
        VpConsigne = 0.0001  # Une très petite valeur pour éviter la division par zéro
    
    nx = ((VpConsigne - Vp) / tauv) * (1 / g) + math.sin(fpa)
    
    print("calcul_nx: VpConsigne={}, Vp={}, Nx={}".format(VpConsigne, Vp, nx))

    return nx

def nx_corrige(nx):
    return min(max(nx, nxmin), nxmax)

def calcul_nz():
    global gamma_c

    altitude_tolerance = 10  # tolérance en mètres
    Vp_safe = Vp if Vp != 0 else 0.0001  # Utiliser une très petite valeur pour éviter la division par zéro

    # Mode Altitude Sélectionnée
    if modeFCUVertical == FCUSelectedAltitude:
        sinGamma = (hcFCU - z) / (Vp_safe * tauh)
        sinGamma = max(min(sinGamma, 1), -1)  # Limiter sinGamma à la plage [-1, 1]
        gamma_c = math.asin(sinGamma)

        print("calcul_nz: FCUSelectedAltitude hc={} z={} gamma_c={}".format(hcFCU * m2ft, z * m2ft, gamma_c * 180 / math.pi))

    # Mode Altitude Gérée
    elif modeFCUVertical == FCUManagedAltitude:
        sinGamma = (hcManaged - z) / (Vp_safe * tauh)
        sinGamma = max(min(sinGamma, 1), -1)  # Limiter sinGamma à la plage [-1, 1]
        gamma_c = math.asin(sinGamma)

        print("calcul_nz: FCUManagedAltitude hc={}".format(hcManaged * m2ft))


    # Mode FPA
    elif modeFCUVertical == FCU_ModeFPA:
        altitude_diff = hcFCU - z

        if abs(altitude_diff) <= altitude_tolerance:
            gamma_c = 0  # Arrêter la montée ou la descente
            print("calcul_nz: FCU_ModeFPA Altitude cible atteinte, gamma_c arrêté à 0")
        elif (altitude_diff > 0 and fpa_rad > 0) or (altitude_diff < 0 and fpa_rad < 0):
            sinGamma = altitude_diff / (Vp_safe * tauh)
            sinGamma = max(min(sinGamma, 1), -1)  # Limiter sinGamma à la plage [-1, 1]
            gamma_c = math.asin(sinGamma)

            print("calcul_nz: FCU_ModeFPA altitude_diff={} gamma_c={}".format(altitude_diff, gamma_c * 180 / math.pi))
        else:
            gamma_c = 0

            message = "/!\FPA incorrect pour altitude cible : Commande Ignorée"
            IvySendMsg(f'{message}')

            print("calcul_nz: FCU_ModeFPA fpa_rad inconsistente avec l'altitude cible, arrêt de gamma_c")


    # Mode VS
    elif modeFCUVertical == FCU_ModeVS:
        altitude_diff = hcFCU - z

        if abs(altitude_diff) <= altitude_tolerance:
            gamma_c = 0  # Arrêter la montée ou la descente
            print("calcul_nz: FCU_ModeVS Altitude cible atteinte, gamma_c arrêté à 0")
        elif (altitude_diff > 0 and Vsc > 0) or (altitude_diff < 0 and Vsc < 0):
            sinGamma = Vsc / Vp_safe
            sinGamma = max(min(sinGamma, 1), -1)  # Limiter sinGamma à la plage [-1, 1]
            gamma_c = math.asin(sinGamma)
            print("calcul_nz: FCU_ModeVS Vsc={} Vp={} gamma_c={}".format(Vsc, Vp, gamma_c * 180 / math.pi))
        else:
            gamma_c = 0
            message = "/!\ VSc incorrect pour altitude cible : Commande Ignorée"
            IvySendMsg(f'{message}')
            print("calcul_nz: FCU_ModeVS Vsc inconsistente avec l'altitude cible, arrêt de gamma_c")

   
    
    # Mode par défaut
    else:
        gamma_c = fpa
        print("calcul_nz: Default mode gamma_c={}".format(gamma_c * 180 / math.pi))

    # Limiter gamma_c entre fpa_max et fpa_min
    gamma_c = max(min(gamma_c, fpa_max), fpa_min)
    
    # Calcul de nz
    
    nz = (((gamma_c - fpa) / taugamma) * Vp_safe / g + math.cos(fpa)) / math.cos(phi)

    print("calcul_nz: Vp={} fpa={} Nz={}".format(Vp_safe, fpa, nz))

    return nz


def nz_corrige(nz):
    return min(max(nz, nzmin), nzmax)

# FGS Zc update
def onFGSZc(agent, *larg):
    global hcManaged

    hcManaged = float(larg[0])
    
    print("onFGSZc: {}".format(hcManaged))
    
    #IvySendMsg("APNzControl nz={}".format(calcul_nz()))

    nx = nx_corrige(calcul_nx())
    nz = nz_corrige(calcul_nz())
    
    #émission des paramètres Nx, Nz sur le bus IVY (qui sont récupérées par le Minimanche qui sert de boite aux lettres)
    IvySendMsg("PaLong Nx={} Nz={}".format(nx, nz))

# FGS Vc update
def onFGSVc(agent, *larg):
    global VpConsigne

    if FCUVitesseManage == 1:
        if larg[0] == "Mach":
            VpConsigne = float(larg[1]) * 600 * kts2ms
            print('Debug: On est en Mach: ', VpConsigne)
            # IvySendMsg(f'Mode Managed - Mach converti en m/s: {hc}') #dev

        else:
            VpConsigne = float(larg[2]) + z * m2ft * ft2FL / 2  # Ils nous envoient une Vi en m/s
            print('Debug: On est en Vp: ', VpConsigne)
            #IvySendMsg(f'Mode Managed - VP(kt): {VpConsigne}') #dev 

    nx = nx_corrige(calcul_nx())
    nz = nz_corrige(calcul_nz())

    #émission des paramètres Nx, Nz sur le bus IVY (qui sont récupérées par le Minimanche qui sert de boite aux lettres)
    IvySendMsg("PaLong Nx={} Nz={}".format(nx, nz)) 



# PA Managed Altitude
def PAManagedAlti(agent, *larg):
    global modeFCUVertical, hcFCU
    modeFCUVertical = FCUManagedAltitude
    hcFCU = ft2m * float(larg[0])
    print("Debug: Altitude managed (m): ", hcFCU)
    IvySendMsg(f'FCU: Mode AltiManaged activé - Zm (m)): {hcFCU}')


# PA Selected Altitude
def PASelectedAlti(agent, *larg):
    global modeFCUVertical, hcFCU
    modeFCUVertical = FCUSelectedAltitude
    hcFCU = ft2m * float(larg[0])
    print("Debug: Altitude selected (m): ", hcFCU)
    IvySendMsg(f'FCU : Mode AltiSelect activé - Zc (m): {hcFCU}')

# PA Selected FPA 
def PA_FPA(agent, *larg):
    global modeFCUVertical, fpa_rad, hcFCU
    modeFCUVertical = FCU_ModeFPA
    fpa_rad = deg2rad * float(larg[1])  # capturer l'angle 
    hcFCU = ft2m * float(larg[0])
    print("Debug: Mode FPA -  fpa_rad (rad): ", fpa_rad)
    IvySendMsg(f'FCU: Mode FPA activé -  FPA (rad): {fpa_rad}')

    

# PA Selected VS 
def PA_VS(agent, *larg):
    global modeFCUVertical, Vsc, hcFCU
    modeFCUVertical = FCU_ModeVS
    Vsc = ft_min2m_s * float(larg[1])  # capturer la vitesse verticale
    hcFCU = ft2m * float(larg[0])
    print("Debug: Mode VS - Vsc (m/s): ", Vsc)
    IvySendMsg(f'FCU: Mode VS activé - Vsc (m/s): {Vsc}')

# Performances update
def performances(agent, NxMax, NxMin, NzMax, NzMin, PMax, PMin, AlphaMax, AlphaMin, PhiMaxManuel, PhiMaxAutomatique, GammaMax, GammaMin, Vmo, Vmin, Mmo, Mmin):
    global nxmax, nxmin, nzmax, nzmin, pmax, pmin, alphamax, alphamin, phimaxmanuel, phimaxautomatique, gammamax, gammamin, vmo, vmin, mmo, mmin
    
    nxmax = float(NxMax)
    nxmin = float(NxMin)
    nzmax = float(NzMax)
    nzmin = float(NzMin)
    pmax = float(PMax)
    pmin = float(PMin)
    alphamax = float(AlphaMax)
    alphamin = float(AlphaMin)
    phimaxmanuel = float(PhiMaxManuel)
    phimaxautomatique = float(PhiMaxAutomatique)
    gammamax = float(GammaMax)
    gammamin = float(GammaMin)
    vmo = float(Vmo)
    vmin = float(Vmin)
    mmo = float(Mmo)
    mmin = float(Mmin)
    #print("Debug:: les perfos ont été màj

    
def send_parameters(agent, *larg):
    nx = nx_corrige(calcul_nx())
    nz = nz_corrige(calcul_nz())
    IvySendMsg("PaLong Nx={} Nz={}".format(nx, nz))
    print("Nx={}, Nz={}".format(nx, nz))
    IvySendMsg('APNxControl nx=',nx)
    IvySendMsg('APNzControl nz=',nz)


# Ivy initialization
app_name = "PALONG"
ivy_bus = "192.168.161.255:2087" #iplocal
#ivy_bus = "192.168.131.255:2087" #ipdev
#ivy_bus = "254.255.255.255:2010"
ivy_bus = "127.255.255.255:2010"
def null_cb(*a):
    pass

#Innitialisation de l'app PA LONGI
IvyInit("PALongi", "Ready", 0, null_cb, null_cb)
IvyStart(ivy_bus)

#abonnements bus IVY

#En Provenance du FGS:
IvyBindMsg(onFGSVc, '^Statut=(\S+) MachManaged=(\S+) VcManaged=(\S+)') #MachManaged ou VcManaged du FGS 
IvyBindMsg(onFGSZc, '^ZcManaged=(\S+)') #AltiManaged du FGS

#Performances en provenance du FGS et récupérer des valeurs limites:
IvyBindMsg(performances, '^Performances NxMax=(\S+) NxMin=(\S+) NzMax=(\S+) NzMin=(\S+) PMax=(\S+) PMin=(\S+) AlphaMax=(\S+) AlphaMin=(\S+) PhiMaxManuel=(\S+) PhiMaxAutomatique=(\S+) GammaMax=(\S+) GammaMin=(\S+) Vmo=(\S+) Vmin=(\S+) Mmo=(\S+) Mmin=(\S+)')
    
#En Provenance du FCU:
IvyBindMsg(onFCU,'^FCUAP1 push') # activation-desactivation du FCU

#Mode speed:
IvyBindMsg(State_vector, '^StateVector x=(\S+) y=(\S+) z=(\S+) Vp=(\S+) fpa=(\S+) psi=(\S+) phi=(\S+)') #vecteur d'état
IvyBindMsg(onFCUSpeedMsg, '^FCUSpeedMach Mode=(\S+) Val=(\S+)') #mode Mach ou Speed sélectionné sur le FCU et la valeurs associées

#Mode verticaux:
IvyBindMsg(PA_VS, '^FCUVertical Altitude=(\S+) Mode=VS Val=(\S+)') #Mode Vertical Speed & recup valeurs sassociées
IvyBindMsg(PA_FPA, '^FCUVertical Altitude=(\S+) Mode=FPA Val=(\S+)') #Mode Vertical Speed & recup valeurs associées
IvyBindMsg(PASelectedAlti,'^FCUVertical Altitude=(\S+) Mode=Selected')#mode AltitudesSelected & recup valeur cible
IvyBindMsg(PAManagedAlti,'^FCUVertical Altitude=(\S+) Mode=Managed')#mode AltiotudeManaged & recup valeur cible

#Pause de 1seconde
time.sleep(1)

#Boucle Ivy pour détecter les changements d'état sur le bus 
IvyMainLoop()

#Exemples pour le dev de messages en provenance du FGS et/ou FCU: 
#Performances NxMax=0.5 NxMin=-1.0 NzMax=2.29995 NzMin=-1.3 PMax=0.7 PMin=-0.7 AlphaMax=0.2617993877991494 AlphaMin=-0.08726646259971647 PhiMaxManuel=1.1519173063162575 PhiMaxAutomatique=1.120988970364693 GammaMax=0.17453292519943295 GammaMin=-0.08726646259971647 Vmo=123.46656 Vmin=77.1666 Mmo=0.4 Mmin=0.25
#StateVector x=200 y=100 z=3000 Vp=120 fpa=1 psi=0.1 phi=0.1 #3000m en