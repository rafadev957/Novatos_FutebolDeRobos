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
        self.tx = 0 #eixo x do robô após um determinado tempo
        self.ty = 0 #eixo y do robô após um determinado tempo
        self.var_posx = 0 #variação do eixo x do robô
        self.var_posy = 0 #variação do eixo y do robô
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


    #LÓGICAS DO ROBÔ A BAIXO:

    def controladorP(self, x, y): #controlador da direção do robô, calcula o "erro" de ângulação entre o robô e a bola
        angulo_ro = math.atan2(y - self.y, x - self.x) # só passar o y e o x do objetivo
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
        if (self.x <= (0.75 - margem_segura) and self.x >= (0 + margem_segura)) and (self.y <= (0.65 - margem_segura) and self.y >= (-0.65 + margem_segura)):
            self.contador = 0
            return False
        
        else:
            self.contador += 1
            #print("contador para perigo: {}".format(self.contador)) #debuger
            #loop para ele não dar ré só por passar na margem
            if self.contador >= 20:
                self.contador = 0
                #print("PERIGO \n"*5) #debuger
                return True

    """
    def stuck(self): #colisão com robôs
        self.tx = self.x
        self.ty = self.y
        self.contador += 1
        #print("timer stuck", self.contador) #debuger
        if self.contador >= 20:
            self.var_posx = abs(self.tx - self.x)
            self.var_posy = abs(self.ty - self.y)
            self.contador = 0

        #verifica a diferença dos eixos
        print("posx: {:.5f} | posy: {:.5f}".format(self.var_posx, self.var_posy)) #debuger
        if self.var_posx <= 0.3 and self.var_posy <= 0.3:
            return True #ta travado
        else:
            return False #não ta travado
    """


    """
    IDEIA: ATACANTE, CORRE ATRÁS DA BOLA COMO OBJETIVO, SE A BOLINHA ESTIVER NO CAMPO DE DEFESA
    ELE PARA E VAI NA LINHA X = 0 E Y = 0, PARA ESPERAR A BOLA VOLTA AO CAMPO DE ATAQUE
    """

    def update(self): #estados do atacante
        if self.x < 0.05:
            self.estado = "ALINHAR"

        if self.estado == "ATACAR":
            #corre atrás da bola
            self.controladorP(self.xobj, self.yobj) #parâmetros de x e y como objetivo
            self.con.sendOne(self.id, self.ve, self.vd)

            #verifica se o robô está fora do retangulo seguro
            if self.collision(): #or self.stuck
                self.estado = "RE" #muda o estado
            

        elif self.estado == "ALINHAR":
            self.controladorP(0.2, 0) # parâmetros de alinhamento, x e y do objetivo dado ao robô
            self.con.sendOne(self.id, self.ve, self.vd)
            if self.arrived() < 0.1: #chegou no objetivo
                self.estado = "ESPERA"


        elif self.estado == "RE":
            #print("dando ré") #debuger da ré
            self.con.sendOne(self.id, -40, -40)
            self.passos += 1
            if self.passos >= 10: #conta x passos para trás
                self.con.sendOne(self.id, 0, 0)
                self.passos = 0 #reseta os passos
                self.estado = "ATACAR" #troca de estado

                if self.xobj < 0:
                    self.estado = "ALINHAR"


        elif self.estado == "ESPERA":
            self.con.sendOne(self.id, 0, 0)
            if self.xobj >= 0.1: #a bola esta no campo de ataque
                self.estado = "ATACAR"
            elif self.x < 0.1: #o robô esta no campo de defesa
                self.estado = "ALINHAR"


        elif self.estado == "PARADO":
            self.estado = "ALINHAR"