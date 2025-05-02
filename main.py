import sys, os, time
sys.path.append(os.path.join(os.path.dirname(__file__), 'communication'))
from communication import Communication

con = Communication("127.0.0.1:20011", "224.0.0.1:10002")
con.startServer()
while True:
    con.sendOne(0, 1.5, 0) 
    print(con.frame.ball.x, con.frame.ball.y)
    time.sleep(0.1)