#region imports
import math
import numpy as np
import random as rnd
from scipy.optimize import fsolve
from Fluid import Fluid
#endregion
# region class definitions
class Pipe():
    #region constructor
    def __init__(self, Start='A', End='B',L=100, D=200, r=0.00025, fluid=Fluid()):
        '''
        Defines a generic pipe with orientation from lowest letter to highest, alphabetically.
        :param Start: the start node (string)
        :param End: the end node (string)
        :param L: the pipe length in m (float)
        :param D: the pipe diameter in mm (float)
        :param r: the pipe roughness in m  (float)
        :param fluid:  a Fluid object (typically water)
        '''
        #region attributes
        # from arguments given in constructor
        self.startNode=min(Start,End) #makes sure to use the lowest letter for startNode
        self.endNode=max(Start,End) #makes sure to use the highest letter for the endNode
        self.length=L
        self.r=r
        self.fluid=fluid #the fluid in the pipe

        # other calculated properties
        self.d=D/1000.0 #diameter in m
        self.relrough = self.r/self.d #calculate relative roughness for easy use later
        self.A=math.pi/4.0*self.d**2 #calculate pipe cross sectional area for easy use later
        self.Q=10 #working in units of L/s, just an initial guess
        self.vel=self.V()  #calculate the initial velocity of the fluid
        self.reynolds=self.Re() #calculate the initial reynolds number
        #endregion
    #endregion

    #region methods
    def V(self):
        '''
        Calculate average velocity in the pipe for volumetric flow self.Q
        :return:the average velocity in m/s
        '''
        # Q is in L/s => convert to m^3/s
        Q_m3s = self.Q * 1.0e-3
        self.vel= Q_m3s / self.A  # the average velocity is Q/A (be mindful of units)
        return self.vel

    def Re(self):
        '''
        Calculate the reynolds number under current conditions.
        :return:
        '''
        v = self.V()  # ensure velocity is up to date
        self.reynolds= (self.fluid.rho * v * self.d) / self.fluid.mu # Re=rho*V*d/mu, be sure to use V() so velocity is updated.
        return self.reynolds

    def FrictionFactor(self):
        """
        This function calculates the friction factor for a pipe based on the
        notion of laminar, turbulent and transitional flow.
        :return: the (Darcy) friction factor
        """
        # update the Reynolds number and make a local variable Re
        Re=self.Re()
        rr=self.relrough
        # to be used for turbulent flow
        def CB():
            # note:  in numpy log is for natural log.  log10 is log base 10.
            cb = lambda f: 1 / (f ** 0.5) + 2.0 * np.log10(rr / 3.7 + 2.51 / (Re * f ** 0.5))
            result = fsolve(cb, (0.01))
            val = cb(result[0])
            return result[0]
        # to be used for laminar flow
        def lam():
            return 64 / Re

        if Re >= 4000:  # true for turbulent flow
            return CB()
        if Re <= 2000:  # true for laminar flow
            return lam()

        # transition flow is ambiguous, so use normal variate weighted by Re
        CBff = CB()
        Lamff = lam()
        # I assume laminar is more accurate when just above 2000 and CB more accurate when just below Re 4000.
        # I will weight the mean appropriately using a linear interpolation.
        mean = Lamff+((Re-2000)/(4000-2000))*(CBff - Lamff)
        sig = 0.2 * mean
        # Now, use normalvariate to put some randomness in the choice
        return rnd.normalvariate(mean, sig)

    def frictionHeadLoss(self):  # calculate headloss through a section of pipe in m of fluid
        '''
        Use the Darcy-Weisbach equation to find the head loss through a section of pipe.
        '''
        g = 9.81  # m/s^2
        ff = self.FrictionFactor()
        hl = ff * (self.length / self.d) * (self.vel**2 / (2.0 * g)) # calculate the head loss in m of water
        return hl

    def getFlowHeadLoss(self, s):
        '''
        Calculate the head loss for the pipe.
        :param s: the node i'm starting with in a traversal of the pipe
        :return: the signed headloss through the pipe in m of fluid
        '''
        #while traversing a loop, if s = startNode I'm traversing in same direction as positive pipe
        nTraverse= 1 if s==self.startNode else -1
        #if flow is positive sense, scalar =1 else =-1
        nFlow=1 if self.Q >= 0 else -1
        return nTraverse*nFlow*self.frictionHeadLoss()

    def Name(self):
        '''
        Gets the pipe name.
        :return:
        '''
        return self.startNode+'-'+self.endNode

    def oContainsNode(self, node):
        #does the pipe connect to the node?
        return self.startNode==node or self.endNode==node

    def printPipeFlowRate(self):
        print('The flow in segment {} is {:0.2f} L/s'.format(self.Name(),self.Q))

    def getFlowIntoNode(self, n):
        '''
        determines the flow rate into node n
        :param n: a node object
        :return: +/-Q
        '''
        if n==self.startNode:
            return -self.Q
        return self.Q
    #endregion
#endregion