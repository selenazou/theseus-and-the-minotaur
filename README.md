# Theseus and the Minotaur Solver

Welcome to the Theseus and the Minotaur Logic Puzzle Solver! This solver was designed and implemented for the *CISC 204: Logic for Computing* course at Queen's University. It aims to create a logical model for a given 6x6 board configuration of the *Theseus and the Minotaur* game, then determine whether this configuration is solvable. A description of the game by the creator can be found [here](http://www.logicmazes.com/theseus4.html).

## Structure

You really only need one file to check out the solver -- the others are for administrative or marking purposes.
* `run.py`: Python script containing the entire code to solve a given instance of a puzzle. This includes 3 pre-programmed scenarios; to try these out, comment out the 'game()' call in line 1047 and uncomment the relevant parts of the script (lines 24 and 1044 for scenario 1; lines 27 and 1045 for scenario 2; and lines 30 and 1046 for scenario 3). To test it out with computer-randomized board configurations, just use the script as is :)

Note that at this time, the maximum number of moves is limited to 15 to prevent the recursion from causing a stack overflow (even for some complex scenarios under 15 moves, the solver may still take a long time or occasionally crash).
