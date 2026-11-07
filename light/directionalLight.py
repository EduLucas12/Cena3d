# Fonte: Stemkoski & Pascale (2022), seção 6.2
from light.light import Light


class DirectionalLight(Light):
    """Luz com direção constante (como o Sol). A direção fica guardada
    na matriz de transformação (eixo -z local)."""

    def __init__(self, color=[1, 1, 1], direction=[0, -1, 0]):
        super().__init__(Light.DIRECTIONAL)
        self.color = color
        self.setDirection(direction)
