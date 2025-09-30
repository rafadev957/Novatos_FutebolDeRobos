import math, sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'pb'))
from pb import vssref_common_pb2
class Defender:

    def __init__(self): #atributos do robô
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
        self.kp = 10 #ajuste do erro (controlador)
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

    def arrived(self): #distância do objetivo e o robô
        """
        IDEIA: O DEFENSOR SEGUE A BOLA NO EIXO Y, SE ELA PASSA O MEIO DO CAMPO SÓ O DEFENSOR ATUA
        """
        d = math.sqrt((self.con.frame.ball.x - self.x)**2 + (self.con.frame.ball.y - self.y)**2)
        #print("distância do robô ao obj: {:.4f}".format(d))
        return d < 0.07 #retorna a distância quando for menor que 0.09


    def collision(self): #colisão com parede
        #tamanho do campo - margem = perigo
        margem_segura = 0.1 #não para nas quinas, variável local
        # 0 > x >= x_ponto
        if (self.x < (0 - margem_segura) and self.x >= (-0.37 + margem_segura)) and (self.y <= (0.65 - margem_segura) and self.y >= (-0.65 + margem_segura)):
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


    def CalculateError(self,Flag,x_obj,y_obj): #Se Flag == True calcula o erro em relação a orientação dianteira, else calcula da traseira
        angulo_ro = math.atan2(y_obj - self.y, x_obj - self.x)
        #Correção em relação ao pi e -pi 
        if Flag == True:
            erro = angulo_ro - self.orientation
            if math.fabs(erro) > math.pi:
                if self.orientation < 0:
                    self.orientation = 2*math.pi + self.orientation
                if angulo_ro < 0:
                    angulo_ro = 2*math.pi + angulo_ro
                erro = angulo_ro - self.orientation
            return erro
        else:
            self.orientation = -(math.pi-self.orientation)
            erro = self.orientation - angulo_ro 
            if math.fabs(erro) > math.pi:
                if self.orientation < 0:
                    self.orientation = 2*math.pi + self.orientation
                if angulo_ro < 0:
                    angulo_ro = 2*math.pi + angulo_ro
                erro = self.orientation - angulo_ro
            return erro


    def AlignmentWithX(self): #Se perder o alinhamento com x determinado (-0.37)
        x_ponto = -0.37
        y_ponto = self.y
        d = math.sqrt((x_ponto - self.x)**2 +(y_ponto - self.y)**2) #distância do robô ao ponto (-0.37,0)
        angulo_ro = math.atan2(y_ponto - self.y, x_ponto - self.x) #ângulo de erro em relação ao ponto (-0.37,0)
        erro = self.CalculateError(True,-0.37,self.y)
        ce = cd = 0
        cr = self.kp*abs(erro) #Correção das velocidades proporcional ao erro
        if erro < 0 - 0.05:
            self.ve = cr 
            self.vd = -cr
        elif erro > 0 + 0.05:
            self.ve = -cr
            self.vd = cr
        else: #Se estiver alinhado anda reto
            self.ve = 20+40*(self.x-x_ponto )
            self.vd = 20+40*(self.x-x_ponto )
        if d <= 0.03:
            self.ve = 0
            self.vd = 0
            self.estado = "ALINHAR_VERTICAL"


    def AlignmentWithBall(self):
        self.yobj = self.con.frame.ball.y #definindo o y do objetivo como o y da bolinha
        d = self.yobj - self.y #calculando a distância entre o y da bolinha e o y do robo
        vr = self.kp*abs(d)
        if self.yobj > self.y + 0.02 and self.yobj > self.y - 0.02:
            self.ve = self.vb 
            self.vd = self.vb 
        elif self.yobj < self.y + 0.02 and self.yobj < self.y - 0.02:
            self.ve = -self.vb 
            self.vd = -self.vb 
        else:
            self.ve = 0
            self.vd = 0


    def controladorP(self): #controlador da direção do robô, calcula o "erro" de ângulação entre o robô e a bola
        #Calculo de erro em relação a orientação dianteira
        erro1 = self.CalculateError(True,self.xobj,self.yobj)

        #Calculo de erro em relação a orientação traseira
        erro2 = self.CalculateError(False,self.xobj,self.yobj)

        #Calculo da diferença entre os erros
        dif_erros = abs(erro1)-abs(erro2)

        #Se a orientação dianteira estiver mais perto da bolinha, anda de frente atrás da bola
        if abs(erro1) < abs(erro2) and abs(dif_erros) >= 0.2:
            ce = cd = 0
            cr = self.kp*math.fabs(erro1)
            if erro1 > 0:
                ce = -cr
                cd = cr
            elif erro1 < 0:
                ce = cr
                cd = -cr
            self.ve = self.vb + ce
            self.vd = self.vb + cd
        
        #Se a orientação traseira estiver mais perto da bolinha, anda de costas atrás da bola
        elif abs(erro1) > abs(erro2) and abs(dif_erros) >= 0.2:   
            ce = cd = 0
            cr = self.kp*math.fabs(erro2)
            if erro2 > 0:
                ce = cr
                cd = -cr
            elif erro2 < 0:
                ce = -cr
                cd = cr
            self.ve = -self.vb + ce
            self.vd = -self.vb + cd
        
        else:
            if dif_erros <= 0:
                #SE a bolinha estiver na mesma linha do robo com baixa diferença entre os erros gire para tomar uma decisão
                self.ve = 7
                self.vd = -7 #Valor 7 definido a partir de testes PROVAVELMENTE tem forma melhor de fazer isso
            else:
                self.ve = -7
                self.vd = 7


    def update(self): #estados do defensor
        foul = self.referee.foul 
        if foul != vssref_common_pb2.GAME_ON:
            self.estado = "ESPERA_RECOMECO"
        
        #Se a bolinha estiver fora da área de atuação do defensor faça: 
        elif self.xobj >= 0 or self.xobj < -0.375: 
            if self.estado == "ALINHAR":
                self.AlignmentWithX()
                self.con.sendOne(self.id, self.ve, self.vd,False)  

            elif self.estado == "ALINHAR_VERTICAL":
                erro = math.pi/2 - self.orientation #calculo do erro de alinhamento com a vertical se orientando para cima
                vr = abs(erro)*10 #calculo da velocidade de rotação proporcional ou tamanho do erro
                if self.orientation <= math.pi/2 - 0.001:
                    self.con.sendOne(self.id,-vr,vr,False)
                elif self.orientation >= math.pi/2 + 0.001:
                    self.con.sendOne(self.id,vr,-vr,False)
                else:
                    self.con.sendOne(self.id,0,0,False)
                    self.estado = "ALINHAR_BOLINHA"
                
            elif self.estado == "ALINHAR_BOLINHA":
                #Para evitar com que o robô trave no estado de alinhar a bolinha fora do local determinado
                if self.xobj > -0.375 and self.x < -0.35 and self.x > -0.39: 
                    self.AlignmentWithBall()
                    self.con.sendOne(self.id, self.ve, self.vd,False) 
                else:
                    self.estado ="ALINHAR"
                 
        #Se a bolinha passar para o campo defensivo/de atuação do defensor faça:   
        else:
            self.estado = "ALINHAR"
            self.controladorP()
            self.con.sendOne(self.id, self.ve, self.vd,False)  
        
        #verifica se o robô está fora do retangulo seguro
        """if self.collision():
            self.estado = "RE" #muda o estado
            """

        #verifica se o robô chegou no objetivo
        if self.arrived() and self.estado != "CHUTAR":
            self.con.sendOne(self.id, 0, 0,False)
            self.estado = "CHUTAR"

        elif self.estado == "RE":
            #print("dando ré") #debuger da ré
            self.con.sendOne(self.id, -30, -30,False)
            self.passos += 1
            if self.passos >= 10: #conta x passos para trás
                self.passos = 0 #reseta os passos
                self.estado = "ALINHAR" #troca de estado

        elif self.estado == "CHUTAR":
            #Se o robo estiver na parte superior do campo chuta rodando no sentido anti-horario
            if self.y >= 0:
                self.con.sendOne(self.id,-self.vb,self.vb,False)
            #Se o robo estiver na parte inferior do campo chuta rodando no sentido horario
            elif self.y < 0:
                self.con.sendOne(self.id,self.vb,-self.vb,False)
            d = math.sqrt((self.xobj - self.x)**2 +(self.yobj - self.y)**2)
            if d >= 0.15:
                self.estado = "ALINHAR"

        elif self.estado == "ESPERA_RECOMECO":
            self.con.sendOne(self.id,0,0,False)
            if foul == vssref_common_pb2.GAME_ON:
                self.estado = "ALINHAR"

        if self.estado == "PARADO":
            self.estado = "ALINHAR"