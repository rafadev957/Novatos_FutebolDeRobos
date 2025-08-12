import sys, os, time, math
sys.path.append(os.path.join(os.path.dirname(__file__), 'communication'))
from communication import Communication
from attacker import Attacker

r0 = Attacker()

con = Communication("127.0.0.1:20011", "224.0.0.1:10002")
con.startServer()

r0.setCommunication(con)

while True:
    
    if len(con.frame.robots_yellow) > 0:

        r0.setObj(con.frame.ball.x, con.frame.ball.y)

        r0.setPose(con.frame.robots_yellow[r0.id].x, 
                   con.frame.robots_yellow[r0.id].y, 
                   con.frame.robots_yellow[r0.id].orientation) 

        r0.update()
        time.sleep(0.1)
