import math
from robot import Robot

class Attacker(Robot):  #herdo de robot

    def __init__(self, id, vb): #atributos do robô
        super().__init__(id, vb)
        self.xobj = 0 #eixo X do objetivo do robô (bola)
        self.yobj = 0 #eixo Y do objetivo do robô (bola)
        self.kp = 7.5 #ajuste do erro (controladorP)
        self.t0 = 0 #tempo inicial de espera
        self.passos = 0 #passos do robô para dar ré
        self.contador = 0 #contador de tempo da ré e do stuck
    
    
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
        d = math.sqrt((0.1 - self.x)**2 + (0 - self.y)**2)
        #print("distância do robô ao obj: {:.4f}".format(d))
        if d <= 0.1:
            return True


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
        foul = self.referee.foul
        if foul != vssref_common_pb2.GAME_ON:
            self.estado = "ESPERA_RECOMECO"
        """if foul == vssref_common_pb2.FREE_BALL:
            #print("Free ball")
            self.estado = "ESPERA_RECOMECO"
            #if self.referee.team == vssref_common_pb2.YELLOW:
                #print("Ocorreu falta para o time azul")
            #if self.referee.quadrant == vssref_common_pb2.QUADRANT_1:
                #print("Ocorreu no quadrante 1")
        elif foul == vssref_common_pb2.GAME_ON:
            #print("Recomeçou")
            self.estado = "ATACAR"
        """

        angulo_ro = math.atan2(self.yobj - self.y, self.xobj - self.x)
        
        if self.collision() == True:
            self.estado = "RE" #muda o estado


        if self.x < 0:
            self.estado = "ALINHAR"

        if self.estado == "ATACAR":
            #corre atrás da bola
            self.controladorP(angulo_ro) #parâmetros de x e y como objetivo
            self.con.sendOne(self.id, self.ve, self.vd,False)
            #verifica se o robô está fora do retangulo seguro
            

        elif self.estado == "ALINHAR":
            angulo_ro = math.atan2(0 - self.y, 0.1 - self.x) # yobjetivo, xobjetivo
            erro = angulo_ro - self.orientation

            if math.fabs(erro) > math.pi:
                
                if self.orientation < 0: #orientação negativa
                    self.orientation = 2*math.pi + self.orientation
                
                if angulo_ro < 0:
                    angulo_ro = 2*math.pi + angulo_ro

                erro = angulo_ro - self.orientation

            if erro > 0.4:
                self.con.sendOne(self.id, -4, 4,False)
            elif erro < -0.4:
                self.con.sendOne(self.id, 4, -4,False)
            else:
                self.con.sendOne(self.id, self.vb, self.vb,False)
            
            if self.arrived(): #chegou no objetivo
                self.estado = "ESPERA"


        elif self.estado == "RE":
            #print("dando ré") #debuger da ré
            self.con.sendOne(self.id, -self.vb, -self.vb,False)
            self.passos += 1
            if self.passos >= 10: #conta x passos para trás
                self.con.sendOne(self.id, 0, 0,False)
                self.passos = 0 #reseta os passos
                if self.passos == 0:
                    self.estado = "ATACAR" #troca de estado
                if self.xobj < 0.1 and self.collision() == False:
                    self.estado = "ALINHAR"


        elif self.estado == "ESPERA":
            self.con.sendOne(self.id, 0, 0,False)
            
            if self.collision() == True:
                self.estado == "RE"
                
            elif self.xobj > 0.1 and self.estado != "RE": #a bola esta no campo de ataque
                self.estado = "ATACAR"
            elif self.x < 0.1 and self.estado != "RE": #o robô esta no campo de defesa
                self.estado = "ALINHAR"


        elif self.estado == "PARADO":
            self.estado = "ALINHAR"


        elif self.estado == "ESPERA_RECOMECO":
            self.con.sendOne(self.id,0,0,False)
            if foul == vssref_common_pb2.GAME_ON:
                self.estado = "ATACAR"
    
        #print(self.estado)