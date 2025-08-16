import sys, os, time
sys.path.append(os.path.join(os.path.dirname(__file__), 'communication'))
from communication import Communication
from attacker import Attacker
from defender import Defender
from goalkeeper import Goalkeeper

r0 = Attacker()

con = Communication("127.0.0.1:20011", "224.0.0.1:10002")
con.startServer()

r0.setCommunication(con)
#adicionar mais robôs: r1.id = 1 ou r2.id = 2

while True:
    
    if len(con.frame.robots_yellow) > 0: #garante que haja algo na lista de robos

        r0.setObj(con.frame.ball.x, con.frame.ball.y)

        r0.setPose(con.frame.robots_yellow[r0.id].x, 
                   con.frame.robots_yellow[r0.id].y, 
                   con.frame.robots_yellow[r0.id].orientation) 

        r0.update()
        time.sleep(0.1)
