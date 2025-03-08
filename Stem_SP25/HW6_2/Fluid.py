#region class definitions
class Fluid():
    #region constructor
    def __init__(self, mu=0.00089, rho=1000):
        '''
        default properties are for water
        :param mu: dynamic viscosity in Pa*s -> (kg*m/s^2)*(s/m^2) -> kg/(m*s)
        :param rho: density in kg/m^3
        '''
        #region attributes
        self.mu = mu # simply make a copy of the value in the argument as a class property
        self.rho= rho # simply make a copy of the value in the argument as a class property
        self.nu = self.mu/self.rho # calculate the kinematic viscosity in units of m^2/s
        #endregion
    #endregion
#endregion