import sys, os, time
sys.path.append(os.path.join(os.path.dirname(__file__), 'communication'))
from communication import Communication

con = Communication("127.0.0.1:20011", "224.0.0.1:10002")
con.startServer()

t = 0
while True:
    if t // 100 % 2 == 0 and t % 100 == 0:
        #Time amarelo
        con.sendOne(0, 6.5, 0)
        con.sendOne(1, 5.0, 0.5)
        con.sendOne(2, -2, 2)
        #Time azul
        con.sendOne(0, -0.5, -0.5, False)
        con.sendOne(1, 5, -5, False)
        con.sendOne(2, -0.5, -1.0, False)
    elif t % 100 == 0:
        con.sendOne(0, -6.5, 0)
        con.sendOne(1, -5.0, -0.5)
        con.sendOne(2, 2, -2)
        #Time azul
        con.sendOne(0, 0.5, 0.5, False)
        con.sendOne(1, -5, 5, False)
        con.sendOne(2, 0.5, 1.0, False)
    print(con.frame.ball.x, con.frame.ball.y)
    if len(con.frame.robots_blue) > 0:
        for i in range(len(con.frame.robots_blue)):
            print(i, con.frame.robots_blue[i].x, 
                     con.frame.robots_blue[i].y,
                     con.frame.robots_blue[i].orientation
            )
    print()
    if len(con.frame.robots_yellow) > 0:
        for i in range(len(con.frame.robots_yellow)):
            print(i, con.frame.robots_yellow[i].x, 
                     con.frame.robots_yellow[i].y,
                     con.frame.robots_yellow[i].orientation
            )
    print(t, "---------------------------------", con.env.step)
    time.sleep(0.1)
    t += 1 