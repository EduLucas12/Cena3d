# Fonte: Stemkoski & Pascale (2022), seções 2.4.2, 3.4, 5.3, 6.4.1 e 6.9.2
from OpenGL.GL import *


class Uniform(object):
    """Variável 'uniform': valor igual para todos os vértices de um desenho
    (matrizes, cor, textura, luzes, sombra)."""

    def __init__(self, dataType, data):
        # tipo: int | bool | float | vec2 | vec3 | vec4 | mat4 | sampler2D | Light | Shadow
        self.dataType = dataType
        self.data = data
        self.variableRef = None

    def locateVariable(self, programRef, variableName):
        # structs (Light e Shadow) têm uma referência para cada campo
        if self.dataType == "Light":
            self.variableRef = {}
            for field in ["lightType", "color", "direction", "position", "attenuation"]:
                self.variableRef[field] = glGetUniformLocation(programRef, variableName + "." + field)
        elif self.dataType == "Shadow":
            self.variableRef = {}
            for field in ["lightDirection", "projectionMatrix", "viewMatrix",
                          "depthTexture", "strength", "bias"]:
                self.variableRef[field] = glGetUniformLocation(programRef, variableName + "." + field)
        else:
            self.variableRef = glGetUniformLocation(programRef, variableName)

    def uploadData(self):
        # se o programa não usa a variável, sai
        if self.variableRef == -1:
            return
        # ADAPTAÇÃO: sem dado ainda (ex.: sombra desativada), não envia nada
        if self.data is None:
            return
        if self.dataType == "int":
            glUniform1i(self.variableRef, self.data)
        elif self.dataType == "bool":
            glUniform1i(self.variableRef, self.data)
        elif self.dataType == "float":
            glUniform1f(self.variableRef, self.data)
        elif self.dataType == "vec2":
            glUniform2f(self.variableRef, self.data[0], self.data[1])
        elif self.dataType == "vec3":
            glUniform3f(self.variableRef, self.data[0], self.data[1], self.data[2])
        elif self.dataType == "vec4":
            glUniform4f(self.variableRef, self.data[0], self.data[1], self.data[2], self.data[3])
        elif self.dataType == "mat4":
            # GL_TRUE: a matriz numpy está em ordem de linhas, o OpenGL transpõe
            glUniformMatrix4fv(self.variableRef, 1, GL_TRUE, self.data)
        elif self.dataType == "sampler2D":
            textureObjectRef, textureUnitRef = self.data
            # ativa a unidade de textura, liga a textura nela
            # e envia o NÚMERO da unidade para o sampler do shader
            glActiveTexture(GL_TEXTURE0 + textureUnitRef)
            glBindTexture(GL_TEXTURE_2D, textureObjectRef)
            glUniform1i(self.variableRef, textureUnitRef)
        elif self.dataType == "Light":
            glUniform1i(self.variableRef["lightType"], self.data.lightType)
            glUniform3f(self.variableRef["color"], *self.data.color)
            direction = self.data.getDirection()
            glUniform3f(self.variableRef["direction"], *direction)
            # ADAPTAÇÃO: posição no mundo (o livro usa getPosition, local)
            position = self.data.getWorldPosition()
            glUniform3f(self.variableRef["position"], *position)
            glUniform3f(self.variableRef["attenuation"], *self.data.attenuation)
        elif self.dataType == "Shadow":
            direction = self.data.lightSource.getDirection()
            glUniform3f(self.variableRef["lightDirection"], *direction)
            glUniformMatrix4fv(self.variableRef["projectionMatrix"], 1, GL_TRUE,
                               self.data.camera.projectionMatrix)
            glUniformMatrix4fv(self.variableRef["viewMatrix"], 1, GL_TRUE,
                               self.data.camera.viewMatrix)
            # textura de profundidade vai na unidade 15 (pouco usada pelas outras)
            textureObjectRef = self.data.renderTarget.texture.textureRef
            textureUnitRef = 15
            glActiveTexture(GL_TEXTURE0 + textureUnitRef)
            glBindTexture(GL_TEXTURE_2D, textureObjectRef)
            glUniform1i(self.variableRef["depthTexture"], textureUnitRef)
            glUniform1f(self.variableRef["strength"], self.data.strength)
            glUniform1f(self.variableRef["bias"], self.data.bias)
