# floorplanner
The following project will use simulated Annealing to place the blocks when their different possible dimensions are given and outputs the coordinates at which they can be placed.
the command to be used to run is the folllowing
python floorplanner.py -input "<input_file_path>\n100.blocks" -output n100.out

The parameters for simulated annealing are found out during runtime based on the maximum area which it can take at any point of time. This gives the simuated engine to try most possibe polish expressions which are possible.

The sizing and adding coordinates functions are both based on stack based implementation but they are coded using recursions for the sae of simplicity(uses the computer stack to get to conclusions)

The 3 figures generated are for only n100.blocks
1.  Cost Function vs Iteration
2.  Temperature vs Iteration : Gives a rough estimate on how the temperature is changing
3.  Percentage of Accepted Moves vs Temperature: Explains the number of moves that are being accepted. In the figure the right most point is the initial tempearature at which all possible moves are accepted as temperature decreases the number of moves which are being accepted decreases and tends to 0

The code for the matlab plots is removed to improve the speed of the code

Sizing is done based on the algorithm discussed in the class which helps in finding the best possible dimensions and ignoring the ones which lead to worst configurations and also thus sorting them already.

The project doesnot handle the case when a block has configurations with different areas. To handle this we need to remove the configuration which donot make sense where we eliminate the dimension where both the width and length are greater than any other configurations.
