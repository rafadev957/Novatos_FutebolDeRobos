import math
class Goalkeeper:

    def __init__(self): #métodos do robô
        self.id = 2 #identidade padrão
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


    def collision(self): #colisão com parede
        #tamanho do campo - margem = perigo
        margem_segura = 0.1 #não para nas quinas, variável local
        if (self.x <= (0.75 - margem_segura) and self.x >= (-0.75 + margem_segura)) and (self.y <= (0.65 - margem_segura) and self.y >= (-0.65 + margem_segura)):
            self.contador_re = 0
            return False

        else:
            self.contador_re += 1
            print("contador para perigo: {}".format(self.teste)) #debuger
            #loop para ele não dar ré só por passar na margem
            if self.contador_re >= 45:
                self.contador_re = 0
                print("PERIGO \n"*5) #debuger
                return True


    def alignment(self):
        correcao = abs(self.yobj - self.y)*100 #Calculo da velocidade para alinhar com a bolinha (não sei se é a melhor forma de calcular a correção)
        #quando a bolinha esta dentro das linhas da trave
        if self.yobj<= 0.19 and self.yobj >= -0.19:
            if self.y <= self.yobj:
                self.vd = correcao
                self.ve = correcao
            else: 
                self.vd = -correcao
                self.ve = -correcao
        #quando esta acima das traves
        elif self.yobj > 0.19:
            if self.y < 0.19:
                self.vd = correcao
                self.ve = correcao
            else:
                self.vd = 0
                self.ve = 0
        #quando esta abaixo das traves
        elif self.yobj < -0.19:
            if self.y > -0.19:
                self.vd = -correcao
                self.ve = -correcao
            else:
                self.vd = 0
                self.ve = 0
            

    def update(self): #estados do goleiro
        
        angulo_ro = math.atan2(self.yobj - self.y, self.xobj - self.x)
        if self.estado == "Alinhar_bolinha":
            self.alignment()
            self.con.sendOne(self.id, self.ve, self.vd)


            #verifica se o robô está fora do retangulo seguro
            '''if self.wall_collision():
                self.estado = "RE"''' #muda o estado


            #verifica se o robô chegou no objetivo
            #if self.arrived():
                #pass
                #self.estado = "ESPERA"
                #self.t0 = self.con.env.step #timer
                #self.con.sendOne(self.id, 0, 0)


        elif self.estado == "RE":
            print("dando ré") #debuger da ré
            self.con.sendOne(self.id, -30, -30)
            self.passos += 1
            if self.passos >= 10: #conta x passos para trás
                self.passos = 0 #reseta os passos
                self.estado = "IR_ATE" #troca de estado


        elif self.estado == "ESPERA":
            t = self.con.env.step - self.t0
            if t >= 2000: #tempo do simulador
                self.estado = "IR_ATE"
            print("tempo de espera do robô: {}".format(t))


        elif self.estado == "PARADO":
            erro = math.pi/2 - self.orientation #calculo do erro de alinhamento com a vertical se orientando para cima
            vr = abs(erro)*10 #calculo da velocidade de rotação proporcional ou tamanho do erro
    
            if self.orientation <= math.pi/2 - 0.001:
                self.con.sendOne(self.id,-vr,vr)
            elif self.orientation >= math.pi/2 + 0.001:
                self.con.sendOne(self.id,vr,-vr)
            else:
                self.con.sendOne(self.id,0,0)
                self.estado = "Alinhar_bolinha"