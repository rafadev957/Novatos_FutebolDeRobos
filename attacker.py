import math
class Attacker:

    def __init__(self):

        #métodos do robô
        self.id = 0 #identidade
        self.x = 0 #eixo X do robô
        self.y = 0 #eixo Y do robô
        self.orientation = 0 #orientação (radianos)
        self.ve = 0 #velocidade roda esquerda
        self.vd = 0 #velocidade roda direita
        self.xobj = 0 #eixo X do objetivo do robô (bola)
        self.yobj = 0 #eixo Y do objetivo do robô (bola)
        self.estado = "PARADO" #estado do robô
        self.vb = 40 #velocidade base das rodas
        self.kp = 7.5 #ajuste do erro (controlador)
        self.t0 = 0 #tempo inicial de espera (0)
        self.con = None #comunicação
        self.passos = 0 #passos do robô para dar ré


    def setCommunication(self, con):

        #comunicação do simulador e o código (robô)
        self.con = con


    def arrived(self):

        #distância do objetivo e o robô
        d = math.sqrt((self.xobj - self.x)**2 + (self.yobj - self.y)**2)
        print("distância do robô ao obj: {}".format(d))
        return d < 0.05


    def setObj(self, x, y):

        #cria o objetivo do robô a partir do X e Y do robô
        self.xobj = x
        self.yobj = y


    def setPose(self, x, y, orientation):

        #cria a pose do robô, seu x, Y e orientação, a partir do con
        self.x = x
        self.y = y
        self.orientation = orientation


    def controladorP(self, angulo_ro):

        #calcula o "erro" do robô e a bola
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


    def wall_collision(self, t0):
        if (self.x >= 0.73 or self.x <= -0.73) and (self.y >= 0.63 or self.y <= -0.63):
            t = self.con.env.step - t0
            print("tempo na parede: {}".format(t))
            if t >= 5000: #se ele ficar muito parado, então ele travou
                return True
        else:
            return False



    def update(self): #estados do atacante

        angulo_ro = math.atan2(self.yobj - self.y, self.xobj - self.x)
        if self.estado == "IR_ATE":
            # Verifica se o robô bateu na parede
            self.t0 = self.con.env.step
            if self.wall_collision(self.t0) and self.estado == "IR_ATE": #se wall_collision retornar True
                self.estado = "RE" #muda o estado
                print("dando ré")

            else:
                self.controladorP(angulo_ro)
                self.con.sendOne(self.id, self.ve, self.vd)

            #verifica se o robô chegou no objetivo
            if self.arrived():
                self.estado = "ESPERA"
                self.t0 = self.con.env.step
                self.con.sendOne(self.id, 0, 0)

        elif self.estado == "RE":
            self.passos += 1
            self.con.sendOne(self.id, -10, -10)

            if self.passos >= 10: #conta x passos para tras
                self.estado = "IR_ATE" #troca de estado
                self.passos = 0 #reseta os passos


        elif self.estado == "ESPERA":
            t = self.con.env.step - self.t0
            if t >= 2000: #tempo do simulador
                self.estado = "IR_ATE"
            print("tempo de espera do robô: {}".format(t))

        elif self.estado == "PARADO":
            self.estado = "IR_ATE"
