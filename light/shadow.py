# Fonte: Stemkoski & Pascale (2022), seção 6.9.2
from core.camera import Camera
from core.renderTarget import RenderTarget
from material.depthMaterial import DepthMaterial
from OpenGL.GL import *


class Shadow(object):
    """Tudo que o shadow mapping precisa: a luz direcional, uma câmera
    ortográfica presa nela, o render target (mapa de profundidade)
    e o material de profundidade."""

    def __init__(self, lightSource, strength=0.5, resolution=[512, 512],
                 cameraBounds=[-5, 5, -5, 5, 0, 20], bias=0.01):
        super().__init__()
        self.lightSource = lightSource
        # câmera da sombra: ortográfica, porque os raios de luz são paralelos
        self.camera = Camera()
        left, right, bottom, top, near, far = cameraBounds
        self.camera.setOrthographic(left, right, bottom, top, near, far)
        self.lightSource.add(self.camera)
        # CLAMP_TO_BORDER: fora do mapa lê a borda branca = sem sombra
        # ADAPTAÇÃO: floatPrecision=True -> profundidade em 32 bits (ver renderTarget.py)
        self.renderTarget = RenderTarget(resolution, properties={"wrap": GL_CLAMP_TO_BORDER},
                                         floatPrecision=True)
        self.material = DepthMaterial()
        self.strength = strength
        self.bias = bias

    def updateInternal(self):
        self.camera.updateViewMatrix()
        self.material.uniforms["viewMatrix"].data = self.camera.viewMatrix
        self.material.uniforms["projectionMatrix"].data = self.camera.projectionMatrix
