import sys, os, time
sys.path.append(os.path.join(os.path.dirname(__file__), 'communication'))
from communication import Communication
from attacker import Attacker
from defender import Defender
from goalkeeper import Goalkeeper

#INICIALIZAÇÃO DOS ROBÔS COM AS RESPECTIVAS CLASSES
r0 = Attacker()   #FICA NO CAMPO DE ATAQUE
r1 = Defender()   #FICA NO CAMPO DE DEFESA
r2 = Goalkeeper() #FICA NO CAMPO DO GOL

con = Communication("127.0.0.1:20011", "224.0.0.1:10002")
con.startServer()

#COMUNICAÇÃO DOS ROBÔS COM O SERVIDOR
r0.setCommunication(con)
r1.setCommunication(con)
r2.setCommunication(con)

while True:
    
    if len(con.frame.robots_yellow) > 0: #garante que haja algo na lista de robos

        #POSE DOS ROBÔS EM RELAÇÃO COM O MUNDO
        r0.setPose(con.frame.robots_yellow[r0.id].x, 
                   con.frame.robots_yellow[r0.id].y, 
                   con.frame.robots_yellow[r0.id].orientation)
        r1.setPose(con.frame.robots_yellow[r0.id].x, 
                   con.frame.robots_yellow[r0.id].y, 
                   con.frame.robots_yellow[r0.id].orientation)
        r2.setPose(con.frame.robots_yellow[r2.id].x, 
                   con.frame.robots_yellow[r2.id].y, 
                   con.frame.robots_yellow[r2.id].orientation) 

        #OBJETIVOS DOS ROBÔS
        r0.setObj(con.frame.ball.x, con.frame.ball.y)
        r2.setObj(con.frame.ball.x, con.frame.ball.y)


        #ATUALIZAÇÃO OS ROBÔS NO CAMPO
        #r0.update()
        r1.update()
        #r2.update()

        #TESTES DE SAIDAS AQUI:
        #print(con.frame.robots_yellow[r2.id].x, con.frame.robots_yellow[r2.id].y, con.frame.robots_yellow[r2.id].orientation)
        
        #DELAY DO TEMPO DE RESPOSTA DO SIMULADOR E O CÓDIGO
        time.sleep(0.1)
