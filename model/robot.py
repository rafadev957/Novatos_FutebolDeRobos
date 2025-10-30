class Robot:

    def __init__(self, id, vb):
        self.id = id #identidade padrão
        self.x = 0 #eixo X do robô
        self.y = 0 #eixo Y do robô
        self.orientation = 0 #orientação (radianos)
        self.ve = 0 #velocidade roda esquerda
        self.vd = 0 #velocidade roda direita
        self.vb = vb
        self.estado = "PARADO" #estado padrão do robô ao iniciar o jogo
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
    
    def updatePose(self):
        if len(self.con.frame.robots_yellow) > 0:
            myself = self.con.frame.robots_yellow[self.id]
            self.setPose(myself.x, myself.y, myself.orientation)
