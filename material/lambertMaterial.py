# Fonte: Stemkoski & Pascale (2022), seção 6.4.2
from material.phongMaterial import PhongMaterial


class LambertMaterial(PhongMaterial):
    """Lambert = Phong sem a parcela especular (superfície fosca).
    ADAPTAÇÃO: no livro é um arquivo copiado; aqui herdamos do Phong
    e zeramos specularStrength para não duplicar o shader."""

    def __init__(self, texture=None, properties={}, useShadow=False):
        super().__init__(texture, {}, useShadow)
        self.uniforms["specularStrength"].data = 0
        self.setProperties(properties)
