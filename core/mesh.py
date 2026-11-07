# Fonte: Stemkoski & Pascale (2022), seção 4.2.3
from core.object3D import Object3D
from OpenGL.GL import *


class Mesh(Object3D):
    """Objeto visível = Geometry (forma) + Material (aparência).
    O VAO guarda a ligação entre os buffers da geometria e as
    variáveis 'in' do shader do material."""

    def __init__(self, geometry, material):
        super().__init__()
        self.geometry = geometry
        self.material = material
        self.visible = True
        # cria e liga o VAO
        self.vaoRef = glGenVertexArrays(1)
        glBindVertexArray(self.vaoRef)
        for variableName, attributeObject in geometry.attributes.items():
            attributeObject.associateVariable(material.programRef, variableName)
        glBindVertexArray(0)
