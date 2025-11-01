from entity import Entity

class Ball(Entity):

    def __init__(self):
        self.vx = 0
        self.vy = 0
        self.con = None
    
    def setCommunication(self, con):
        self.con = con

    def update(self): #entidade de criação não pode ter acesso a comunicação
        self.x = self.con.ball.x
        self.y = self.con.ball.y
        self.vx = self.con.ball.vx
        self.vy = self.con.ball.vy