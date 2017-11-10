import numpy as np

class lithium_ion_battery():
    # working voltage 3.8
    # cut-off voltage 2
    # we have 100 cells
    def __init__(self, capacity):
        self.cell_voltage = 4
        self.cutoff_voltage = 2
        self.grade = (self.cell_voltage - self.cutoff_voltage) / 100
        self.total_capacity = capacity
        self.capacity = capacity #Wh
        self.Ah = self.capacity / (self.cell_voltage * 100)
        self.need_charge = False
        self.energy_consume = 0
        self.SOC = 0.9
        #self.output = 1  # unit is C, c rate

    def use(self, duration, power):
        # duration in second
        # power in Watt  (j/s)
        #self.need_charge = False
        self.SOC = self.capacity / self.total_capacity
        if self.SOC > 0.9:
            self.SOC = 0.9
        if self.SOC <= 0.2:
            self.need_charge = True
        self.cell_voltage = self.SOC * 100 * self.grade + self.cutoff_voltage    # we assume it is linear
        #self.capacity -= duration * outputrate * self.Ah * self.cell_voltage * 100 / 3600
        if not self.need_charge:
            self.energy_consume = duration * power / (3600)
            self.capacity -= duration * power / (3600)

        return self.need_charge

    def charge(self, wh):
        if (wh + self.capacity) > self.total_capacity:
            self.capacity = self.total_capacity
            self.need_charge = False
        else:
            self.capacity = wh + self.capacity
            self.need_charge = False
