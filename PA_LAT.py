from ivy.std_api import *
import math
import time

# STATE VECTOR
x = 0
y = 0
z = 0
Vitesse = 1
fpa = 0
PSI = 0  
PHI = 0  

# FCU
mode_actif = "Managed"
selected_value = 0

# PERFO_AVIONS
WindVelocity = 0
WindDirection = 0
MagneticDeclination = 0  
Pmax = 0  
PhiMaxAutomatique = 0

# FGS
LegX = 0
LegY = 0
LegCap = 0

def null_cb(*a):
    pass

def heading():
    global x, y, z, Vitesse, fpa, PSI, PHI, selected_value, PhiMaxAutomatique, Pmax, mode_actif
    TauPhi = 1
    TauPsi = 3 * TauPhi
    gravity = 9.81
    p = 0
    diff_heading = (selected_value - PSI)
    print("heading(): selected_value={}, psi={}".format(selected_value*180/math.pi, PSI*180/math.pi))
    print("DIFFERENCE DE HEADING EN RADIANS{}".format(diff_heading))
    while diff_heading > math.pi:
        diff_heading = diff_heading - 2 * math.pi
    while diff_heading <= -math.pi:
        diff_heading = diff_heading + 2 * math.pi
    phic = diff_heading * (Vitesse / (gravity * TauPsi))
    if phic > PhiMaxAutomatique:
        phic = PhiMaxAutomatique
    if phic < -PhiMaxAutomatique:
        phic = -PhiMaxAutomatique
    p = (phic - PHI) / TauPhi
    if p >= Pmax:
        p = Pmax
    if p <= (-Pmax):
        p = -Pmax
    p_string = str(p)
    #print("heading(): selected_value={}, PSI={}, phic={}, PHI={}".format(selected_value*180/math.pi, PSI*180/math.pi, phic*180/math.pi, PHI*180/math.pi))
    print(p_string)
    IvySendMsg("AP_LAT p=" + p_string)

def track():
    global selected_value, Vitesse, PSI, fpa, x, y, WindVelocity, WindDirection
    psiC = 0
    derive = 0
    a = Vitesse * math.cos(fpa) * math.cos(PSI) + WindVelocity * math.cos(WindDirection)
    b = Vitesse * math.cos(fpa) * math.sin(PSI) + WindVelocity * math.sin(WindDirection)
    khi = math.atan2(b, a)
    argsin = WindVelocity * math.sin(khi - WindDirection) / (Vitesse * math.cos(fpa))
    if argsin > 1:
        argsin = 1
    elif argsin < -1 :
        argsin = -1
    derive = math.asin(argsin)
    psiC = selected_value - derive
    selected_value = psiC
    if (PSI -psiC <= 1):
        selected_value = PSI
    else :
        selected_value = psiC
    print("track(): psiC={}".format(psiC*180/math.pi))
    heading()

def axis():
    tauXtk = 8
    khiC = 0
    global selected_value #Vitesse, PSI, fpa, x, y, WindVelocity, WindDirection, LegX, LegY, LegCap
    print("route actuelle x =", LegX, "route actuelle y =", LegY)
    print("LegCap:", LegCap , "en deg")
    xpoint = (Vitesse * math.cos(fpa) * math.cos(PSI)) + (WindVelocity * math.cos(WindDirection))
    ypoint = (Vitesse * math.cos(fpa) * math.sin(PSI)) + (WindVelocity * math.sin(WindDirection))
    GS = math.sqrt((math.pow(ypoint, 2)) + (math.pow(xpoint, 2)))
    xTk = -(x - LegX) * math.sin(LegCap) + (y - LegY) * math.cos(LegCap)
    print("XTK =", xTk)
    VerificationSin = xTk / (GS * tauXtk)
    if VerificationSin <= -math.sin(45):
        VerificationSin = -math.sin(45)
    if VerificationSin >= math.sin(45):
        VerificationSin = math.sin(45)
    khiC = -math.asin(VerificationSin) + LegCap #Depassement a mettre 
    selected_value = khiC

    print("route sélectionnée", selected_value * (180 / math.pi), "en deg")
    track()

