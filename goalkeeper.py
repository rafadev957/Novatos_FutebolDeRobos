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


    def AlignmentWithBall(self):
        self.vb = abs(self.yobj - self.y)*60 + 50*abs(self.xobj)/0.75 #Calculo da velocidade para alinhar com a bolinha (não sei se é a melhor forma de calcular a correção)
        #print(self.vb)
        if self.xobj < 0: #Para o goleiro amarelo: se a bola estiver no campo de defesa se alinha com a bolinha, se não centraliza
            #quando a bolinha esta dentro das linhas da trave
            if self.yobj<= 0.19 and self.yobj >= -0.19:
                if self.y <= self.yobj:
                    self.vd = self.vb
                    self.ve = self.vb
                else: 
                    self.vd = -self.vb
                    self.ve = -self.vb
            #quando esta acima das traves
            elif self.yobj > 0.19:
                if self.y < 0.19:
                    self.vd = self.vb
                    self.ve = self.vb
                else:
                    self.vd = 0
                    self.ve = 0
            #quando esta abaixo das traves
            elif self.yobj < -0.19:
                if self.y > -0.19:
                    self.vd = -self.vb
                    self.ve = -self.vb
                else:
                    self.vd = 0
                    self.ve = 0
        else:
            self.yobj = 0 #Setando o yobj como o meio do gol
            self.vb = 40
            if self.y <= self.yobj + 0.02 and self.y >= self.yobj - 0.02:
                self.vd = 0
                self.ve = 0
            elif self.y > self.yobj:
                self.vd = -self.vb
                self.ve = -self.vb
            elif self.y < self.yobj:
                self.vd = self.vb
                self.ve = self.vb

    def PositionCheck(self): 
        #Se o goleiro sair das linhas da trave, ele volta para o limite delas
        if self.y <= -0.19 - 0.02:
            self.ve = 30
            self.vd = 30
        elif self.y >= 0.19 + 0.02:
            self.ve = -30
            self.vd = -30
    
    def AlignmentWithX(self): #Se perder o alinhamento com x do gol (-0.7 ou -0.69) 
        self.xobj = -0.69
        self.yobj = 0
        d = math.sqrt((self.xobj - self.x)**2 +(self.yobj - self.y)**2) #distância do robô ao ponto (-0.69,0)
        angulo_ro = math.atan2(self.yobj - self.y, self.xobj - self.x) #ângulo de erro em relação ao ponto (-0.69,0)
        erro = angulo_ro - self.orientation 

        #correção em relação ao pi e -pi 
        if math.fabs(erro) > math.pi: 
            if self.orientation < 0:
                self.orientation = 2*math.pi + self.orientation
            if angulo_ro < 0:
                angulo_ro = 2*math.pi + angulo_ro
            erro = angulo_ro - self.orientation
        ce = cd = 0
        cr = self.kp*abs(erro) #Correção das velocidades proporcional ao erro
        if erro < 0 - 0.05:
            self.ve = cr 
            self.vd = -cr
        elif erro > 0 + 0.05:
            self.ve = -cr
            self.vd = cr
        else: #Se estiver alinhado anda reto
            self.ve = 10
            self.vd = 10
        if d <= 0.01:
            self.estado = "Alinhar_Vertical"

    def update(self): #estados do goleiro
        
        angulo_ro = math.atan2(self.yobj - self.y, self.xobj - self.x)
        if self.estado == "Alinhar_Bolinha":
            self.AlignmentWithBall()
            self.PositionCheck()
            self.con.sendOne(self.id, self.ve, self.vd)

            #Se perder o alinhamento com a vertical, realinhar com a vertical orientando apra cima
            if self.orientation <= math.pi/2 - 0.001 or self.orientation >= math.pi/2 + 0.001:
                self.estado = "Alinhar_Vertical"

            #Se sair do ponto x = -0.7 (para o goleiro amarelo), reposicionar
            if self.x <= -0.69 - 0.01 or self.x >= -0.69 + 0.01: 
                self.estado = "Reposicionar"
            #verifica se o robô está fora do retangulo seguro
            '''if self.wall_collision():
                self.estado = "RE"''' #muda o estado


            #verifica se o robô chegou no objetivo
            #if self.arrived():
                #pass
                #self.estado = "ESPERA"
                #self.t0 = self.con.env.step #timer
                #self.con.sendOne(self.id, 0, 0)

        elif self.estado == "Alinhar_Vertical":
            erro = math.pi/2 - self.orientation #calculo do erro de alinhamento com a vertical se orientando para cima
            vr = abs(erro)*10 #calculo da velocidade de rotação proporcional ou tamanho do erro
        
            if self.orientation <= math.pi/2 - 0.001:
                self.con.sendOne(self.id,-vr,vr)
            elif self.orientation >= math.pi/2 + 0.001:
                self.con.sendOne(self.id,vr,-vr)
            else:
                self.con.sendOne(self.id,0,0)
                self.estado = "Alinhar_Bolinha"

        elif self.estado == "Reposicionar":
            self.AlignmentWithX()
            self.con.sendOne(self.id,self.ve,self.vd)
            
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
            self.estado = "Alinhar_Vertical"
            