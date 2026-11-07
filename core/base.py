# Fonte: Stemkoski & Pascale (2022), seções 2.1, 2.4.3 e 2.5
import pygame
import sys
from core.input import Input


class Base(object):
    """Classe base de toda aplicação: cria a janela com o Pygame,
    mantém o laço principal (entrada -> atualização -> renderização)
    e controla o tempo (time e deltaTime)."""

    def __init__(self, screenSize=[512, 512], title="Graphics Window"):
        # inicializa todos os módulos do pygame
        pygame.init()
        # DOUBLEBUF: dois buffers de imagem (evita "tearing")
        # OPENGL: a janela terá um contexto OpenGL
        displayFlags = pygame.DOUBLEBUF | pygame.OPENGL
        # antialiasing (multisampling com 4 amostras por pixel)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        # perfil "core" do OpenGL (compatível entre plataformas)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,
                                        pygame.GL_CONTEXT_PROFILE_CORE)
        # ADAPTAÇÃO: pede explicitamente a versão 3.3 (necessário em alguns drivers)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        # cria e exibe a janela
        self.screen = pygame.display.set_mode(screenSize, displayFlags)
        pygame.display.set_caption(title)
        # indica se o laço principal está ativo
        self.running = True
        # relógio do pygame: mede o tempo entre quadros
        self.clock = pygame.time.Clock()
        # gerencia a entrada do usuário (teclado / fechar janela)
        self.input = Input()
        # segundos desde que a aplicação começou
        self.time = 0
        self.deltaTime = 0

    # implementado pela classe filha
    def initialize(self):
        pass

    # implementado pela classe filha
    def update(self):
        pass

    def run(self):
        ## inicialização ##
        self.initialize()
        ## laço principal ##
        while self.running:
            ## processa entrada ##
            self.input.update()
            if self.input.quit:
                self.running = False
            # segundos desde a iteração anterior (base das animações por tempo)
            self.deltaTime = self.clock.get_time() / 1000
            self.time += self.deltaTime
            ## atualiza + renderiza (feito no update da aplicação) ##
            self.update()
            # mostra a imagem pronta na tela (troca os buffers)
            pygame.display.flip()
            # limita a 60 quadros por segundo
            self.clock.tick(60)
        ## encerramento ##
        pygame.quit()
        sys.exit()
