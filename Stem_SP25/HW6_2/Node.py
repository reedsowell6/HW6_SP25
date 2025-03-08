#region class definitions
class Node():
    #region constructor
    def __init__(self, Name='a', Pipes=[], ExtFlow=0):
        '''
        A node in a pipe network.
        :param Name: name of the node
        :param Pipes: a list/array of pipes connected to this node
        :param ExtFlow: any external flow into (+) or out (-) of this node in L/s
        '''
        #region attributes
        self.name=Name
        self.pipes=Pipes
        self.extFlow=ExtFlow
        #endregion
    #endregion

    #region methods
    def getNetFlowRate(self):
        '''
        Calculates the net flow rate into this node in L/s
        # :return: the net flow rate into this node
        '''
        Qtot = self.extFlow #count the external flow first
        for p in self.pipes:
            #retrieves the pipe flow rate (+) if into node (-) if out of node.  see class for pipe.
            Qtot+=p.getFlowIntoNode(self.name)
        return Qtot
    #endregion
#endregion