# region imports
import numpy as np
from scipy.interpolate import griddata
# endregion

# region class definitions
class steam():
    """
    The steam class is used to find thermodynamic properties of steam along an isobar.
    """
    def __init__(self, pressure, T=None, x=None, v=None, h=None, s=None, name=None):
        '''
        :param pressure: pressure in kPa
        :param T: Temperature in °C
        :param x: quality (0–1)
        :param v: specific volume in m^3/kg
        :param h: enthalpy in kJ/kg
        :param s: entropy in kJ/(kg·K)
        :param name: an identifier
        '''
        self.p = pressure  # kPa
        self.T = T         # °C
        self.x = x         # quality
        self.v = v         # m^3/kg
        self.h = h         # kJ/kg
        self.s = s         # kJ/(kg·K)
        self.name = name
        self.region = None  # 'Superheated' or 'Saturated' or ?

        if (T is None and x is None and v is None and h is None and s is None):
            # no second property => cannot calculate
            return
        else:
            self.calc()

    def calc(self):
        '''
        Determine if we’re in saturated or superheated region,
        then find the unknown properties by interpolation.
        '''
        # 1) Load the saturated steam table (in bar) from file
        #    The columns are: T[°C], p[bar], hf, hg, sf, sg, vf, vg
        sat_data = np.loadtxt('sat_water_table.txt', skiprows=1)
        ts  = sat_data[:, 0]  # °C
        ps  = sat_data[:, 1]  # bar
        hfs = sat_data[:, 2]  # kJ/kg
        hgs = sat_data[:, 3]
        sfs = sat_data[:, 4]
        sgs = sat_data[:, 5]
        vfs = sat_data[:, 6]
        vgs = sat_data[:, 7]

        # 2) Load the superheated steam table (p in kPa)
        #    The columns are: Tcol[°C], hcol[kJ/kg], scol[kJ/(kg·K)], pcol[kPa]
        sh_data = np.loadtxt('superheated_water_table.txt', skiprows=1)
        tcol = sh_data[:, 0]  # °C
        hcol = sh_data[:, 1]  # kJ/kg
        scol = sh_data[:, 2]  # kJ/(kg·K)
        pcol = sh_data[:, 3]  # kPa

        # Convert self.p (kPa) -> bar for use with the saturated table
        Pbar = self.p / 100.0

        # Interpolate saturated properties at this pressure
        # We do 1D griddata because ps is 1D, ts is 1D, etc.
        Tsat = float(griddata((ps,), ts,  (Pbar,), method='linear'))
        hf   = float(griddata((ps,), hfs, (Pbar,), method='linear'))
        hg   = float(griddata((ps,), hgs, (Pbar,), method='linear'))
        sf   = float(griddata((ps,), sfs, (Pbar,), method='linear'))
        sg   = float(griddata((ps,), sgs, (Pbar,), method='linear'))
        vf   = float(griddata((ps,), vfs, (Pbar,), method='linear'))
        vg   = float(griddata((ps,), vgs, (Pbar,), method='linear'))

        # Keep these around if needed
        self.hf = hf
        # (Similarly, you could store self.hg, etc.)

        # Ideal gas constant for water vapor (approx)
        R = 8.314 / (18 / 1000.0)  # J/(mol·K) ÷ [kg/mol] => J/(kg·K)
                                   # ~ 461.5 J/(kg·K)

        #region figure out which second property is given
        if self.T is not None:
            # we have T and p
            if self.T > Tsat:
                # superheated region
                self.region = 'Superheated'
                # Interpolate h, s from superheated table using T & p
                # T in °C, p in kPa => we pass (self.T, self.p)
                self.h = float(griddata(
                    (tcol, pcol), hcol, (self.T, self.p), method='linear'))
                self.s = float(griddata(
                    (tcol, pcol), scol, (self.T, self.p), method='linear'))
                self.x = 1.0
                # Estimate v with ideal gas (rough approximation)
                TK = self.T + 273.15
                # p in kPa => multiply by 1000 for Pa
                self.v = R * TK / (self.p * 1000.0)
            else:
                # saturated (two-phase or just saturated vapor if x=1)
                self.region = 'Saturated'
                self.T = Tsat
                # We do not know x => but if user explicitly gave T < Tsat, that’s incomplete
                # Typically we assume x=1 if T=Tsat for turbine inlet, or user sets x
                # If you need to handle subcooled, that’s more complicated.
                # For now assume x=1 for "saturated vapor"
                if self.x is None:
                    self.x = 1.0
                self.h = hf + self.x*(hg - hf)
                self.s = sf + self.x*(sg - sf)
                self.v = vf + self.x*(vg - vf)

        elif self.x is not None:
            # saturated mixture => direct interpolation
            self.region = 'Saturated'
            self.T = Tsat
            self.h = hf + self.x*(hg - hf)
            self.s = sf + self.x*(sg - sf)
            self.v = vf + self.x*(vg - vf)

        elif self.h is not None:
            # we have h and p
            x_test = (self.h - hf) / (hg - hf)
            if x_test <= 1.0:
                # still saturated region
                self.region = 'Saturated'
                self.x = x_test
                self.T = Tsat
                self.s = sf + self.x*(sg - sf)
                self.v = vf + self.x*(vg - vf)
            else:
                # superheated
                self.region = 'Superheated'
                self.x = 1.0
                # We do 2D interpolation with (h, p) => T, s
                self.T = float(griddata(
                    (hcol, pcol), tcol, (self.h, self.p), method='linear'))
                self.s = float(griddata(
                    (hcol, pcol), scol, (self.h, self.p), method='linear'))
                # approximate v
                TK = (self.T if self.T is not None else Tsat) + 273.15
                self.v = R * TK / (self.p * 1000.0)

        elif self.s is not None:
            # we have s and p
            x_test = (self.s - sf) / (sg - sf)
            if x_test <= 1.0:
                # saturated region
                self.region = 'Saturated'
                self.x = x_test
                self.T = Tsat
                self.h = hf + self.x*(hg - hf)
                self.v = vf + self.x*(vg - vf)
            else:
                # superheated region
                self.region = 'Superheated'
                self.x = 1.0
                # 2D interpolation with (s, p) => T, h
                self.T = float(griddata(
                    (scol, pcol), tcol, (self.s, self.p), method='linear'))
                self.h = float(griddata(
                    (scol, pcol), hcol, (self.s, self.p), method='linear'))
                # approximate v
                TK = (self.T if self.T is not None else Tsat) + 273.15
                self.v = R * TK / (self.p * 1000.0)
        #endregion

    def print(self):
        """
        Nicely formatted steam property report.
        """
        print('Name: ', self.name)
        if self.x is not None and self.x < 0.0:
            print('Region: compressed liquid')
        else:
            print('Region: ', self.region)
        print('p = {:0.2f} kPa'.format(self.p))
        if self.x is not None and self.x >= 0.0:
            print('T = {:0.1f} °C'.format(self.T))
        print('h = {:0.2f} kJ/kg'.format(self.h))
        if self.x is not None and self.x >= 0.0:
            print('s = {:0.4f} kJ/(kg·K)'.format(self.s))
            if self.region == 'Saturated':
                print('v = {:0.6f} m^3/kg'.format(self.v))
                print('x = {:0.4f}'.format(self.x))
        print()
# endregion

# region function definitions
def main():
    # Example usage
    inlet = steam(7350, name='Turbine Inlet')  # not enough info
    inlet.x = 0.9
    inlet.calc()
    inlet.print()

    h1 = inlet.h
    s1 = inlet.s
    print(h1, s1,'\n')

    outlet = steam(100, s=inlet.s, name='Turbine Exit')
    outlet.print()

    another = steam(8575, h=2050, name='State 3')
    another.print()
    yetanother = steam(8575, h=3125, name='State 4')
    yetanother.print()
# endregion

# region function calls
if __name__=="__main__":
    main()
# endregion
