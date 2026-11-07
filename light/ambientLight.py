# Fonte: Stemkoski & Pascale (2022), seção 6.2
from light.light import Light


class AmbientLight(Light):
    def __init__(self, color=[1, 1, 1]):
        super().__init__(Light.AMBIENT)
        self.color = color
