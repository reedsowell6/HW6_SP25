#region imports
from ResistorNetwork import ResistorNetwork, ResistorNetwork_2
#endregion

# region Function Definitions
def main():
    """
    This program solves for the unknown currents in the circuit of the homework assignment.
    :return: nothing
    """
    print("Network 1:")
    # JES MISSING CODE: Instantiate a ResistorNetwork object
    Net = ResistorNetwork()
    # JES MISSING CODE: Call the function that builds the resistor network from a text file
    Net.BuildNetworkFromFile("ResistorNetwork.txt")
    # Now analyze the circuit
    IVals = Net.AnalyzeCircuit()

    print("\nNetwork 2:")
    # JES MISSING CODE: Instantiate a ResistorNetwork_2 object
    Net_2 = ResistorNetwork_2()
    # JES MISSING CODE: Call the function that builds the resistor network from a text file
    Net_2.BuildNetworkFromFile("ResistorNetwork_2.txt")
    # Now analyze the second circuit
    IVals_2 = Net_2.AnalyzeCircuit()
# endregion

# region function calls
if __name__=="__main__":
    main()
# endregion
