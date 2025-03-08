#region imports
from scipy.optimize import fsolve
import numpy as np
from Fluid import Fluid
from Node import Node
#endregion
# region class definitions
class PipeNetwork():
    #region constructor
    def __init__(self, Pipes=[], Loops=[], Nodes=[], fluid=Fluid()):
        '''
        The pipe network is built from pipe, node, loop, and fluid objects.
        :param Pipes: a list of pipe objects
        :param Loops: a list of loop objects
        :param Nodes: a list of node objects
        :param fluid: a fluid object
        '''
        #region attributes
        self.loops=Loops
        self.nodes=Nodes
        self.Fluid=fluid
        self.pipes=Pipes
        #endregion
    #endregion

    #region methods
    def findFlowRates(self):
        # Number of equations = # of nodes + # of loops
        N = len(self.nodes) + len(self.loops)

        # initial guess (10 L/s for each unknown, for instance)
        Q0 = np.full(N, 10.0)

        def fn(q):
            # 1) Update each pipe’s flow from the first len(self.pipes) entries of q
            for i in range(len(self.pipes)):
                self.pipes[i].Q = q[i]  # <-- #$JES MISSING CODE$

            # 2) Get the node-flow equations (net flow at each node)
            L = self.getNodeFlowRates()  # <-- #$JES MISSING CODE$

            # 3) Get the loop-head-loss equations (net head loss around each loop)
            L += self.getLoopHeadLosses()  # <-- #$JES MISSING CODE$
            return L

        # Use fsolve to find flows that satisfy node & loop equations
        FR = fsolve(fn, Q0)
        return FR

    def getNodeFlowRates(self):
        #each node object is responsible for calculating its own net flow rate
        qNet=[n.getNetFlowRate() for n in self.nodes]
        return qNet

    def getLoopHeadLosses(self):
        #each loop object is responsible for calculating its own net head loss
        lhl=[l.getLoopHeadLoss() for l in self.loops]
        return lhl

    def getPipe(self, name):
        #returns a pipe object by its name
        for p in self.pipes:
            if name == p.Name():
                return p

    def getNodePipes(self, node):
        #returns a list of pipe objects that are connected to the node object
        l=[]
        for p in self.pipes:
            if p.oContainsNode(node):
                l.append(p)
        return l

    def nodeBuilt(self, node):
        #determines if I have already constructed this node object (by name)
        for n in self.nodes:
            if n.name==node:
                return True
        return False

    def getNode(self, name):
        #returns one of the node objects by name
        for n in self.nodes:
            if n.name==name:
                return n

    def buildNodes(self):
        #automatically create the node objects by looking at the pipe ends
        for p in self.pipes:
            if self.nodeBuilt(p.startNode)==False:
                #instantiate a node object and append it to the list of nodes
                self.nodes.append(Node(p.startNode,self.getNodePipes(p.startNode)))
            if self.nodeBuilt(p.endNode)==False:
                #instantiate a node object and append it to the list of nodes
                self.nodes.append(Node(p.endNode,self.getNodePipes(p.endNode)))

    def printPipeFlowRates(self):
        for p in self.pipes:
            p.printPipeFlowRate()

    def printNetNodeFlows(self):
        for n in self.nodes:
            print('net flow into node {} is {:0.2f}'.format(n.name, n.getNetFlowRate()))

    def printLoopHeadLoss(self):
        for l in self.loops:
            print('head loss for loop {} is {:0.2f}'.format(l.name, l.getLoopHeadLoss()))
    #endregion
# endregion