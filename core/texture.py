# Fonte: Stemkoski & Pascale (2022), seção 5.1
import pygame
from OpenGL.GL import *


class Texture(object):
    """Carrega uma imagem com o Pygame e envia os pixels para a GPU."""

    def __init__(self, fileName=None, properties={}):
        # superfície do pygame que guarda os pixels
        self.surface = None
        self.textureRef = glGenTextures(1)
        # filtros e modo de repetição padrão
        self.properties = {
            "magFilter": GL_LINEAR,                # ampliação: bilinear
            "minFilter": GL_LINEAR_MIPMAP_LINEAR,  # redução: mipmap
            "wrap": GL_REPEAT                      # UV fora de [0,1] repete
        }
        self.setProperties(properties)
        if fileName is not None:
            self.loadImage(fileName)
            self.uploadData()

    def loadImage(self, fileName):
        self.surface = pygame.image.load(fileName)

    def setProperties(self, props):
        for name, data in props.items():
            if name in self.properties.keys():
                self.properties[name] = data
            else:
                raise Exception("Texture has no property with name: " + name)

    def uploadData(self):
        width = self.surface.get_width()
        height = self.surface.get_height()
        # ADAPTAÇÃO: tostring() está obsoleto no pygame 2; tobytes() é o equivalente
        # o "1" inverte a imagem na vertical (no OpenGL o v=0 é embaixo)
        pixelData = pygame.image.tobytes(self.surface, "RGBA", True)
        glBindTexture(GL_TEXTURE_2D, self.textureRef)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, pixelData)
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, self.properties["magFilter"])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, self.properties["minFilter"])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, self.properties["wrap"])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, self.properties["wrap"])
        # borda branca: importante para a sombra (fora do mapa = sem sombra)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, [1, 1, 1, 1])
