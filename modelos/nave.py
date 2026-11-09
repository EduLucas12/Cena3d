# Modelo 1: NAVE ESPACIAL (tema 6)
# Composta apenas com geometrias do framework (cilindro, cone, caixa, elipsoide).
# A nave fica "em pé" no eixo +y; a escotilha/rampa fica na face +z local.
from math import pi, sin
from core.mesh import Mesh
from core.group import Group
from geometry.boxGeometry import BoxGeometry
from geometry.cylinderGeometry import CylinderGeometry
from geometry.cylindricalGeometry import CylindricalGeometry
from geometry.coneGeometry import ConeGeometry
from geometry.ellipsoidGeometry import EllipsoidGeometry
from material.phongMaterial import PhongMaterial
from material.surfaceMaterial import SurfaceMaterial

RAIO = 0.9                 # raio do corpo
ANGULO_RAMPA_ABERTA = 2.32  # ~133°: a ponta da rampa encosta no chão


class Nave(object):

    def __init__(self):
        # nó raiz: é ele que se desloca e gira durante a animação
        self.raiz = Group()

        # ---------- materiais (Phong: brilho especular de metal pintado) ----------
        branco = PhongMaterial(useShadow=True, properties={"baseColor": [0.93, 0.93, 0.95],
                                                           "shininess": 48})
        vermelho = PhongMaterial(useShadow=True, properties={"baseColor": [0.85, 0.15, 0.12],
                                                             "shininess": 48})
        azul = PhongMaterial(useShadow=True, properties={"baseColor": [0.15, 0.3, 0.75]})
        cinza = PhongMaterial(useShadow=True, properties={"baseColor": [0.3, 0.3, 0.33],
                                                          "specularStrength": 1.5})
        vidro = PhongMaterial(useShadow=True, properties={"baseColor": [0.35, 0.65, 0.9],
                                                          "shininess": 96, "specularStrength": 2})
        escuro = PhongMaterial(properties={"baseColor": [0.05, 0.05, 0.07]})

        # ---------- corpo principal ----------
        corpo = Mesh(CylinderGeometry(radius=RAIO, height=3.2, radialSegments=40), branco)
        corpo.setPosition([0, 2.2, 0])          # vai de y=0.6 até y=3.8
        self.raiz.add(corpo)

        faixa = Mesh(CylinderGeometry(radius=RAIO + 0.02, height=0.3, radialSegments=40), azul)
        faixa.setPosition([0, 3.3, 0])
        self.raiz.add(faixa)

        # bico (cone) e ponta
        bico = Mesh(ConeGeometry(radius=RAIO, height=1.7, radialSegments=40), vermelho)
        bico.setPosition([0, 3.8 + 0.85, 0])
        self.raiz.add(bico)

        # bocal do motor: tronco de cone (raio de cima menor que o de baixo)
        bocal = Mesh(CylindricalGeometry(radiusTop=0.45, radiusBottom=0.65, height=0.6,
                                         radialSegments=32), cinza)
        bocal.setPosition([0, 0.3, 0])
        self.raiz.add(bocal)

        # janela da cabine: elipsoide achatado encostado no corpo
        janela = Mesh(EllipsoidGeometry(width=0.75, height=0.6, depth=0.3), vidro)
        janela.setPosition([0, 3.0, RAIO - 0.05])
        self.raiz.add(janela)

        # ---------- 4 aletas ----------
        # cada aleta fica num Group girado em Y; a aleta em si é sempre
        # construída do mesmo jeito (apontando para +z) e o giro do grupo a distribui
        for i in range(4):
            suporte = Group()
            suporte.rotateY(pi / 4 + i * pi / 2)   # 45°, 135°, 225°, 315°
            self.raiz.add(suporte)
            aleta = Mesh(BoxGeometry(0.1, 1.5, 0.75), vermelho)
            aleta.setPosition([0, 1.05, RAIO + 0.3])
            suporte.add(aleta)
            # sapata de pouso na ponta da aleta
            sapata = Mesh(CylinderGeometry(radius=0.16, height=0.12), cinza)
            sapata.setPosition([0, 0.06, RAIO + 0.55])
            suporte.add(sapata)
            perna = Mesh(BoxGeometry(0.08, 0.35, 0.08), cinza)
            perna.setPosition([0, 0.25, RAIO + 0.55])
            suporte.add(perna)

        # ---------- escotilha + rampa articulada ----------
        # vão escuro da porta (aparece quando a rampa abre)
        vao = Mesh(BoxGeometry(0.72, 1.25, 0.05), escuro)
        vao.setPosition([0, 1.6, RAIO - 0.02])
        self.raiz.add(vao)
        # pivô na dobradiça (borda de baixo da porta)
        self.rampaPivo = Group()
        self.rampaPivo.setPosition([0, 0.95, RAIO + 0.03])
        self.raiz.add(self.rampaPivo)
        # fechada, a rampa fica em pé tampando o vão; abrir = girar o pivô em X
        rampa = Mesh(BoxGeometry(0.8, 1.4, 0.06), branco)
        rampa.setPosition([0, 0.7, 0])
        self.rampaPivo.add(rampa)
        listra = Mesh(BoxGeometry(0.5, 1.1, 0.065), azul)
        listra.setPosition([0, 0.7, 0])
        self.rampaPivo.add(listra)
        self.anguloRampa = 0.0

        # ---------- chama do motor ----------
        # SurfaceMaterial (sem iluminação): o fogo tem cor própria, não depende da luz
        self.chama = Group()
        self.chama.setPosition([0, 0.0, 0])
        self.raiz.add(self.chama)
        chamaExterna = Mesh(ConeGeometry(radius=0.55, height=1.8),
                            SurfaceMaterial({"baseColor": [1.0, 0.45, 0.08]}))
        chamaExterna.rotateX(pi)                  # cone de cabeça para baixo
        chamaExterna.setPosition([0, -0.9, 0])
        chamaInterna = Mesh(ConeGeometry(radius=0.32, height=1.2),
                            SurfaceMaterial({"baseColor": [1.0, 0.92, 0.45]}))
        chamaInterna.rotateX(pi)
        chamaInterna.setPosition([0, -0.6, 0])
        for m in (chamaExterna, chamaInterna):
            m.castShadow = False                  # fogo não projeta sombra
            self.chama.add(m)
        self.chamaExterna, self.chamaInterna = chamaExterna, chamaInterna
        self.setChama(0)

    # ------------------------------------------------------------------
    # Métodos usados pela animação
    # ------------------------------------------------------------------
    def setRampa(self, fracao):
        """0 = fechada, 1 = aberta. Gira o pivô só a diferença de ângulo."""
        alvo = fracao * ANGULO_RAMPA_ABERTA
        self.rampaPivo.rotateX(alvo - self.anguloRampa)
        self.anguloRampa = alvo

    def setChama(self, intensidade, tempo=0.0):
        """Escala a chama (0 = apagada). O 'sin' dá uma tremulação ao fogo."""
        if intensidade <= 0.001:
            self.chama.visible = False
            for m in (self.chamaExterna, self.chamaInterna):
                m.visible = False
            return
        for m in (self.chamaExterna, self.chamaInterna):
            m.visible = True
        tremor = 1.0 + 0.12 * sin(tempo * 40)
        s = intensidade * tremor
        # a matriz do grupo é refeita do zero: escala sem acumular
        pos = self.chama.getPosition()
        from core.matrix import Matrix
        self.chama.transform = Matrix.makeTranslation(*pos) @ Matrix.makeScale(s)
