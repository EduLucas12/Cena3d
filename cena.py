# Trabalho Prático de Computação Gráfica - UNIPAC 2026/02
# Cena: base de lançamento. O astronauta sai da torre de comando,
# acena para o público, a nave gira para encontrá-lo, ele embarca e ela decola.
# Framework: Stemkoski & Pascale (2022), "Developing Graphics Frameworks
# with Python and OpenGL" (adaptado).
#
# Controles:  W A S D andar | R F subir/descer | Q E girar | T G olhar cima/baixo
#             P pausar/continuar | C câmera livre/automática | Enter reiniciar
from math import pi
import pygame
from core.base import Base
from core.renderer import Renderer
from core.scene import Scene
from core.camera import Camera
from light.ambientLight import AmbientLight
from light.directionalLight import DirectionalLight
from light.pointLight import PointLight
from extras.movementRig import MovementRig
from modelos.cenario import criarCenario
from modelos.nave import Nave
from modelos.astronauta import Astronauta
from animacao import Sequencia

LARGURA, ALTURA = 1000, 700
TITULO = "Base 6-19 - Nave e Astronauta"


class Cena(Base):

    def initialize(self):
        # cor de fundo parecida com o céu (só aparece se algo falhar)
        self.renderer = Renderer(clearColor=[0.05, 0.06, 0.15])
        self.scene = Scene()

        # ---------- câmera livre: perspectiva controlada pelo teclado ----------
        # angleOfView=60°, aspectRatio = largura/altura (evita imagem esticada)
        self.camera = Camera(angleOfView=60, aspectRatio=LARGURA / ALTURA, near=0.1, far=200)
        self.rig = MovementRig(unitsPerSecond=4, degreesPerSecond=45)
        self.rig.add(self.camera)
        self.rig.setPosition([-1.5, 4.0, 14.5])
        self.rig.lookAttachment.rotateX(-0.1)    # olha levemente para baixo
        self.scene.add(self.rig)

        # ---------- câmera automática: parada num ponto, "segue" a ação com lookAt ----------
        self.cameraAuto = Camera(angleOfView=50, aspectRatio=LARGURA / ALTURA, near=0.1, far=200)
        self.cameraAuto.setPosition([0.5, 2.0, 11.5])
        self.scene.add(self.cameraAuto)
        self.usarCameraAuto = False

        # ---------- luzes ----------
        # ambiente: clareia tudo um pouco (sem ela, o lado escuro fica preto)
        self.scene.add(AmbientLight(color=[0.32, 0.32, 0.38]))
        # direcional: o "sol" de fim de tarde, que também projeta as sombras
        self.sol = DirectionalLight(color=[0.95, 0.85, 0.72], direction=[-0.6, -1.0, -0.45])
        # a posição da luz direcional só importa para a câmera da sombra:
        # fica "atrás" da cena, na direção oposta à luz
        self.sol.setPosition([10, 17, 7.5])
        self.scene.add(self.sol)
        # pontual: brilho alaranjado do motor (apagada até a ignição)
        self.luzMotor = PointLight(color=[0, 0, 0], position=[0, 0, 0], attenuation=[1, 0, 0.12])
        self.scene.add(self.luzMotor)

        # ---------- ambiente ----------
        self.pecas = criarCenario(self.scene)

        # ---------- nave (modelo 1) ----------
        self.nave = Nave()
        self.scene.add(self.nave.raiz)

        # ---------- astronauta (modelo 2) ----------
        self.astronauta = Astronauta()
        self.scene.add(self.astronauta.raiz)

        # ---------- sombras (shadow mapping, seção 6.9) ----------
        # cameraBounds = volume da câmera ortográfica da luz (esq, dir, baixo, cima, perto, longe)
        self.renderer.enableShadows(self.sol, strength=0.6, resolution=[2048, 2048],
                                    cameraBounds=[-15, 15, -15, 15, 0, 50], bias=0.0015)

        # ---------- animação ----------
        # tempo da animação: separado de self.time para poder pausar
        self.tAnim = 0.0
        self.pausado = False
        self.sequencia = Sequencia(self)
        self.sequencia.aplicar(self.tAnim)
        self.legenda = ""

    def update(self):
        # ----- teclas de controle (eventos discretos: isKeyDown) -----
        if self.input.isKeyDown("p"):
            self.pausado = not self.pausado
        if self.input.isKeyDown("c"):
            self.usarCameraAuto = not self.usarCameraAuto
        if self.input.isKeyDown("return"):
            self.tAnim = 0.0

        # ----- avança o relógio da animação só se não estiver pausado -----
        if not self.pausado:
            self.tAnim += self.deltaTime
        self.sequencia.aplicar(self.tAnim)

        # ----- câmeras (continuam funcionando mesmo pausado) -----
        self.rig.update(self.input, self.deltaTime)
        if self.usarCameraAuto:
            self.cameraAuto.lookAt(self.alvoCameraAuto())
            cameraAtiva = self.cameraAuto
        else:
            cameraAtiva = self.camera

        # ----- título da janela mostra a fase atual -----
        legenda = (f"{TITULO}  |  {self.sequencia.faseAtual}  |  t = {self.tAnim:4.1f} s"
                   + ("  |  PAUSADO" if self.pausado else "")
                   + ("  |  camera automatica" if self.usarCameraAuto else ""))
        if legenda != self.legenda:
            pygame.display.set_caption(legenda)
            self.legenda = legenda

        self.renderer.render(self.scene, cameraAtiva)

    def alvoCameraAuto(self):
        """Olha para o astronauta até ele embarcar; depois passa a seguir a nave."""
        pa = self.astronauta.raiz.getWorldPosition()
        pn = self.nave.raiz.getWorldPosition()
        alvoA = [pa[0], pa[1] + 0.8, pa[2]]
        alvoN = [pn[0], pn[1] + 2.5, pn[2]]
        k = min(1.0, max(0.0, (self.tAnim - 26.5) / 2.0))   # transição suave de 2 s
        return [alvoA[i] + (alvoN[i] - alvoA[i]) * k for i in range(3)]


if __name__ == "__main__":
    Cena(screenSize=[LARGURA, ALTURA], title=TITULO).run()
