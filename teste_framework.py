# Teste da etapa 1: confere se o framework funciona (luz, textura e sombra).
# Baseado no test-6-5.py do livro (seção 6.9.2).
import pygame
from core.base import Base
from core.renderer import Renderer
from core.scene import Scene
from core.camera import Camera
from core.mesh import Mesh
from core.texture import Texture
from light.ambientLight import AmbientLight
from light.directionalLight import DirectionalLight
from material.phongMaterial import PhongMaterial
from geometry.rectangleGeometry import RectangleGeometry
from geometry.sphereGeometry import SphereGeometry
from geometry.boxGeometry import BoxGeometry
from geometry.coneGeometry import ConeGeometry
from extras.movementRig import MovementRig


class Teste(Base):
    def initialize(self):
        self.renderer = Renderer([0.2, 0.2, 0.2])
        self.scene = Scene()
        self.camera = Camera(aspectRatio=800 / 600)
        self.rig = MovementRig()
        self.rig.add(self.camera)
        self.rig.setPosition([0, 2, 6])
        self.scene.add(self.rig)

        self.scene.add(AmbientLight(color=[0.2, 0.2, 0.2]))
        self.dirLight = DirectionalLight(direction=[-1, -1, -0.5])
        self.dirLight.setPosition([3, 6, 1.5])
        self.scene.add(self.dirLight)

        # textura xadrez criada em memória (só para o teste)
        surf = pygame.Surface((64, 64))
        for i in range(8):
            for j in range(8):
                cor = (230, 230, 230) if (i + j) % 2 == 0 else (60, 60, 60)
                surf.fill(cor, (i * 8, j * 8, 8, 8))
        xadrez = Texture()
        xadrez.surface = surf
        xadrez.uploadData()

        chao = Mesh(RectangleGeometry(20, 20),
                    PhongMaterial(texture=xadrez, useShadow=True,
                                  properties={"repeatUV": [5, 5]}))
        chao.rotateX(-3.14159 / 2)
        self.scene.add(chao)

        self.esfera = Mesh(SphereGeometry(0.8),
                           PhongMaterial(useShadow=True, properties={"baseColor": [0.3, 0.5, 1.0]}))
        self.esfera.setPosition([-1.5, 1.2, 0])
        self.scene.add(self.esfera)
        caixa = Mesh(BoxGeometry(), PhongMaterial(useShadow=True, properties={"baseColor": [1, 0.5, 0.3]}))
        caixa.setPosition([1.5, 0.5, 0])
        self.scene.add(caixa)
        cone = Mesh(ConeGeometry(0.5, 1.5), PhongMaterial(useShadow=True))
        cone.setPosition([0, 0.75, -1.5])
        self.scene.add(cone)

        self.renderer.enableShadows(self.dirLight, resolution=[1024, 1024])

    def update(self):
        # a esfera sobe e desce (movimento baseado em tempo) -> sombra acompanha
        from math import sin
        self.esfera.setPosition([-1.5, 1.2 + 0.6 * sin(2 * self.time), 0])
        self.rig.update(self.input, self.deltaTime)
        self.renderer.render(self.scene, self.camera)


Teste(screenSize=[800, 600], title="Teste do framework").run()
