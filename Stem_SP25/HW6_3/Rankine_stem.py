from Steam_stem import steam

class rankine():
    def __init__(self, p_low=8, p_high=8000, t_high=None, name='Rankine Cycle'):
        '''
        If t_high is None, assume saturated vapor (x=1) at p_high for state1.
        Otherwise, use t_high for superheated steam at p_high.
        '''
        self.p_low = p_low
        self.p_high = p_high
        self.t_high = t_high
        self.name   = name

        self.efficiency   = None
        self.turbine_work = 0.0
        self.pump_work    = 0.0
        self.heat_added   = 0.0
        self.state1       = None
        self.state2       = None
        self.state3       = None
        self.state4       = None

    def calc_efficiency(self):
        # STATE 1: Turbine Inlet
        if self.t_high is None:
            # saturated vapor at p_high => x=1
            self.state1 = steam(self.p_high, x=1.0, name='Turbine Inlet')  # <-- #JES MISSING CODE
        else:
            # superheated steam at p_high => T = t_high
            self.state1 = steam(self.p_high, T=self.t_high, name='Turbine Inlet')  # <-- #JES MISSING CODE

        # STATE 2: Turbine Exit => p_low, s = s1 (isentropic)
        self.state2 = steam(self.p_low, s=self.state1.s, name='Turbine Exit')  # <-- #JES MISSING CODE

        # STATE 3: Pump Inlet => saturated liquid at p_low => x=0
        self.state3 = steam(self.p_low, x=0.0, name='Pump Inlet')  # <-- #JES MISSING CODE

        # STATE 4: Pump Exit => p_high, same s as state3 is not truly correct for real liquids,
        # but let's do a simpler approach:
        self.state4 = steam(self.p_high, s=self.state3.s, name='Pump Exit')
        # Then approximate the enthalpy rise in the pump:
        self.state4.h = self.state3.h + self.state3.v * (self.p_high - self.p_low)
        # (Units: kJ/kg + [m^3/kg * kPa] => must confirm consistent units. Usually 1 kPa=1 kJ/(m^3).)

        # Now compute the cycle energies
        self.turbine_work = self.state1.h - self.state2.h   # (kJ/kg)
        self.pump_work    = self.state4.h - self.state3.h   # (kJ/kg)
        self.heat_added   = self.state1.h - self.state4.h   # (kJ/kg)

        self.efficiency = 100.0 * (self.turbine_work - self.pump_work) / self.heat_added
        return self.efficiency

    def print_summary(self):
        if self.efficiency is None:
            self.calc_efficiency()

        print('Cycle Summary for: ', self.name)
        print('\tEfficiency: {:0.3f}%'.format(self.efficiency))
        print('\tTurbine Work: {:0.3f} kJ/kg'.format(self.turbine_work))
        print('\tPump Work: {:0.3f} kJ/kg'.format(self.pump_work))
        print('\tHeat Added: {:0.3f} kJ/kg'.format(self.heat_added))
        self.state1.print()
        self.state2.print()
        self.state3.print()
        self.state4.print()

def main():
    # Example test:
    # If t_high is specified, that means superheated steam at turbine inlet
    # If t_high is not specified, that means x=1 at turbine inlet
    rankine1 = rankine(p_low=8, p_high=8000, t_high=300, name='Rankine Test (superheated)')  # <-- #JES MISSING CODE
    eff = rankine1.calc_efficiency()
    print('Efficiency = {:0.2f}%'.format(eff))
    rankine1.print_summary()

if __name__=="__main__":
    main()
