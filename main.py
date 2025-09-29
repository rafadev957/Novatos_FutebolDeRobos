import sys, os, time
sys.path.append(os.path.join(os.path.dirname(__file__), 'communication'))
from communication import Communication
from referee import Referee
from attacker import Attacker
from defender import Defender
from goalkeeper import Goalkeeper

#INICIALIZAÇÃO DOS ROBÔS COM AS RESPECTIVAS CLASSES
r0 = Attacker()   #FICA NO CAMPO DE ATAQUE
r1 = Defender()   #FICA NO CAMPO DE DEFESA
r2 = Goalkeeper() #FICA NO CAMPO DO GOL

ref = Referee("224.5.23.2:10004", "224.5.23.2:10003")
ref.startServer()

con = Communication("127.0.0.1:20011", "224.0.0.1:10002")
con.startServer()

#COMUNICAÇÃO DOS ROBÔS COM O SERVIDOR
r0.setCommunication(con, ref)
r1.setCommunication(con, ref)
r2.setCommunication(con, ref)

while True:
    
    if len(con.frame.robots_blue) > 0: #garante que haja algo na lista de robos

        #POSE DOS ROBÔS EM RELAÇÃO COM O MUNDO
        r0.setPose(con.frame.robots_blue[r0.id].x, 
                   con.frame.robots_blue[r0.id].y, 
                   con.frame.robots_blue[r0.id].orientation)
        r1.setPose(con.frame.robots_blue[r1.id].x, 
                   con.frame.robots_blue[r1.id].y, 
                   con.frame.robots_blue[r1.id].orientation)
        r2.setPose(con.frame.robots_blue[r2.id].x, 
                   con.frame.robots_blue[r2.id].y, 
                   con.frame.robots_blue[r2.id].orientation) 

        #OBJETIVOS DOS ROBÔS
        r0.setObj(con.frame.ball.x, con.frame.ball.y)
        r1.setObj(con.frame.ball.x, con.frame.ball.y)
        r2.setObj(con.frame.ball.x, con.frame.ball.y)


        #ATUALIZAÇÃO OS ROBÔS NO CAMPO
        r0.update()
        r1.update()
        r2.update()

        #TESTES DE SAIDAS AQUI:
        #print(con.frame.robots_yellow[r2.id].x, con.frame.robots_yellow[r2.id].y, con.frame.robots_yellow[r2.id].orientation)
        
        #DELAY DO TEMPO DE RESPOSTA DO SIMULADOR E O CÓDIGO
        time.sleep(0.1)


"""
exemplo para pegar a velociade do robô n
r1.setVelocity(con.frame.robots_yellow[r1.id].vx, 
                       con.frame.robots_yellow[r1.id].vy)
"""