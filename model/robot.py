class Robot:

    def __init__(self):
        self.id = 0 #identidade padrão
        self.x = 0 #eixo X do robô
        self.y = 0 #eixo Y do robô
        self.orientation = 0 #orientação (radianos)
        self.ve = 0 #velocidade roda esquerda
        self.vd = 0 #velocidade roda direita
        self.estado = "PARADO" #estado padrão do robô ao iniciar o jogo