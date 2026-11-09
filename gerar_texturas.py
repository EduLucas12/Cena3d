# Gera as imagens de textura usadas na cena (pasta images/).
# As texturas são desenhadas com o próprio Pygame, então não dependem
# de imagens externas. Rode uma vez:  python gerar_texturas.py
import os
import random
import math
import pygame

pygame.init()
random.seed(619)  # semente fixa: sempre gera as mesmas imagens (temas 6 e 19)
PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(PASTA, exist_ok=True)


def ruido(surf, intensidade, base):
    """Pinta cada pixel com a cor base + uma variação aleatória (aspecto granulado)."""
    w, h = surf.get_size()
    for x in range(w):
        for y in range(h):
            d = random.randint(-intensidade, intensidade)
            surf.set_at((x, y), tuple(max(0, min(255, c + d)) for c in base))


def concreto():
    """Placas de concreto do pátio (repetida várias vezes no chão)."""
    s = pygame.Surface((256, 256))
    ruido(s, 12, (150, 148, 142))
    # juntas entre as placas
    pygame.draw.line(s, (95, 93, 90), (0, 0), (255, 0), 3)
    pygame.draw.line(s, (95, 93, 90), (0, 0), (0, 255), 3)
    # algumas manchas
    for _ in range(6):
        x, y, r = random.randint(20, 236), random.randint(20, 236), random.randint(8, 22)
        mancha = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
        pygame.draw.circle(mancha, (90, 88, 84, 40), (r, r), r)
        s.blit(mancha, (x - r, y - r))
    pygame.image.save(s, os.path.join(PASTA, "concreto.png"))


def plataforma():
    """Disco da plataforma de lançamento (aplicado num polígono circular)."""
    n = 512
    c = n // 2
    s = pygame.Surface((n, n))
    ruido(s, 10, (70, 72, 76))
    # faixa de segurança zebrada (amarelo/preto) na borda
    for i in range(48):
        a0 = 2 * math.pi * i / 48
        a1 = 2 * math.pi * (i + 1) / 48
        cor = (230, 190, 30) if i % 2 == 0 else (25, 25, 25)
        pts = [(c + 250 * math.cos(a0), c + 250 * math.sin(a0)),
               (c + 250 * math.cos(a1), c + 250 * math.sin(a1)),
               (c + 215 * math.cos(a1), c + 215 * math.sin(a1)),
               (c + 215 * math.cos(a0), c + 215 * math.sin(a0))]
        pygame.draw.polygon(s, cor, pts)
    # círculos e cruz de alinhamento
    pygame.draw.circle(s, (235, 235, 235), (c, c), 150, 6)
    pygame.draw.circle(s, (235, 235, 235), (c, c), 60, 6)
    pygame.draw.line(s, (235, 235, 235), (c - 200, c), (c + 200, c), 5)
    pygame.draw.line(s, (235, 235, 235), (c, c - 200), (c, c + 200), 5)
    # marca de queimado no centro (escapamento dos motores)
    for r in range(55, 0, -1):
        k = int(70 * (1 - r / 55))
        pygame.draw.circle(s, (70 - k // 2, 68 - k // 2, 66 - k // 2), (c, c), r)
    # identificação da base
    fonte = pygame.font.Font(None, 54)
    txt = fonte.render("BASE 6-19", True, (235, 235, 235))
    s.blit(txt, txt.get_rect(center=(c, c + 105)))
    pygame.image.save(s, os.path.join(PASTA, "plataforma.png"))


def metal():
    """Painéis metálicos rebitados (torre de comando)."""
    s = pygame.Surface((256, 256))
    ruido(s, 8, (176, 182, 190))
    for k in (0, 128):
        pygame.draw.line(s, (110, 115, 122), (0, k), (255, k), 3)
        pygame.draw.line(s, (110, 115, 122), (k, 0), (k, 255), 3)
    for x in range(12, 256, 32):
        for y in (8, 120, 136, 248):
            pygame.draw.circle(s, (120, 125, 132), (x, y), 3)
            pygame.draw.circle(s, (215, 220, 226), (x - 1, y - 1), 1)
    pygame.image.save(s, os.path.join(PASTA, "metal.png"))


def ceu():
    """Céu de fim de tarde com estrelas (aplicado numa esfera gigante).
    Na esfera, v=1 é o topo (zênite) e v=0.5 é o horizonte."""
    w, h = 1024, 512
    s = pygame.Surface((w, h))
    topo, meio, horizonte = (8, 10, 32), (40, 46, 96), (235, 140, 80)
    for y in range(h):
        t = y / (h / 2)  # 0 no zênite, 1 no horizonte
        if t <= 1:
            if t < 0.7:
                k = t / 0.7
                cor = [topo[i] + (meio[i] - topo[i]) * k for i in range(3)]
            else:
                k = (t - 0.7) / 0.3
                cor = [meio[i] + (horizonte[i] - meio[i]) * k for i in range(3)]
        else:
            cor = (60, 50, 50)  # abaixo do horizonte (fica escondido pelo chão)
        pygame.draw.line(s, [int(c) for c in cor], (0, y), (w, y))
    # estrelas só na parte de cima
    for _ in range(900):
        x, y = random.randint(0, w - 1), random.randint(0, int(h * 0.38))
        b = random.randint(150, 255)
        s.set_at((x, y), (b, b, b))
        if random.random() < 0.08:
            pygame.draw.circle(s, (b, b, 255), (x, y), 1)
    pygame.image.save(s, os.path.join(PASTA, "ceu.png"))


if __name__ == "__main__":
    concreto()
    plataforma()
    metal()
    ceu()
    print("Texturas geradas em", PASTA)
