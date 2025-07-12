This application is a pentomino solver that has two modes of operations. Given a grid and size, and a set of exclusions 
so that the available number of squares is divisible by 5. The pentominos will be placed on the grid during the solver. 
This is a client server application demonstrating splits between a frontend UI making a pretty display of the solver. And 
the engine that performs the resolution of the puzzle. 

The datesolver is a play on the pentomino solver in which a fixed size grid is used, and Day, Day of Week and Month formulate 
exclusions to show the current date. 

Running the applicaiton:

python pentomino_rest.py

Note this application is created as a sample for client/server computing and provides a solution, and is not optimized to be
the fastest solution or provide all solutions. 

The server side, runs multiple threads walking the possibility of solutions. Using logic of good placement, and no non contiguous
cells that are less than 5 so that a pentomino can fit in the remaining cell. 

Solutions speeds can be reduced, by suggesting locations of pieces using the UI and placing the pentominos on the grid. 
Use the space bar to rotate/flip the pentomino orientation. Green and red boarders of the pentomino squares should indicate 
valid drop locations over the grid. 

This was written in conjunction with AI Tools where prompting was given to create various features of the applicaiton. 
Author/Promptor: Klwilson2272
No warrantee is implied, and the software functions as is. 
