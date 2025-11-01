import sys, os, time, math
sys.path.append(os.path.join(os.path.dirname(__file__), 'communication'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'model'))
from communication import Communication
from referee import Referee
from worldModel import WorldModel

ref = Referee("224.5.23.2:10004", "224.5.23.2:10003")
ref.startServer()

con = Communication("127.0.0.1:20011", "224.0.0.1:10002")
con.startServer()

worldModel = WorldModel()

worldModel.setCommunicationAndReferee(con, ref)

"""exemplo para pegar a velociade do robô n rn.setVelocity(con.frame.robots_yellow[rn.id].vx, con.frame.robots_yellow[rn.id].vy) -> velocidade me x e y do robô n"""

while True:
    worldModel.update()    
    time.sleep(0.1)