# README  
The topology used can be seen in the report, below is the node and corresponding localhost port number:
A: 8001  
B: 8002  
C: 8003  
D: 8004  
E: 8005  
To reproduce the result, open 5 terminals, switch the working directory to \'92Step3 Code\'92, and execute these 5 commands separately in the 5 terminals, each would set up a node    
python3 Main.py 8001 10 localhost 8002 10.0 localhost 8003 4.0 localhost 8004 8.0  
python3 Main.py 8002 10 localhost 8001 6.0 localhost 8004 2.0 localhost 8005 2.0  
python3 Main.py 8003 10 localhost 8001 4.0  
python3 Main.py 8004 10 localhost 8001 5.0 localhost 8002 3.0 localhost 8005 7.0  
python3 Main.py 8005 10 localhost 8002 1.0 localhost 8004 5.0  
After executing all the commands, in the terminal for one specific node (for example B),  
type neighbors to show the neighbors of the node (node B)  
type showrt to print the routing table for the node (node B)  
type close to shutdown the node (node B)  
  
Reference:  
This code is built upon the work of jambs (GitHub:https://github.com/jamiis/distributed-bellman-ford#user-input)}
