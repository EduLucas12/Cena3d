# Fonte: Stemkoski & Pascale (2022), seções 4.3 e 6.3.4
import numpy
from core.attribute import Attribute


class Geometry(object):
    """Guarda os atributos de vértice (posição, cor, UV, normais)."""

    def __init__(self):
        self.attributes = {}
        self.vertexCount = None

    def addAttribute(self, dataType, variableName, data):
        self.attributes[variableName] = Attribute(dataType, data)

    def countVertices(self):
        attrib = list(self.attributes.values())[0]
        self.vertexCount = len(attrib.data)

    # aplica uma matriz direto nos vértices (usado para tampar o cilindro)
    def applyMatrix(self, matrix, variableName="vertexPosition"):
        oldPositionData = self.attributes[variableName].data
        newPositionData = []
        for oldPos in oldPositionData:
            newPos = list(oldPos).copy()
            newPos.append(1)              # coordenada homogênea
            newPos = matrix @ newPos
            newPos = list(newPos[0:3])
            newPositionData.append(newPos)
        self.attributes[variableName].data = newPositionData

        # normais giram só com a parte de rotação da matriz
        rotationMatrix = numpy.array([matrix[0][0:3], matrix[1][0:3], matrix[2][0:3]])
        for normalName in ["vertexNormal", "faceNormal"]:
            if normalName in self.attributes:
                oldData = self.attributes[normalName].data
                newData = [list(rotationMatrix @ numpy.array(n)) for n in oldData]
                self.attributes[normalName].data = newData
                self.attributes[normalName].uploadData()

        self.attributes[variableName].uploadData()

    # junta os atributos de outra geometria nesta
    def merge(self, otherGeometry):
        for variableName, attributeObject in self.attributes.items():
            attributeObject.data += otherGeometry.attributes[variableName].data
            attributeObject.uploadData()
        self.countVertices()
