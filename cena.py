# Trabalho Prático de Computação Gráfica - UNIPAC 2026/02
# Cena: base de lançamento. O astronauta sai da torre de comando,
# acena para o público, embarca na nave e ela decola.
# Framework: Stemkoski & Pascale (2022), "Developing Graphics Frameworks
# with Python and OpenGL" (adaptado).
from math import pi
from core.base import Base
from core.renderer import Renderer
from core.scene import Scene
from core.camera import Camera
from light.ambientLight import AmbientLight
from light.directionalLight import DirectionalLight
from extras.movementRig import MovementRig
from modelos.cenario import criarCenario
from modelos.nave import Nave

LARGURA, ALTURA = 1000, 700


class Cena(Base):

    def initialize(self):
        # cor de fundo parecida com o céu (só aparece se algo falhar)
        self.renderer = Renderer(clearColor=[0.05, 0.06, 0.15])
        self.scene = Scene()

        # ---------- câmera em perspectiva controlada pelo teclado ----------
        # angleOfView=60°, aspectRatio = largura/altura (evita imagem esticada)
        self.camera = Camera(angleOfView=60, aspectRatio=LARGURA / ALTURA, near=0.1, far=200)
        self.rig = MovementRig(unitsPerSecond=4, degreesPerSecond=45)
        self.rig.add(self.camera)
        self.rig.setPosition([0.0, 5.5, 21])
        self.rig.lookAttachment.rotateX(-0.2)   # olha levemente para baixo
        self.scene.add(self.rig)

        # ---------- luzes ----------
        # ambiente: clareia tudo um pouco (sem ela, o lado escuro fica preto)
        self.scene.add(AmbientLight(color=[0.32, 0.32, 0.38]))
        # direcional: o "sol" de fim de tarde, que também projeta as sombras
        self.sol = DirectionalLight(color=[0.95, 0.85, 0.72], direction=[-0.6, -1.0, -0.45])
        # a posição da luz direcional só importa para a câmera da sombra:
        # fica "atrás" da cena, na direção oposta à luz
        self.sol.setPosition([10, 17, 7.5])
        self.scene.add(self.sol)

        # ---------- ambiente ----------
        self.pecas = criarCenario(self.scene)

        # ---------- nave (modelo 1) ----------
        self.nave = Nave()
        self.nave.raiz.setPosition([0, 0.3, 0])     # em cima da plataforma
        # começa com a escotilha virada para +x (de costas para a torre);
        # na animação ela gira para "encontrar" o astronauta
        self.nave.raiz.rotateY(pi / 2)
        self.scene.add(self.nave.raiz)

        # ---------- sombras (shadow mapping, seção 6.9) ----------
        # cameraBounds = volume da câmera ortográfica da luz (esq, dir, baixo, cima, perto, longe)
        self.renderer.enableShadows(self.sol, strength=0.6, resolution=[2048, 2048],
                                    cameraBounds=[-15, 15, -15, 15, 0, 50], bias=0.0015)

    def update(self):
        self.rig.update(self.input, self.deltaTime)
        self.renderer.render(self.scene, self.camera)


if __name__ == "__main__":
    Cena(screenSize=[LARGURA, ALTURA], title="Base 6-19 - Nave e Astronauta").run()
