import math
class Defender:

    def __init__(self): #métodos do robô
        self.id = 1 #identidade padrão
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


    def setObj(self, x, y): #cria o objetivo do robô sendo a bola a partir dos eixos X e Y do robô
        self.xobj = -0.3
        self.yobj = 0


    def setPose(self, x, y, orientation): #cria a pose do robô (seu X, Y e Orientação) a partir da comunicação
        self.x = x
        self.y = y
        self.orientation = orientation


    #LÓGICAS DO ROBÔ A BAIXO:

    def arrived(self): #distância do objetivo e o robô
        """
        IDEIA: O DEFENSOR SEGUE A BOLA NO EIXO Y, SE ELA PASSA O MEIO DO CAMPO SÓ O DEFENSOR ATUA
        """
        d = math.sqrt((self.con.frame.ball.x - self.x)**2 + (self.con.frame.ball.y - self.y)**2)
        #print("distância do robô ao obj: {:.4f}".format(d))
        return d < 0.1 #retorna a distância quando for menor que 0.1


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

        self.setObj(self.x, self.con.frame.ball.y) #obj do robô é o seu próprio x e a posição do eixo y da bola

        if self.estado == "ALINHAR":
            #verifica se o robô está fora do retangulo seguro
            if self.collision():
                self.estado = "RE" #muda o estado


            #verifica se o robô chegou no objetivo
            elif self.arrived():
                self.estado = "ESPERA"


        elif self.estado == "RE":
            #print("dando ré") #debuger da ré
            self.con.sendOne(self.id, -30, -30)
            self.passos += 1
            if self.passos >= 10: #conta x passos para trás
                self.passos = 0 #reseta os passos
                self.estado = "ALINHAR" #troca de estado


        elif self.estado == "ESPERA":
            self.con.sendOne(self.id, 0, 0)
            if (self.yobj - self.y) > 0.1: #se a diferença do eixo y da bola com o do robô
                self.estado = "ALINHAR"


        elif self.estado == "PARADO":
            self.estado = "ALINHAR"