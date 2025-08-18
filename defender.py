import math
class Defender:

    def __init__(self): #métodos do robô
        self.id = 0 #identidade padrão
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
        self.t0 = 0 #tempo inicial de espera
        self.passos = 0 #passos do robô para dar ré
        self.contador_re = 0 #contador de tempo para a ré
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
        """
        isto pode sofrer alterações, a área de defesa pode ser altera
        -0.50 x e 0 y significa o local onde o robo 1 spawna
        """
        d = math.sqrt((-0.50 - self.x)**2 + (0 - self.y)**2) #defensor precisa estar na área de defesa
        #print("distância do robô ao obj: {:.4f}".format(d))
        return d < 0.1


    def collision(self): #colisão com parede
        #tamanho do campo - margem = perigo
        margem_segura = 0.1 #não para nas quinas, variável local
        if (self.x <= (0.75 - margem_segura) and self.x >= (-0.75 + margem_segura)) and (self.y <= (0.65 - margem_segura) and self.y >= (-0.65 + margem_segura)):
            self.contador_re = 0
            return False

        else:
            self.contador_re += 1
            #print("contador para perigo: {}".format(self.teste)) #debuger
            #loop para ele não dar ré só por passar na margem
            if self.contador_re >= 45:
                self.contador_re = 0
                #print("PERIGO \n"*5) #debuger
                return True


    def update(self): #estados do defensor

        angulo_ro = math.atan2(self.yobj - self.y, self.xobj - self.x)
        if self.estado == "IR_ATE":
            self.controladorP(angulo_ro)
            self.con.sendOne(self.id, self.ve, self.vd)


            #verifica se o robô está fora do retangulo seguro
            if self.collision():
                self.estado = "RE" #muda o estado


            #verifica se o robô chegou no objetivo
            elif self.arrived():
                self.estado = "ESPERA"
                self.con.sendOne(self.id, 0, 0)


        elif self.estado == "RE":
            #print("dando ré") #debuger da ré
            self.con.sendOne(self.id, -30, -30)
            self.passos += 1
            if self.passos >= 10: #conta x passos para trás
                self.passos = 0 #reseta os passos
                self.estado = "IR_ATE" #troca de estado


        elif self.estado == "ESPERA":
            if self.xobj <= 0:
                self.estado = "IR_ATE"
                print("bola está na área de defesa")
                #ideia: defensor vai na bola, depois volta ao local "objetivo"


        elif self.estado == "PARADO":
            self.estado = "IR_ATE"