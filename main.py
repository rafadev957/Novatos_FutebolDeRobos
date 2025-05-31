import sys, os, time, math
sys.path.append(os.path.join(os.path.dirname(__file__), 'communication'))
from communication import Communication

con = Communication("127.0.0.1:20011", "224.0.0.1:10002")
con.startServer()

estado = "ANDAR_FRENTE"
id = 1
while True:
    
    if len(con.frame.robots_yellow) > 0:
        bx = con.frame.ball.x
        by = con.frame.ball.y
        rx = con.frame.robots_yellow[id].x
        ry = con.frame.robots_yellow[id].y
        angulo_ro = math.atan2(by - ry, bx - rx)
        angulo_r = con.frame.robots_yellow[id].orientation
        if estado == "ANDAR_FRENTE":
            con.sendOne(id, 15.5, 15.5)
            t0 = con.env.step
            estado = "ESPERA"
        elif estado == "ESPERA":
            t = con.env.step - t0
            if (angulo_ro - angulo_r < -0.5 or angulo_ro - angulo_r > 0.5) and t > 800:
                estado = "ALINHAR"
            print(estado, "tempo decorrido:", t)
        elif estado == "ALINHAR":
            if angulo_ro - angulo_r >= -0.05 and angulo_ro - angulo_r <= 0.05:
                estado = "ANDAR_FRENTE"
                con.sendOne(id, 0, 0)
            else:
                con.sendOne(id, -4, 4)
            print(estado, angulo_ro - angulo_r)