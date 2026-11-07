# Fonte: Stemkoski & Pascale (2022), seções 4.3.1, 5.2.1, 5.7.3 e 6.3.1
from geometry.geometry import Geometry


class RectangleGeometry(Geometry):
    def __init__(self, width=1, height=1, position=[0, 0], alignment=[0.5, 0.5]):
        super().__init__()
        x, y = position
        a, b = alignment
        P0 = [x + (-a) * width, y + (-b) * height, 0]
        P1 = [x + (1 - a) * width, y + (-b) * height, 0]
        P2 = [x + (-a) * width, y + (1 - b) * height, 0]
        P3 = [x + (1 - a) * width, y + (1 - b) * height, 0]
        C0, C1, C2, C3 = [1, 1, 1], [1, 0, 0], [0, 1, 0], [0, 0, 1]
        # dois triângulos, sentido anti-horário
        positionData = [P0, P1, P3, P0, P3, P2]
        colorData = [C0, C1, C3, C0, C3, C2]
        self.addAttribute("vec3", "vertexPosition", positionData)
        self.addAttribute("vec3", "vertexColor", colorData)
        # coordenadas de textura: cantos da imagem nos cantos do retângulo
        T0, T1, T2, T3 = [0, 0], [1, 0], [0, 1], [1, 1]
        uvData = [T0, T1, T3, T0, T3, T2]
        self.addAttribute("vec2", "vertexUV", uvData)
        # normal: retângulo no plano xy aponta para +z
        normalVector = [0, 0, 1]
        normalData = [normalVector] * 6
        self.addAttribute("vec3", "vertexNormal", normalData)
        self.addAttribute("vec3", "faceNormal", normalData)
        self.countVertices()
