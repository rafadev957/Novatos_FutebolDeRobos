import math, sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'pb'))
from pb import vssref_common_pb2
class Goalkeeper:

    def __init__(self): #atributos do robô
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
        self.referee = None #JUIZ


    def setCommunication(self, con, referee): #comunicação do simulador e o código (robô)
        self.con = con
        self.referee = referee


    def setObj(self, x, y): #cria o objetivo do robô sendo a bola a partir dos eixos X e Y do robô
        self.xobj = x
        self.yobj = y


    def setPose(self, x, y, orientation): #cria a pose do robô (seu X, Y e Orientação) a partir da comunicação
        self.x = x
        self.y = y
        self.orientation = orientation


    #LÓGICAS DO ROBÔ A BAIXO:

    def collision(self): #colisão com parede
        #tamanho do campo - margem = perigo
        margem_segura = 0.1 #margem segura
        #MUDAR OS X E Y DO RETÂNGULO PARA O GOLEIRO
        if (self.x <= (0.60 - margem_segura) and self.x >= (-0.80 + margem_segura)) and (self.y <= (0.2 - margem_segura) and self.y >= (-0.2 + margem_segura)):
            self.contador_re = 0
            return False

        else:
            self.contador_re += 1
            print("contador para perigo: {}".format(self.teste)) #debuger
            #loop para ele não dar ré só por passar na margem
            if self.contador_re >= 45:
                self.contador_re = 0
                #print("PERIGO \n"*5) #debuger
                return True
    

    def arrived(self): #distância do objetivo e o robô
        d = math.sqrt((self.con.frame.ball.x - self.x)**2 + (self.con.frame.ball.y - self.y)**2)
        #print("distância do robô ao obj: {:.4f}".format(d))
        return d < 0.07 #retorna a distância quando for menor que 0.09


    def AlignmentWithBall(self):
        #velocidade base do goleiro
        self.vb = abs(self.yobj - self.y)*60 + 50*abs(self.xobj)/0.75 #Calculo da velocidade para alinhar com a bolinha (não sei se é a melhor forma de calcular a correção)
        #print(self.vb)
        if self.xobj < 0: #Para o goleiro amarelo: se a bola estiver no campo de defesa se alinha com a bolinha, se não centraliza
            #quando a bolinha esta dentro das linhas da trave
            if self.yobj<= 0.19 and self.yobj >= -0.19:
                if self.y + 0.02 <= self.yobj and self.y - 0.02 <= self.yobj:
                    self.vd = self.vb
                    self.ve = self.vb
                elif self.y + 0.02 >= self.yobj and self.y - 0.02 >= self.yobj: 
                    self.vd = -self.vb
                    self.ve = -self.vb
                else:
                    self.vd = 0
                    self.ve = 0
            #quando esta acima das traves
            elif self.yobj > 0.19:
                if self.y + 0.02 < 0.19 and self.y - 0.02 < 0.19:
                    self.vd = self.vb
                    self.ve = self.vb
                else:
                    self.vd = 0
                    self.ve = 0
            #quando esta abaixo das traves
            elif self.yobj < -0.19:
                if self.y + 0.02 > -0.19 and self.y - 0.02 > -0.19:
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
            self.ve = 30
            self.vd = 30
        if d <= 0.01:
            self.estado = "ALINHAR_VERTICAL"
        

    def update(self): #estados do goleiro
        foul = self.referee.foul 
        if foul != vssref_common_pb2.GAME_ON:
            self.estado = "ESPERA_RECOMECO"


        elif self.estado == "ALINHAR_BOLINHA":
            self.AlignmentWithBall()
            self.PositionCheck()
            self.con.sendOne(self.id, self.ve, self.vd)
            if self.arrived():
                self.con.sendOne(self.id, 0, 0)
                self.estado = "CHUTAR"

            #Se perder o alinhamento com a vertical, realinhar com a vertical orientando apra cima
            if self.orientation <= math.pi/2 - 0.001 or self.orientation >= math.pi/2 + 0.001:
                self.estado = "ALINHAR_VERTICAL"

            #Se sair do ponto x = -0.69 (para o goleiro amarelo), reposicionar
            if self.x <= -0.69 - 0.01 or self.x >= -0.69 + 0.01: 
                self.estado = "REPOSICIONAR"
            #verifica se o robô está fora do retangulo seguro
            '''if self.collision():
                self.estado = "RE"''' #muda o estado


        elif self.estado == "ALINHAR_VERTICAL":
            erro = math.pi/2 - self.orientation #calculo do erro de alinhamento com a vertical se orientando para cima
            vr = abs(erro)*10 #calculo da velocidade de rotação proporcional ou tamanho do erro
        
            if self.orientation <= math.pi/2 - 0.001:
                self.con.sendOne(self.id,-vr,vr)
            elif self.orientation >= math.pi/2 + 0.001:
                self.con.sendOne(self.id,vr,-vr)
            else:
                self.con.sendOne(self.id,0,0)
                self.estado = "ALINHAR_BOLINHA"


        elif self.estado == "REPOSICIONAR":
            self.AlignmentWithX()
            self.con.sendOne(self.id,self.ve,self.vd)
        
        
        elif self.estado == "CHUTAR":
            #Se o robo estiver na parte superior do campo chuta rodando no sentido anti-horario
            if self.y >= 0:
                self.con.sendOne(self.id,-self.vb,self.vb)
            #Se o robo estiver na parte inferior do campo chuta rodando no sentido horario
            elif self.y < 0:
                self.con.sendOne(self.id,self.vb,-self.vb)
            d = math.sqrt((self.xobj - self.x)**2 +(self.yobj - self.y)**2)
            if d >= 0.2:
                self.estado = "ALINHAR_BOLINHA"

        elif self.estado == "RE":
            #print("dando ré") #debuger da ré
            self.con.sendOne(self.id, -30, -30)
            self.passos += 1
            if self.passos >= 10: #conta x passos para trás
                self.passos = 0 #reseta os passos
                self.estado = "IR_ATE" #troca de estado

        elif self.estado == "PARADO":
            self.estado = "ALINHAR_VERTICAL"
        
        if self.estado == "ESPERA_RECOMECO":
            self.con.sendOne(self.id,0,0)
            if foul == vssref_common_pb2.GAME_ON:
                self.estado = "REPOSICIONAR"
            