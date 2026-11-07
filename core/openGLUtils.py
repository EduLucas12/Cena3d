# Fonte: Stemkoski & Pascale (2022), seção 2.2.2
from OpenGL.GL import *


class OpenGLUtils(object):
    """Métodos estáticos para compilar shaders e ligar (link) o programa na GPU."""

    @staticmethod
    def initializeShader(shaderCode, shaderType):
        # versão da GLSL exigida
        shaderCode = '#version 330\n' + shaderCode
        # cria um objeto shader vazio e guarda a referência
        shaderRef = glCreateShader(shaderType)
        # envia o código-fonte e compila
        glShaderSource(shaderRef, shaderCode)
        glCompileShader(shaderRef)
        # verifica se a compilação deu certo
        compileSuccess = glGetShaderiv(shaderRef, GL_COMPILE_STATUS)
        if not compileSuccess:
            errorMessage = glGetShaderInfoLog(shaderRef)
            glDeleteShader(shaderRef)
            errorMessage = '\n' + errorMessage.decode('utf-8')
            raise Exception(errorMessage)
        return shaderRef

    @staticmethod
    def initializeProgram(vertexShaderCode, fragmentShaderCode):
        vertexShaderRef = OpenGLUtils.initializeShader(vertexShaderCode, GL_VERTEX_SHADER)
        fragmentShaderRef = OpenGLUtils.initializeShader(fragmentShaderCode, GL_FRAGMENT_SHADER)
        # cria o programa, anexa os dois shaders e faz o link
        programRef = glCreateProgram()
        glAttachShader(programRef, vertexShaderRef)
        glAttachShader(programRef, fragmentShaderRef)
        glLinkProgram(programRef)
        linkSuccess = glGetProgramiv(programRef, GL_LINK_STATUS)
        if not linkSuccess:
            errorMessage = glGetProgramInfoLog(programRef)
            glDeleteProgram(programRef)
            errorMessage = '\n' + errorMessage.decode('utf-8')
            raise Exception(errorMessage)
        return programRef

    @staticmethod
    def printSystemInfo():
        print("  Vendor: " + glGetString(GL_VENDOR).decode('utf-8'))
        print("Renderer: " + glGetString(GL_RENDERER).decode('utf-8'))
        print("OpenGL version supported: " + glGetString(GL_VERSION).decode('utf-8'))
        print("  GLSL version supported: " + glGetString(GL_SHADING_LANGUAGE_VERSION).decode('utf-8'))
