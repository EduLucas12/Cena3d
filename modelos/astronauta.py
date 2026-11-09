# Modelo 2: ASTRONAUTA ESTILIZADO (tema 19)
# Composto com caixas, esferas, elipsoides e cilindros do framework.
# O astronauta olha para +z local (lado do visor). Articulações = Groups.
from math import pi, sin
from core.mesh import Mesh
from core.group import Group
from core.matrix import Matrix
from geometry.boxGeometry import BoxGeometry
from geometry.sphereGeometry import SphereGeometry
from geometry.ellipsoidGeometry import EllipsoidGeometry
from geometry.cylinderGeometry import CylinderGeometry
from material.phongMaterial import PhongMaterial

ESCALA = 0.75          # o modelo é feito com ~1,55 de altura e reduzido para caber na escotilha
ALTURA_QUADRIL = 0.55


class Astronauta(object):

    def __init__(self):
        self.raiz = Group()
        # ESCALA uniforme no nó raiz: todos os filhos diminuem junto
        self.raiz.scale(ESCALA)

        # ---------- materiais ----------
        traje = PhongMaterial(useShadow=True, properties={"baseColor": [0.95, 0.95, 0.93],
                                                          "specularStrength": 0.4,
                                                          "shininess": 16})
        cinza = PhongMaterial(useShadow=True, properties={"baseColor": [0.55, 0.57, 0.6]})
        escuro = PhongMaterial(useShadow=True, properties={"baseColor": [0.22, 0.22, 0.25]})
        laranja = PhongMaterial(useShadow=True, properties={"baseColor": [1.0, 0.5, 0.1]})
        # visor dourado bem brilhante (reflexo especular forte)
        visor = PhongMaterial(useShadow=True, properties={"baseColor": [0.85, 0.6, 0.15],
                                                          "shininess": 128,
                                                          "specularStrength": 3})

        # ---------- tronco e cabeça (presos direto na raiz) ----------
        y0 = ALTURA_QUADRIL
        tronco = Mesh(BoxGeometry(0.5, 0.58, 0.32), traje)
        tronco.setPosition([0, y0 + 0.29, 0])
        self.raiz.add(tronco)
        cinto = Mesh(BoxGeometry(0.52, 0.08, 0.34), escuro)
        cinto.setPosition([0, y0 + 0.03, 0])
        self.raiz.add(cinto)
        mochila = Mesh(BoxGeometry(0.42, 0.5, 0.2), cinza)   # suporte de vida, nas costas (-z)
        mochila.setPosition([0, y0 + 0.33, -0.25])
        self.raiz.add(mochila)
        painel = Mesh(BoxGeometry(0.22, 0.14, 0.04), escuro)  # painel de controle no peito
        painel.setPosition([0, y0 + 0.36, 0.17])
        self.raiz.add(painel)
        for i, cor in enumerate([[0.9, 0.1, 0.1], [0.1, 0.8, 0.2], [0.1, 0.4, 0.95]]):
            botao = Mesh(SphereGeometry(0.022, 8, 6),
                         PhongMaterial(properties={"baseColor": cor}))
            botao.setPosition([-0.06 + 0.06 * i, y0 + 0.36, 0.195])
            self.raiz.add(botao)
        bandeira = Mesh(BoxGeometry(0.1, 0.06, 0.02), laranja)  # emblema no ombro
        bandeira.setPosition([0.2, y0 + 0.5, 0.165])
        self.raiz.add(bandeira)

        pescoco = Mesh(CylinderGeometry(radius=0.12, height=0.08), cinza)
        pescoco.setPosition([0, y0 + 0.62, 0])
        self.raiz.add(pescoco)
        capacete = Mesh(SphereGeometry(0.25, 32, 16), traje)
        capacete.setPosition([0, y0 + 0.86, 0])
        self.raiz.add(capacete)
        rosto = Mesh(EllipsoidGeometry(width=0.36, height=0.27, depth=0.2), visor)
        rosto.setPosition([0, y0 + 0.87, 0.16])
        self.raiz.add(rosto)

        # ---------- braços: ombro (Group) -> braço -> cotovelo (Group) -> antebraço -> luva ----------
        self.ombro = {}
        self.cotovelo = {}
        for lado, sx in (("D", 1), ("E", -1)):        # D = direito (+x), E = esquerdo (-x)
            ombro = Group()
            self.raiz.add(ombro)
            ombreira = Mesh(SphereGeometry(0.1, 16, 8), traje)
            ombro.add(ombreira)
            braco = Mesh(BoxGeometry(0.13, 0.26, 0.14), traje)
            braco.setPosition([0, -0.14, 0])
            ombro.add(braco)
            cotovelo = Group()
            ombro.add(cotovelo)
            antebraco = Mesh(BoxGeometry(0.12, 0.24, 0.13), traje)
            antebraco.setPosition([0, -0.12, 0])
            cotovelo.add(antebraco)
            punho = Mesh(CylinderGeometry(radius=0.075, height=0.04), laranja)
            punho.setPosition([0, -0.25, 0])
            cotovelo.add(punho)
            luva = Mesh(SphereGeometry(0.075, 12, 8), cinza)
            luva.setPosition([0, -0.31, 0])
            cotovelo.add(luva)
            self.ombro[lado] = ombro
            self.cotovelo[lado] = cotovelo
        # posição fixa das articulações (a rotação é aplicada por cima)
        self.posOmbro = {"D": [0.31, y0 + 0.5, 0], "E": [-0.31, y0 + 0.5, 0]}
        self.posCotovelo = [0, -0.28, 0]

        # ---------- pernas: quadril (Group) -> perna -> bota ----------
        self.quadril = {}
        for lado, sx in (("D", 1), ("E", -1)):
            quadril = Group()
            self.raiz.add(quadril)
            perna = Mesh(BoxGeometry(0.18, 0.44, 0.2), traje)
            perna.setPosition([0, -0.22, 0])
            quadril.add(perna)
            joelheira = Mesh(BoxGeometry(0.19, 0.06, 0.21), cinza)
            joelheira.setPosition([0, -0.26, 0.005])
            quadril.add(joelheira)
            bota = Mesh(BoxGeometry(0.2, 0.12, 0.3), escuro)
            bota.setPosition([0, -0.49, 0.04])
            quadril.add(bota)
            self.quadril[lado] = quadril
        self.posQuadril = {"D": [0.13, y0, 0], "E": [-0.13, y0, 0]}

        self.posePadrao()

    # ------------------------------------------------------------------
    # Pose: a matriz de cada articulação é REFEITA a cada quadro:
    #   M = Translação(posição da junta) @ RotaçãoX(frente/trás) @ RotaçãoZ(para o lado)
    # Assim os ângulos não acumulam e a pose depende só do tempo.
    # ------------------------------------------------------------------
    @staticmethod
    def _junta(grupo, pos, rx=0.0, rz=0.0):
        grupo.transform = (Matrix.makeTranslation(*pos)
                           @ Matrix.makeRotationX(rx) @ Matrix.makeRotationZ(rz))

    def setPose(self, ombroD=(0, 0), cotoveloD=(0, 0), ombroE=(0, 0), cotoveloE=(0, 0),
                quadrilD=0, quadrilE=0):
        """Cada braço recebe (rx, rz) em radianos; cada perna, só rx."""
        self._junta(self.ombro["D"], self.posOmbro["D"], *ombroD)
        self._junta(self.cotovelo["D"], self.posCotovelo, *cotoveloD)
        self._junta(self.ombro["E"], self.posOmbro["E"], *ombroE)
        self._junta(self.cotovelo["E"], self.posCotovelo, *cotoveloE)
        self._junta(self.quadril["D"], self.posQuadril["D"], quadrilD)
        self._junta(self.quadril["E"], self.posQuadril["E"], quadrilE)

    def posePadrao(self):
        # braços levemente abertos (traje volumoso)
        self.setPose(ombroD=(0, 0.12), ombroE=(0, -0.12))

    def poseAndando(self, t):
        """Ciclo de caminhada: pernas e braços balançam em oposição (seno do tempo)."""
        a = 0.45 * sin(t * 7)
        self.setPose(ombroD=(-a * 0.8, 0.12), cotoveloD=(-0.3, 0),
                     ombroE=(a * 0.8, -0.12), cotoveloE=(-0.3, 0),
                     quadrilD=a, quadrilE=-a)

    def poseAceno(self, t, levantar=1.0):
        """Braço direito levantado pelo ombro (rotação em Z) e o cotovelo
        balançando de um lado para o outro = 'tchau'.
        levantar: 0..1 (permite subir/descer o braço suavemente)."""
        ombroZ = 0.12 + levantar * 2.5             # ~150° com o braço todo erguido
        balanco = levantar * 0.5 * sin(t * 9)      # vai e volta do antebraço
        self.setPose(ombroD=(0, ombroZ), cotoveloD=(0, 0.3 + balanco),
                     ombroE=(0, -0.12))

    def poseSinal(self, levantar=1.0):
        """Sinal para a nave: braço direito esticado à frente, apontando (resposta)."""
        self.setPose(ombroD=(-levantar * 1.45, 0.05), cotoveloD=(0, 0),
                     ombroE=(0, -0.12))
