from math import pi

def meters_to_feet(meters: float):
    return meters * 3.28084

def feet_to_meters(feet: float):
    return feet / 3.28084

def knots_to_ms(knots: float):
    return knots * 0.514444

def ms_to_knots(ms: float):
    return ms / 0.514444

def ias_to_tas(ias: float, altitude: float):
    return ias - altitude/(2*100)

def tas_to_ias(tas: float, altitude: float):
    return tas + altitude/(2*100)

def deg_to_rad(deg: float):
    return deg * pi / 180

def rad_to_deg(rad: float):
    return rad * 180 / pi

def tas_to_mach(speed: float):
    return speed / 600

def mach_to_tas(mach: float):
    return mach * 600

def nm_to_m(nm: float):
    return nm * 1852
