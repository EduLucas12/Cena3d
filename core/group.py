# Fonte: Stemkoski & Pascale (2022), seção 4.2.1
from core.object3D import Object3D


class Group(Object3D):
    """Nó interno, só para agrupar e transformar várias peças juntas."""
    def __init__(self):
        super().__init__()
