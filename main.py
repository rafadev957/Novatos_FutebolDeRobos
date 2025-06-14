import sys, os, time, math
sys.path.append(os.path.join(os.path.dirname(__file__), 'communication'))
from communication import Communication

con = Communication("127.0.0.1:20011", "224.0.0.1:10002")
con.startServer()

estado = "IR_ATE"
id = 1
objx = 0
objy = 0

vb = 35
ce = 0
cd = 0
kp = 7.5

t0 = 0

def chegou(obj, robot):
    d = math.sqrt((obj.x - robot.x)**2 + (obj.y - robot.y)**2)
    print(d)
    return d < 0.1

def controladorP(angulo_ro, angulo_r):
    erro = angulo_ro - angulo_r

    if math.fabs(erro) > math.pi:
        
        if angulo_r < 0:
            angulo_r = 2*math.pi + angulo_r
        
        if angulo_ro < 0:
            angulo_ro = 2*math.pi + angulo_ro

        erro = angulo_ro - angulo_r

    ce = cd = 0

    cr = kp*math.fabs(erro)

    if erro > 0:
        cd = cr
        ce = -cr
    elif erro < 0:
        ce = cr
        cd = -cr
    
    ve = vb + ce
    vd = vb + cd
    return ve, vd    

while True:
    
    if len(con.frame.robots_yellow) > 0:
        bx = con.frame.ball.x
        by = con.frame.ball.y
        rx = con.frame.robots_yellow[id].x
        ry = con.frame.robots_yellow[id].y
        
        angulo_ro = math.atan2(by - ry, bx - rx)
        angulo_r = con.frame.robots_yellow[id].orientation

        if estado == "IR_ATE":
            ve, vd = controladorP(angulo_ro, angulo_r)
            con.sendOne(id, ve, vd)
            if chegou(con.frame.ball, con.frame.robots_yellow[id]):
                estado = "ESPERA"
                t0 = con.env.step
                con.sendOne(id, 0, 0)
                
        elif estado == "ESPERA":
            t = con.env.step - t0
            if t > 2000:
                estado = "IR_ATE"
            print(t)
        time.sleep(0.1)

        