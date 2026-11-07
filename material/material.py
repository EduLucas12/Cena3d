# Fonte: Stemkoski & Pascale (2022), seção 4.4.1
from core.openGLUtils import OpenGLUtils
from core.uniform import Uniform
from OpenGL.GL import *


class Material(object):
    """Guarda: programa de shader, uniforms e configurações de renderização."""

    def __init__(self, vertexShaderCode, fragmentShaderCode):
        self.programRef = OpenGLUtils.initializeProgram(vertexShaderCode, fragmentShaderCode)
        self.uniforms = {}
        # todo shader usa essas três matrizes (preenchidas pelo Renderer)
        self.uniforms["modelMatrix"] = Uniform("mat4", None)
        self.uniforms["viewMatrix"] = Uniform("mat4", None)
        self.uniforms["projectionMatrix"] = Uniform("mat4", None)
        self.settings = {}
        self.settings["drawStyle"] = GL_TRIANGLES

    def addUniform(self, dataType, variableName, data):
        self.uniforms[variableName] = Uniform(dataType, data)

    def locateUniforms(self):
        for variableName, uniformObject in self.uniforms.items():
            uniformObject.locateVariable(self.programRef, variableName)

    def updateRenderSettings(self):
        pass

    # muda uniforms ou settings a partir de um dicionário
    def setProperties(self, properties):
        for name, data in properties.items():
            if name in self.uniforms.keys():
                self.uniforms[name].data = data
            elif name in self.settings.keys():
                self.settings[name] = data
            else:
                raise Exception("Material has no property named: " + name)