def on_selectedHeading(agent, *selectedHeading):
    global selected_value, mode_actif
    selected_value = float(selectedHeading[0]) * (math.pi / 180) - MagneticDeclination
    mode_actif = "selectedHeading"
    print("SelectedHeading reçu avant appel heading()")
    heading()
    print("SelectedHeading reçu")

def on_selectedTrack(agent, *selectedTrack):
    global mode_actif, selected_value
    mode_actif = "selectedTrack"
    selected_value = float(selectedTrack[0]) * (math.pi / 180) - MagneticDeclination
    #track()
    print("SelectedTrack reçu")

def on_managed(agent, *arg):
    global mode_actif
    mode_actif = "Managed"
    #axis()

def on_state_vector(agent, *state_vector):
    global x, y, z, Vitesse, fpa, PSI, PHI
    x = float(state_vector[0])
    y = float(state_vector[1])
    z = float(state_vector[2])
    Vitesse = float(state_vector[3])
    fpa = float(state_vector[4])
    PSI = float(state_vector[5])
    PHI = float(state_vector[6])
    print("reçu state vector")

def on_mise_a_jour_Wind(agent, *majWind):
    global WindVelocity, WindDirection
    WindVelocity = float(majWind[0])
    WindDirection = float(majWind[1])

def on_mise_a_jour_Declinaison(agent, *majDeclination):
    global MagneticDeclination
    MagneticDeclination = float(majDeclination[0])

def on_PhiMaxAutomatique(agent, *PhiMaxInfo):
    global PhiMaxAutomatique, Pmax
    PhiMaxAutomatique = float(PhiMaxInfo[9])
    Pmax = float(PhiMaxInfo[4])

def on_FGS(agent, *FGSinfo):
    global LegX, LegY, LegCap
    LegX = float(FGSinfo[0])
    LegY = float(FGSinfo[1])
    LegCap = float(FGSinfo[2])

    if mode_actif == "Managed":
        axis()
    elif mode_actif == "selectedTrack":
        print("TRACKKKKKKKKKKKKK")
        track()
    elif mode_actif == "selectedHeading":
        print("HEADINGGGGGGGGGGGGGGGGGGGGGGGG")
        heading()
    else:
        print("on_FGS ERROR mode_actif={} inconnu !".format(mode_actif))

app_name = "PA_LATERAL"
IvyInit(app_name, "[%s ready]" % app_name, 0, null_cb, null_cb)
#IvyStart("192.168.60.255:2087")
bus_ivy = "192.168.161.255:2087"
bus_ivy = "127.255.255.255:2010"
IvyStart(bus_ivy)
IvyBindMsg(on_selectedHeading,'^FCULateral Mode=SelectedHeading Val=(\S+)')
IvyBindMsg(on_selectedTrack, '^FCULateral Mode=SelectedTrack Val=(\S+)')
IvyBindMsg(on_managed, '^FCULateral Mode=Managed Val=(\S+)')

IvyBindMsg(on_state_vector, '^StateVector x=(\S+) y=(\S+) z=(\S+) Vp=(\S+) fpa=(\S+) psi=(\S+) phi=(\S+)')
IvyBindMsg(on_mise_a_jour_Wind, '^WindComponent WindVelocity=(\S+) WindDirection=(\S+)')
IvyBindMsg(on_mise_a_jour_Declinaison, 'MagneticDeclination=(\S+)')
IvyBindMsg(on_PhiMaxAutomatique, 'Performances NxMax=(\S+) NxMin=(\S+) NzMax=(\S+) NzMin=(\S+) PMax=(\S+) PMin=(\S+) AlphaMax=(\S+) AlphaMin=(\S+) PhiMaxManuel=(\S+) PhiMaxAutomatique=(\S+) GammaMax=(\S+) GammaMin=(\S+) Vmo=(\S+) Vmin=(\S+) Mmo=(\S+) Mmin=(\S+)')
IvyBindMsg(on_FGS, '^AxeFlightPlan LegX=(\S+) LegY=(\S+) LegCap=(\S+)')

IvyMainLoop()