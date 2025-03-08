# region imports
from Fluid import Fluid
from Pipe import Pipe
from Loop import Loop
from PipeNetwork import PipeNetwork
# endregion

# region function definitions
def main():
    # instantiate a Fluid object to define the working fluid as water
    water = Fluid(mu=0.00089, rho=1000)  # <-- Fill in for #$JES MISSING CODE$
    roughness = 0.00025  # in meters

    # instantiate a new PipeNetwork object
    PN = PipeNetwork(fluid=water)  # <-- Fill in for #$JES MISSING CODE$

    # add Pipe objects to the pipe network
    PN.pipes.append(Pipe('a','b',250, 300, roughness, water))
    PN.pipes.append(Pipe('a','c',100, 200, roughness, water))
    PN.pipes.append(Pipe('b','e',100, 200, roughness, water))
    PN.pipes.append(Pipe('c','d',125, 200, roughness, water))
    PN.pipes.append(Pipe('c','f',100, 150, roughness, water))
    PN.pipes.append(Pipe('d','e',125, 200, roughness, water))
    PN.pipes.append(Pipe('d','g',100, 150, roughness, water))
    PN.pipes.append(Pipe('e','h',100, 150, roughness, water))
    PN.pipes.append(Pipe('f','g',125, 250, roughness, water))
    PN.pipes.append(Pipe('g','h',125, 250, roughness, water))

    # build nodes automatically
    PN.buildNodes()

    # update the external flow (L/s) of certain nodes
    PN.getNode('a').extFlow = 60   # inflow of 60 L/s
    PN.getNode('d').extFlow = -30  # outflow of 30 L/s
    PN.getNode('f').extFlow = -15
    PN.getNode('h').extFlow = -15

    # add loops
    PN.loops.append(
        Loop('A', [PN.getPipe('a-b'), PN.getPipe('b-e'), PN.getPipe('d-e'),
                   PN.getPipe('c-d'), PN.getPipe('a-c')])
    )
    PN.loops.append(
        Loop('B', [PN.getPipe('c-d'), PN.getPipe('d-g'), PN.getPipe('f-g'),
                   PN.getPipe('c-f')])
    )
    PN.loops.append(
        Loop('C', [PN.getPipe('d-e'), PN.getPipe('e-h'), PN.getPipe('g-h'),
                   PN.getPipe('d-g')])
    )

    # solve for flow rates
    PN.findFlowRates()

    # print results
    PN.printPipeFlowRates()
    print()
    print('Check node flows:')
    PN.printNetNodeFlows()
    print()
    print('Check loop head loss:')
    PN.printLoopHeadLoss()

if __name__ == "__main__":
    main()

# endregions

