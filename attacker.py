import math
class Attacker:

    def __init__(self):
        self.id = 0
        self.x = 0
        self.y = 0
        self.orientation = 0
        self.ve = 0
        self.vd = 0
        self.xobj = 0
        self.yobj = 0
        self.estado = "PARADO"
        self.vb = 35
        self.kp = 7.5
        self.t0 = 0
        self.con = None

    def setCommunication(self, con):
        self.con = con

    def arrived(self):
        d = math.sqrt((self.xobj - self.x)**2 + (self.yobj - self.y)**2)
        print(d)
        return d < 0.1
    
    def setObj(self, x, y):
        self.xobj = x
        self.yobj = y

    def setPose(self, x, y, orientation):
        self.x = x
        self.y = y
        self.orientation = orientation

    def controladorP(self, angulo_ro):
        erro = angulo_ro - self.orientation

        if math.fabs(erro) > math.pi:
            
            if self.orientation < 0:
                self.orientation = 2*math.pi + self.orientation
            
            if angulo_ro < 0:
                angulo_ro = 2*math.pi + angulo_ro

            erro = angulo_ro - self.orientation

        ce = cd = 0

        cr = self.kp*math.fabs(erro)

        if erro > 0:
            cd = cr
            ce = -cr
        elif erro < 0:
            ce = cr
            cd = -cr
        
        self.ve = self.vb + ce
        self.vd = self.vb + cd


    def update(self):
        angulo_ro = math.atan2(self.yobj - self.y, self.xobj - self.x)
        if self.estado == "IR_ATE":
            self.controladorP(angulo_ro)
            self.con.sendOne(self.id, self.ve, self.vd)
            if self.arrived():
                self.estado = "ESPERA"
                self.t0 = self.con.env.step
                self.con.sendOne(self.id, 0, 0)
                
        elif self.estado == "ESPERA":
            t = self.con.env.step - self.t0
            if t > 2000:
                self.estado = "IR_ATE"
            print(t)
        elif self.estado == "PARADO":
            self.estado = "IR_ATE"