from attacker import Attacker
from defender import Defender
from goalkeeper import Goalkeeper

class WorldModel:

    def __init__(self):
        # Composição ... Uma classe (WorldModel) mantém a referência de outras (Attacker, Deffender)
        # de modo que a inexistência do (WorldModel) arraceta a inexistência das outras classes.
        # Na classe Pai, o filhos (componentes) são instanciados.
        self.r0 = Attacker(0, 40) #id, vb
        self.r1 = Defender(1, 40)
        self.r2 = Goalkeeper(2, 40)
    
    # Associação simples (eu passo uma classe por parâmetro para outra, mas não tenho referências internas à ela)
    def setCommunicationAndReferee(self, con, ref):
        self.r0.setCommunication(con, ref)
        self.r1.setCommunication(con, ref)
        self.r2.setCommunication(con, ref)
    
    def update(self):
        # Atualiza o estado do mundo (percepções)
        self.r0.updatePose()
        self.r1.updatePose()
        self.r2.updatePose()
        # Toma as decisões.
        self.r0.update()
        self.r1.update()
        self.r2.update()