# Fonte: Stemkoski & Pascale (2022), seções 2.1 e 2.5.1
import pygame


class Input(object):
    """Lê os eventos do Pygame e guarda o estado das teclas.
    down/up: eventos discretos (duram 1 quadro)
    pressed: evento contínuo (entre o down e o up)"""

    def __init__(self):
        self.quit = False
        self.keyDownList = []
        self.keyPressedList = []
        self.keyUpList = []

    def update(self):
        # limpa os estados discretos do quadro anterior
        self.keyDownList = []
        self.keyUpList = []
        for event in pygame.event.get():
            # clique no X da janela
            if event.type == pygame.QUIT:
                self.quit = True
            if event.type == pygame.KEYDOWN:
                keyName = pygame.key.name(event.key)
                self.keyDownList.append(keyName)
                self.keyPressedList.append(keyName)
            if event.type == pygame.KEYUP:
                keyName = pygame.key.name(event.key)
                # ADAPTAÇÃO: evita erro se a tecla foi pressionada fora da janela
                if keyName in self.keyPressedList:
                    self.keyPressedList.remove(keyName)
                self.keyUpList.append(keyName)

    def isKeyDown(self, keyCode):
        return keyCode in self.keyDownList

    def isKeyPressed(self, keyCode):
        return keyCode in self.keyPressedList

    def isKeyUp(self, keyCode):
        return keyCode in self.keyUpList
