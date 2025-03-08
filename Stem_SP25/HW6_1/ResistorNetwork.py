#region imports
from scipy.optimize import fsolve
from Resistor import Resistor
from VoltageSource import VoltageSource
from Loop import Loop
#endregion

#region class definitions
class ResistorNetwork():
    #region constructor
    def __init__(self):
        """
        The resistor network consists of Loops, Resistors and Voltage Sources.
        """
        #region attributes
        self.Loops = []      # initialize an empty list of loop objects in the network
        self.Resistors = []  # initialize an empty list of resistor objects in the network
        self.VSources = []   # initialize an empty list of source objects in the network
        #endregion
    #endregion

    #region methods
    def BuildNetworkFromFile(self, filename):
        """
        Reads lines from a file and processes them to populate self.Loops, self.Resistors, self.VSources.
        """
        FileTxt   = open(filename,"r").read().split('\n')
        FileLength = len(FileTxt)
        LineNum    = 0
        self.Resistors = []
        self.VSources  = []
        self.Loops     = []
        while LineNum < FileLength:
            lineTxt = FileTxt[LineNum].lower().strip()
            if len(lineTxt) <1:
                pass
            elif lineTxt[0] == '#':
                pass  # skip comment lines
            elif "resistor" in lineTxt:
                LineNum = self.MakeResistor(LineNum, FileTxt)
            elif "source" in lineTxt:
                LineNum = self.MakeVSource(LineNum, FileTxt)
            elif "loop" in lineTxt:
                LineNum = self.MakeLoop(LineNum, FileTxt)
            LineNum += 1

    def MakeResistor(self, N, Txt):
        """
        Make a resistor object from reading the text file
        """
        # JES Missing Code:
        R = Resistor()      # instantiate a new resistor
        N += 1              # move past the line that said <Resistor>
        txt = Txt[N].lower()
        while "resistor" not in txt:
            if "name" in txt:
                R.Name = txt.split('=')[1].strip()
            if "resistance" in txt:
                R.Resistance = float(txt.split('=')[1].strip())
            N += 1
            txt = Txt[N].lower()

        self.Resistors.append(R)
        return N

    def MakeVSource (self, N, Txt):
        """
        Make a voltage source object from reading the text file
        """
        VS = VoltageSource()
        N += 1
        txt = Txt[N].lower()
        while "source" not in txt:
            if "name" in txt:
                VS.Name = txt.split('=')[1].strip()
            if "value" in txt:
                VS.Voltage = float(txt.split('=')[1].strip())
            if "type" in txt:
                VS.Type = txt.split('=')[1].strip()
            N += 1
            txt = Txt[N].lower()

        self.VSources.append(VS)
        return N

    def MakeLoop(self, N, Txt):
        """
        Make a Loop object from reading the text file
        """
        L = Loop()
        N += 1
        txt = Txt[N].lower()
        while "loop" not in txt:
            if "name" in txt:
                L.Name = txt.split('=')[1].strip()
            if "nodes" in txt:
                # e.g. "nodes=a,b,c,d"
                txt = txt.replace(" ","")
                L.Nodes = txt.split('=')[1].strip().split(',')
            N += 1
            txt = Txt[N].lower()

        self.Loops.append(L)
        return N

    def AnalyzeCircuit(self):
        """
        Use fsolve to find currents in the original resistor network (3 unknowns: I1, I2, I3).
        """
        # JES Missing Code: define an initial guess for i = [I1, I2, I3]
        i0 = [0.1, 0.1, 0.1]   # just a simple guess
        i  = fsolve(self.GetKirchoffVals, i0)

        # Print the results
        print("I1 = {:0.2f} A".format(i[0]))
        print("I2 = {:0.2f} A".format(i[1]))
        print("I3 = {:0.2f} A".format(i[2]))
        return i

    def GetKirchoffVals(self, i):
        """
        Returns the system of KCL/KVL equations for the first (left) circuit
        so that fsolve can drive them to zero.
        """
        # Set currents in the relevant resistors
        self.GetResistorByName('ad').Current = i[0]  # I1
        self.GetResistorByName('bc').Current = i[0]  # I1
        self.GetResistorByName('cd').Current = i[2]  # I3
        self.GetResistorByName('ce').Current = i[1]  # I2

        # KCL at node c: net current in = 0
        #   Inflow:  I1, I2
        #   Outflow: I3
        Node_c_Current = i[0] + i[1] - i[2]

        # Get the loop voltage drops (KVL) from each Loop object
        #   If you have 2 loops, this returns something like [eqn_loop1, eqn_loop2].
        KVL = self.GetLoopVoltageDrops()

        # We append the node-c KCL equation to that list of loop equations
        KVL.append(Node_c_Current)

        return KVL

    def GetElementDeltaV(self, name):
        """
        Retrieves the voltage drop for a resistor or voltage source by name.
        If we find a resistor with matching name, we return -R.DeltaV() so that
        the direction of traversal is consistent with the code in GetLoopVoltageDrops.
        If we find a voltage source, we return either +V or -V depending on direction.
        """
        # Resistors
        for r in self.Resistors:
            if name == r.Name:
                return -r.DeltaV()
            # Also check reversed name (e.g. "ab" vs "ba")
            if name[::-1] == r.Name:
                return -r.DeltaV()

        # Voltage sources
        for v in self.VSources:
            if name == v.Name:
                return v.Voltage
            if name[::-1] == v.Name:
                return -v.Voltage

    def GetLoopVoltageDrops(self):
        """
        For each Loop in self.Loops, traverse the node list in order and sum
        voltage drops across each element. Then return a list of those net drops.
        """
        loopVoltages = []
        for L in self.Loops:
            loopDeltaV = 0.0
            for n in range(len(L.Nodes)):
                if n == len(L.Nodes)-1:
                    # last node connects back to the first
                    name = L.Nodes[0] + L.Nodes[n]
                else:
                    # connect node n to node n+1
                    name = L.Nodes[n] + L.Nodes[n+1]
                loopDeltaV += self.GetElementDeltaV(name)
            loopVoltages.append(loopDeltaV)
        return loopVoltages

    def GetResistorByName(self, name):
        """
        Returns a resistor object from self.Resistors based on matching name
        """
        for r in self.Resistors:
            if r.Name == name:
                return r
        return None  # if not found
    #endregion

