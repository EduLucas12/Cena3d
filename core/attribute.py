# Fonte: Stemkoski & Pascale (2022), seção 2.3.2
from OpenGL.GL import *
import numpy


class Attribute(object):
    """Atributo de vértice (posição, cor, UV, normal...).
    Guarda os dados num buffer da GPU (VBO) e liga esse buffer
    a uma variável 'in' do vertex shader."""

    def __init__(self, dataType, data):
        # tipo: int | float | vec2 | vec3 | vec4
        self.dataType = dataType
        self.data = data
        # pede um buffer livre para a GPU
        self.bufferRef = glGenBuffers(1)
        self.uploadData()

    def uploadData(self):
        # converte para array numpy de floats de 32 bits
        data = numpy.array(self.data).astype(numpy.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.bufferRef)
        glBufferData(GL_ARRAY_BUFFER, data.ravel(), GL_STATIC_DRAW)

    def associateVariable(self, programRef, variableName):
        # procura a variável no programa (shader)
        variableRef = glGetAttribLocation(programRef, variableName)
        # se o shader não usa essa variável, não faz nada
        if variableRef == -1:
            return
        glBindBuffer(GL_ARRAY_BUFFER, self.bufferRef)
        # diz como ler os dados do buffer (quantos componentes por vértice)
        if self.dataType == "int":
            glVertexAttribPointer(variableRef, 1, GL_INT, False, 0, None)
        elif self.dataType == "float":
            glVertexAttribPointer(variableRef, 1, GL_FLOAT, False, 0, None)
        elif self.dataType == "vec2":
            glVertexAttribPointer(variableRef, 2, GL_FLOAT, False, 0, None)
        elif self.dataType == "vec3":
            glVertexAttribPointer(variableRef, 3, GL_FLOAT, False, 0, None)
        elif self.dataType == "vec4":
            glVertexAttribPointer(variableRef, 4, GL_FLOAT, False, 0, None)
        else:
            raise Exception("Attribute " + variableName + " has unknown type " + self.dataType)
        # habilita o envio de dados para essa variável
        # (essa associação fica gravada no VAO que estiver ligado)
        glEnableVertexAttribArray(variableRef)
