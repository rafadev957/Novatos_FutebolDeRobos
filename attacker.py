import math
class Attacker:

    def __init__(self): #atributos do robô
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
        self.kp = 7.5 #ajuste do erro (controladorP)
        self.t0 = 0 #tempo inicial de espera
        self.passos = 0 #passos do robô para dar ré
        self.contador = 0 #contador de tempo da ré e do stuck
        #self.tx = 0 #eixo x do robô após um determinado tempo
        #self.ty = 0 #eixo y do robô após um determinado tempo
        #self.var_posx = 0 #variação do eixo x do robô
        #self.var_posy = 0 #variação do eixo y do robô
        #self.vx = 0
        #self.vy = 0
        self.con = None #comunicação


    def setCommunication(self, con): #comunicação do simulador e o código (robô)
        self.con = con


    def setObj(self, x, y): #cria o objetivo do robô sendo a bola a partir dos eixos X e Y do robô
        self.xobj = x
        self.yobj = y


    def setPose(self, x, y, orientation): #cria a pose do robô (seu X, Y e Orientação) a partir da comunicação
        self.x = x
        self.y = y
        self.orientation = orientation
    

    """def getVelocity(self):
        return math.sqrt()"""

    
    """def setVelocity(self, vx, vy):
        self.vx = vx
        self.vy = vy"""


    #LÓGICAS DO ROBÔ A BAIXO:
    """REDUZIR O OVERSHOOT (ROBÔ SAMBANDO)"""
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
        d = math.sqrt((0.10 - self.x)**2 + (0 - self.y)**2)
        #print("distância do robô ao obj: {:.4f}".format(d))
        return d


    def collision(self): #colisão com parede
        #tamanho do campo - margem = perigo
        margem_segura = 0.1 #não para nas quinas, variável local
        # 0.75 >= x >= 0 and 0.65 >= y >= -0.65
        if (self.x <= (0.75 - margem_segura) and self.x >= (-0.75 + margem_segura)) and (self.y <= (0.65 - margem_segura) and self.y >= (-0.65 + margem_segura)):
            self.contador = 0
            return False
        
        else:
            self.contador += 1
            #print("contador para perigo: {}".format(self.contador)) #debuger
            #loop para ele não dar ré só por passar na margem
            if self.contador >= 18:
                self.contador = 0
                #print("PERIGO \n"*5) #debuger
                return True
            

    """
    IDEIA: ATACANTE, CORRE ATRÁS DA BOLA COMO OBJETIVO, SE A BOLINHA ESTIVER NO CAMPO DE DEFESA
    ELE PARA E VAI NA LINHA X = 0 E Y = 0, PARA ESPERAR A BOLA VOLTA AO CAMPO DE ATAQUE
    """

    def update(self): #estados do atacante
        angulo_ro = math.atan2(self.yobj - self.y, self.xobj - self.x)
        if self.x < 0.05:
            self.estado = "ALINHAR"

        if self.estado == "ATACAR":
            #corre atrás da bola
            self.controladorP(angulo_ro) #parâmetros de x e y como objetivo
            self.con.sendOne(self.id, self.ve, self.vd)

            #verifica se o robô está fora do retangulo seguro
        if self.collision() == True:
            self.estado = "RE" #muda o estado
            

        elif self.estado == "ALINHAR":
            angulo_ro = math.atan2(0 - self.y, 0.2 - self.x)
            self.controladorP(angulo_ro) # parâmetros de alinhamento, x e y do objetivo dado ao robô
            self.con.sendOne(self.id, self.ve, self.vd)
            if self.arrived() < 0.1: #chegou no objetivo
                self.estado = "ESPERA"


        elif self.estado == "RE":
            #print("dando ré") #debuger da ré
            self.con.sendOne(self.id, -self.vb, -self.vb)
            self.passos += 1
            if self.passos >= 10: #conta x passos para trás
                self.con.sendOne(self.id, 0, 0)
                self.passos = 0 #reseta os passos
                self.estado = "ATACAR" #troca de estado

                if self.xobj < 0:
                    self.estado = "ALINHAR"


        elif self.estado == "ESPERA":
            self.con.sendOne(self.id, 0, 0)
            if self.xobj >= 0.3: #a bola esta no campo de ataque
                self.estado = "ATACAR"
            elif self.x < 0: #o robô esta no campo de defesa
                self.estado = "ALINHAR"


        elif self.estado == "PARADO":
            self.estado = "ALINHAR"