# --------------------------------------------------------------------

class ResistorNetwork_2(ResistorNetwork):
    """
    Child class that inherits from ResistorNetwork but overrides
    AnalyzeCircuit and GetKirchoffVals to handle the second (right) circuit
    that has an extra 5 Ohm resistor in parallel with the 32V source.
    """
    #region constructor
    def __init__(self):
        super().__init__()  # runs the constructor of the parent class
        # any additional attributes for the second circuit can go here
    #endregion

    #region methods
    def AnalyzeCircuit(self):
        """
        Use fsolve for the second circuit, which presumably has 5 unknowns
        (I1, I2, I3, I4, I5) if you have added a resistor in parallel with
        the 32V source and possibly have more nodes/loops.
        """
        # Example initial guess for 5 unknown currents:
        i0 = [0.1, 0.1, 0.1, 0.1, 0.1]
        i  = fsolve(self.GetKirchoffVals, i0)

        print("I1 = {:0.2f} A".format(i[0]))
        print("I2 = {:0.2f} A".format(i[1]))
        print("I3 = {:0.2f} A".format(i[2]))
        print("I4 = {:0.2f} A".format(i[3]))
        print("I5 = {:0.2f} A".format(i[4]))
        return i

    def GetKirchoffVals(self, i):
        """
        Return the system of KCL/KVL equations for the second circuit.
        This example assumes you have 5 unknowns and that your text file
        (ResistorNetwork_2.txt) defines new elements (including the 5 Ohm resistor,
        named e.g. 'de') and additional loops.
        """
        # Example of setting currents in your known resistor names:
        #   If you kept the same resistor names 'ad', 'bc', 'cd', 'ce'
        #   plus a new resistor 'de' for the 5 ohm in parallel with 32V source:
        self.GetResistorByName('ad').Current = i[0]  # I1
        self.GetResistorByName('bc').Current = i[0]  # I1
        self.GetResistorByName('cd').Current = i[2]  # I3
        self.GetResistorByName('ce').Current = i[1]  # I2
        # The new 5 ohm resistor from d to e:
        self.GetResistorByName('de').Current = i[4]  # I5

        # Now define your node-current equations (KCL) and gather loop eqns (KVL).
        # Example: KCL at node c
        Node_c_Current = i[0] + i[1] - i[2]

        # Maybe KCL at node e:
        # (Depends on directions of I2, I4, I5 in your actual circuit diagram.)
        # If current i[1] flows from c->e, and i[4] flows from e->f, etc., adapt signs:
        Node_e_Current = i[1] - i[4]  # for instance

        # Then collect your loop KVL equations from self.GetLoopVoltageDrops().
        # Suppose you defined 2 loops in the second circuit’s text file. Then:
        KVL = self.GetLoopVoltageDrops()  # returns something like [loopEqn1, loopEqn2]

        # You need 5 equations total for 5 unknowns, so add 3 KCL eqns:
        #   (One for node c, one for node e, maybe one for node d or f.)
        # For illustration, here’s a dummy node d eqn:
        Node_d_Current = 0.0  # Replace with the actual sum of currents at d

        # Add them to the KVL list so that fsolve sees 5 equations:
        KVL.append(Node_c_Current)
        KVL.append(Node_e_Current)
        KVL.append(Node_d_Current)

        return KVL
    #endregion
#endregion
