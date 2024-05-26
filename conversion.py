from math import pi

def meters_to_feet(meters: float):
    return meters * 3.28084

def feet_to_meters(feet: float):
    return feet / 3.28084

def knots_to_ms(knots: float):
    return knots * 0.514444

def deg_to_rad(deg: float):
    return deg * pi / 180

def rad_to_deg(rad: float):
    return rad * 180 / pi

def speed_to_mach(speed: float):
    return speed / 600

def mach_to_speed(mach: float):
    return mach * 600
