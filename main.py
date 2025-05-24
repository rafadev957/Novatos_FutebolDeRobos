import sys, os, time, math
sys.path.append(os.path.join(os.path.dirname(__file__), 'communication'))
from communication import Communication

con = Communication("127.0.0.1:20011", "224.0.0.1:10002")
con.startServer()

while True:
    if len(con.frame.robots_blue) > 0:
        # vetor no plano (x, y) que liga o robô ao objetivo
        objx = con.frame.ball.x - con.frame.robots_blue[0].x
        objy = con.frame.ball.y - con.frame.robots_blue[0].y
        angulo_obj = math.atan2(objy, objx)

        print("Robô", con.frame.robots_blue[0].orientation, "Obj", angulo_obj)
        if con.frame.robots_blue[0].orientation >= angulo_obj - 0.09 and con.frame.robots_blue[0].orientation <=  angulo_obj + 0.09:
            print("ALINHOU!!!!")
            con.sendOne(0, 0, 0, False)
            time.sleep(0.1)
        else:
            con.sendOne(0, -10.5, 10.5, False)
    time.sleep(0.01)