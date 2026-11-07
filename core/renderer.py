# Fonte: Stemkoski & Pascale (2022), seções 4.5, 5.3, 5.7.3, 5.8, 6.5 e 6.9.2
from OpenGL.GL import *
import pygame
from core.mesh import Mesh
from light.light import Light
from light.shadow import Shadow


class Renderer(object):
    """Desenha a cena: (1) passada de sombra, se ativada; (2) passada normal."""

    def __init__(self, clearColor=[0, 0, 0]):
        glEnable(GL_DEPTH_TEST)       # teste de profundidade (z-buffer)
        glEnable(GL_MULTISAMPLE)      # antialiasing
        # transparência (mistura pelo alfa)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # ADAPTAÇÃO: guarda a cor de fundo para restaurar após a passada de sombra
        self.clearColor = clearColor
        glClearColor(clearColor[0], clearColor[1], clearColor[2], 1)
        self.windowSize = pygame.display.get_surface().get_size()
        self.shadowsEnabled = False

    def enableShadows(self, shadowLight, strength=0.5, resolution=[512, 512],
                      cameraBounds=[-5, 5, -5, 5, 0, 20], bias=0.01):
        self.shadowsEnabled = True
        self.shadowObject = Shadow(shadowLight, strength=strength, resolution=resolution,
                                   cameraBounds=cameraBounds, bias=bias)

    def render(self, scene, camera, clearColor=True, clearDepth=True, renderTarget=None):
        # lista de meshes da cena
        descendantList = scene.getDescendantList()
        meshFilter = lambda x: isinstance(x, Mesh)
        meshList = list(filter(meshFilter, descendantList))

        # ============ PASSADA DE SOMBRA (shadow mapping, seção 6.9) ============
        # desenha a cena do ponto de vista da luz, só gravando a profundidade
        if self.shadowsEnabled:
            glBindFramebuffer(GL_FRAMEBUFFER, self.shadowObject.renderTarget.framebufferRef)
            glViewport(0, 0, self.shadowObject.renderTarget.width,
                       self.shadowObject.renderTarget.height)
            # branco = "muito longe" (sem nada fazendo sombra)
            glClearColor(1, 1, 1, 1)
            glClear(GL_COLOR_BUFFER_BIT)
            glClear(GL_DEPTH_BUFFER_BIT)
            glUseProgram(self.shadowObject.material.programRef)
            self.shadowObject.updateInternal()
            for mesh in meshList:
                if not mesh.visible:
                    continue
                if mesh.material.settings["drawStyle"] != GL_TRIANGLES:
                    continue
                # ADAPTAÇÃO: objetos marcados com castShadow=False não projetam sombra (ex.: céu)
                if not getattr(mesh, "castShadow", True):
                    continue
                glBindVertexArray(mesh.vaoRef)
                self.shadowObject.material.uniforms["modelMatrix"].data = mesh.getWorldMatrix()
                for varName, unifObj in self.shadowObject.material.uniforms.items():
                    unifObj.uploadData()
                glDrawArrays(GL_TRIANGLES, 0, mesh.geometry.vertexCount)
            # ADAPTAÇÃO: restaura a cor de fundo original
            glClearColor(self.clearColor[0], self.clearColor[1], self.clearColor[2], 1)

        # ============ PASSADA NORMAL ============
        if renderTarget is None:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glViewport(0, 0, self.windowSize[0], self.windowSize[1])
        else:
            glBindFramebuffer(GL_FRAMEBUFFER, renderTarget.framebufferRef)
            glViewport(0, 0, renderTarget.width, renderTarget.height)

        if clearColor:
            glClear(GL_COLOR_BUFFER_BIT)
        if clearDepth:
            glClear(GL_DEPTH_BUFFER_BIT)

        # matriz de visão = inversa da câmera
        camera.updateViewMatrix()

        # lista de luzes (o shader espera exatamente 4)
        lightFilter = lambda x: isinstance(x, Light)
        lightList = list(filter(lightFilter, descendantList))
        while len(lightList) < 4:
            lightList.append(Light())

        for mesh in meshList:
            if not mesh.visible:
                continue
            glUseProgram(mesh.material.programRef)
            glBindVertexArray(mesh.vaoRef)
            # uniforms que vêm de fora do material: matrizes model/view/projection
            mesh.material.uniforms["modelMatrix"].data = mesh.getWorldMatrix()
            mesh.material.uniforms["viewMatrix"].data = camera.viewMatrix
            mesh.material.uniforms["projectionMatrix"].data = camera.projectionMatrix
            # luzes
            if "light0" in mesh.material.uniforms.keys():
                for lightNumber in range(4):
                    lightName = "light" + str(lightNumber)
                    mesh.material.uniforms[lightName].data = lightList[lightNumber]
            # posição da câmera (brilho especular do Phong)
            if "viewPosition" in mesh.material.uniforms.keys():
                mesh.material.uniforms["viewPosition"].data = camera.getWorldPosition()
            # sombra
            if self.shadowsEnabled and "shadow0" in mesh.material.uniforms.keys():
                mesh.material.uniforms["shadow0"].data = self.shadowObject
            # envia todos os uniforms para a GPU
            for variableName, uniformObject in mesh.material.uniforms.items():
                uniformObject.uploadData()
            mesh.material.updateRenderSettings()
            glDrawArrays(mesh.material.settings["drawStyle"], 0, mesh.geometry.vertexCount)
