# README
The topology used is the same as Step3 and can be seen in the report, below is the node and corresponding localhost port number:  
A: 8001  
B: 8002  
C: 8003  
D: 8004  
E: 8005   
To reproduce the result, open 5 terminals, switch the working directory to /Step4 Code/step3_modified, and execute these 5 commands separately in the 5 terminals, each would set up a node  
python3 Main.py 8001 10 localhost 8002 10.0 localhost 8003 4.0 localhost 8004 8.0  
python3 Main.py 8002 10 localhost 8001 6.0 localhost 8004 2.0 localhost 8005 2.0  
python3 Main.py 8003 10 localhost 8001 4.0  
python3 Main.py 8004 10 localhost 8001 5.0 localhost 8002 3.0 localhost 8005 7.0  
python3 Main.py 8005 10 localhost 8002 1.0 localhost 8004 5.0  
  
After executing all the commands, open a new terminal, and switch the current working directory to \'92Step4 Code\'92, then execute  
python3 Jtracerout.py  
  
And then input   
  
port_origin: 8080  
addr_designated: localhost:8003  
addr_destination: localhost:8005  
  
Which will send a tracroute packet from localhost:port_origin to addr_designated and get the traceroute from addr_designated to addr_destination  
  
Note: when the topology is first set up, it may take a while for the routing tables to converge using Bellman-Ford algorithm, so the early few attempts may fail, but Jtracerout.py implemented an auto retry after a timeout of 5 seconds for a maximum of 50 times, eventually we would get the expected trace route .  
  
Reference:  
This code is built upon the work of jambs (GitHub:https://github.com/jamiis/distributed-bellman-ford#user-input)}
