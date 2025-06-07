import sys, os, time, math
sys.path.append(os.path.join(os.path.dirname(__file__), 'communication'))
from communication import Communication

con = Communication("127.0.0.1:20011", "224.0.0.1:10002")
con.startServer()

estado = "ONDE_ESTOU"
novo_estado = estado
id = 1
objx = 0
objy = 0

while True:
    
    if len(con.frame.robots_yellow) > 0:
        bx = con.frame.ball.x
        by = con.frame.ball.y
        rx = con.frame.robots_yellow[id].x
        ry = con.frame.robots_yellow[id].y
        
        angulo_ro = math.atan2(objy - ry, objx - rx)

        angulo_r = con.frame.robots_yellow[id].orientation

        if estado == "ONDE_ESTOU":
            if rx < 0 and ry > 0: #Q2
                objx = -0.38
                objy = -0.44
            elif rx < 0 and ry < 0: #Q3
                objx = 0.38
                objy = -0.44
            elif rx > 0 and ry < 0: #Q1
                objx = 0.38
                objy = 0.44
            else: # Q4
                objx = -0.38
                objy = 0.44
            
            estado = "ALINHAR"


        elif estado == "ANDAR_FRENTE":
            t2 = con.env.step
            if (t2 - t1 > 600):
                con.sendOne(id, 15.5, 15.5)
            else:
                con.sendOne(id, 0, 0)

            # Transição
            objr = 0.03
            if rx < objx+objr and rx > objx-objr and ry > objy-objr and ry < objy+objr:
                print("Cheguei")
                con.sendOne(id, 0, 0)
                estado = "ONDE_ESTOU"

        elif estado == "ESPERA":
            t = con.env.step - t0
            if (angulo_ro - angulo_r < -0.5 or angulo_ro - angulo_r > 0.5) and t > 800:
                estado = "ALINHAR"
            print(estado, "tempo decorrido:", t)

        elif estado == "ALINHAR":
            t1 = con.env.step
            if angulo_ro - angulo_r >= -0.05 and angulo_ro - angulo_r <= 0.05:
                estado = "ANDAR_FRENTE"
                con.sendOne(id, 0, 0)
            else:
                con.sendOne(id, -4, 4)
        
        if estado != novo_estado:
            print("Estado", estado)
            novo_estado = estado