import math

class need_energy():
    def __init__(self):
        self.mass = 2000 #kg
        self.mass_factor = 1.05
        self.acceleration = 0 # m^2 / s
        self.coeff_roll_R = 0.02  # coefficient of rolling resistance
        self.air_density = 1.225 # kg/m^3
        self.front_area = 2 # m^2
        self.aero_drag_coff = 0.5
        self.wind_speed = 0 # m/s
        self.road_angle = 0 # angle

    def energy(self, angle, V):  # V is driving speed
        self.road_angle = angle
        rad = math.radians(angle)
        p1 = (self.mass_factor * self.mass * self.acceleration) + (self.mass * 9.8 * self.coeff_roll_R * math.cos(rad))
        p2 = 0.5 * self.air_density * self.front_area * self.aero_drag_coff * ((V - self.wind_speed)**2)
        p3 = self.mass * 9.8 * math.sin(rad)
        P = (p1 + p2 + p3) * V   # Watt
        return P
