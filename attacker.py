import math
class Attacker:

    def __init__(self): #métodos do robô
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
        self.passos = 0 #passos do robô para dar ré
        self.teste = 0 #TESTE CONTADOR DA RÉ
        self.con = None #comunicação


    def setCommunication(self, con): #comunicação do simulador e o código (robô)
        self.con = con


    def setObj(self, x, y): #cria o objetivo do robô a partir do X e Y do robô
        self.xobj = x
        self.yobj = y


    def setPose(self, x, y, orientation): #cria a pose do robô (seu X, Y e Orientação) a partir da comunicação
        self.x = x
        self.y = y
        self.orientation = orientation


    def controladorP(self, angulo_ro): #controlador da direção do robô, calcula o "erro" de ângulação entre o robô e a bola
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


    def arrived(self): #distância do objetivo e o robô
        d = math.sqrt((self.xobj - self.x)**2 + (self.yobj - self.y)**2)
        print("distância do robô ao obj: {:.4f}".format(d))
        return d < 0.1


    def wall_collision(self): #colisão com parede
        #tamanho do campo - margem = perigo
        margem_segura = 1 #não para nas quinas, variável local
        if (self.x <= (0.75 - margem_segura) and self.x >= (-0.75 - margem_segura)) and (self.y <= (0.65 - margem_segura) and self.y >= (-0.65 - margem_segura)):
            return False
        else:
            self.teste += 1
            print("contador para perigo: {}".format(self.teste)) #debuger
            #loop para ele não dar ré só por passar na margem
            if self.teste >= 50:
                self.teste = 0
                print("PERIGO"*5) #debuger
                return True


    def update(self):
        #estados do atacante
        angulo_ro = math.atan2(self.yobj - self.y, self.xobj - self.x)
        if self.estado == "IR_ATE":
            self.controladorP(angulo_ro)
            self.con.sendOne(self.id, self.ve, self.vd)


            #verifica se o robô está fora do retangulo seguro
            if self.wall_collision():
                self.estado = "RE" #muda o estado


            #verifica se o robô chegou no objetivo
            if self.arrived():
                pass
                #self.estado = "ESPERA"
                #self.t0 = self.con.env.step #timer
                #self.con.sendOne(self.id, 0, 0)


        elif self.estado == "RE":
            print("dando ré") #debuger da ré
            self.con.sendOne(self.id, -30, -30)
            self.passos += 1
            if self.passos >= 8: #conta x passos para trás
                self.passos = 0 #reseta os passos
                self.estado = "IR_ATE" #troca de estado


        elif self.estado == "ESPERA":
            t = self.con.env.step - self.t0
            if t >= 2000: #tempo do simulador
                self.estado = "IR_ATE"
            print("tempo de espera do robô: {}".format(t))


        elif self.estado == "PARADO":
            self.estado = "IR_ATE"
