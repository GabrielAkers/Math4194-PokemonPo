# Math4194-PokemonPo


Basically there's a 10x10 grid of walkable streets, no diagonal movement, over a 4x4 mile city center. Pokes spawn on average
every 30 minutes and dissapear after exactly 15. Not all spawn locations are equal with some being clearly favored over others.
The pokes are worth points ranging from 1-20 with the higher values being much more rare than the the lower valued ones. 
The objective is to gain as many points as possible in 12 hours.

This project is a simulation for Pokemon Po intended to be used as a way to verify and present the mathematical model of the game
described and built by myself, Carly and Craig for MATH4194 in Spring 2020.

The code is bad because it was written by me over a period of two days without much planning. 
The project was assigned at night Thursday Jan 9, 2020 and the report was due the morning of Monday Jan 13, 2020.

# INSTRUCTIONS:


1) Download the project
2) Install requirements found in requirements.txt
3) Run pokemon_po.py
4) Read outputted data in the json file that is generated each run

The advantage to generating data this way is that you can see the state of the game at every time step by analyzing the data in the run json. So a replay function could be built using the data.


# EXPLANATION OF VARIABLES:


CONTROL = HUMAN : to play yourself with arrow keys

CONTROL = AGENT : to have the agent play


TIME_SCALE = x : scales timing by x, x in (0,1) makes the sim run slower, x > 1 makes it faster and x=1 runs at default speed
this controls ALL timing in the simulation

SESSION_TIME = x : default is 720 seconds which corresponds to 12 hours as per the problem statement. the game will exit after this time, but you can change that behavior in Game.run() just change lines 546 and 547 so the game doesnt exit after seeing the session time up event. it will now just log data every x seconds (scaled by TIME_SCALE of course) instead of closing


poke_points() : controls the point values of individual pokemon

poke_times() : controls the time between pokemon spawns

poke_spawn_weights(x,y) : assigns weights to each node in the grid. I recommend just building your own weight matrix in the shape of mine and assigning it to weight_file instead of modifying this function


Player.vision_function = func : func just needs to return a list of visible nodes. I've provided two already that can be used - player_vision_radius() and player_vision_adjacent(). You should set this when you instantiate a Player

Player.vision_radius = x : xmod45 is how many nodes can be seen by the agent in a circle around the player object


Agent.path_list = [] : define a list of nodes on the grid like I did in the default case for the agent to go to. if you make it a cycle using itertools it will create a closed loop for it to continuously go for

Agent.point_threshold = x : if a pokemon is spotted in the vision radius of the player and its point value is higher than this threshold and it is closer than the previous pokemon target and the point value is higher than the previous target then it will path to that pokemon's last seen position to get it


