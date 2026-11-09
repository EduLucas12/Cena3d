# Fonte: Stemkoski & Pascale (2022), seção 5.8
from OpenGL.GL import *
import pygame
from core.texture import Texture


class RenderTarget(object):
    """Framebuffer próprio: em vez de desenhar na janela, desenha numa textura.
    É usado na passada de sombra (o mapa de profundidade)."""

    def __init__(self, resolution=[512, 512], texture=None, properties={}, floatPrecision=False):
        self.width, self.height = resolution
        if texture is not None:
            self.texture = texture
        else:
            self.texture = Texture(None, {
                "magFilter": GL_LINEAR,
                "minFilter": GL_LINEAR,
                "wrap": GL_CLAMP_TO_EDGE
            })
            self.texture.setProperties(properties)
            self.texture.surface = pygame.Surface(resolution)
            self.texture.uploadData()
            # ADAPTAÇÃO: textura de ponto flutuante (32 bits por pixel) em vez de 8 bits.
            # Usada no mapa de sombra: com 8 bits a profundidade só tem 256 níveis
            # e aparecem listras ("shadow acne") nas superfícies curvas.
            if floatPrecision:
                glBindTexture(GL_TEXTURE_2D, self.texture.textureRef)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_R32F, self.width, self.height, 0,
                             GL_RED, GL_FLOAT, None)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        # cria o framebuffer
        self.framebufferRef = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebufferRef)
        # buffer de cor = a textura
        glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, self.texture.textureRef, 0)
        # buffer de profundidade = renderbuffer
        depthBufferRef = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, depthBufferRef)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, self.width, self.height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depthBufferRef)
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise Exception("Framebuffer status error")
        # ADAPTAÇÃO: volta para o framebuffer da janela
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
