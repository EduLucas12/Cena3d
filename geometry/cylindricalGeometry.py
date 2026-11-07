# Fonte: Stemkoski & Pascale (2022), seção 4.3.6
from geometry.parametricGeometry import ParametricGeometry
from geometry.polygonGeometry import PolygonGeometry
from core.matrix import Matrix
from math import sin, cos, pi


class CylindricalGeometry(ParametricGeometry):
    """Raio interpolado entre o de baixo e o de cima:
    gera cilindro, cone, prisma, pirâmide e tronco de cone."""

    def __init__(self, radiusTop=1, radiusBottom=1, height=1,
                 radialSegments=32, heightSegments=4, closedTop=True, closedBottom=True):
        def S(u, v):
            return [(v * radiusTop + (1 - v) * radiusBottom) * sin(u),
                    height * (v - 0.5),
                    (v * radiusTop + (1 - v) * radiusBottom) * cos(u)]
        super().__init__(0, 2 * pi, radialSegments, 0, 1, heightSegments, S)

        # tampas: polígonos girados e movidos para cima/baixo
        if closedTop:
            topGeometry = PolygonGeometry(radialSegments, radiusTop)
            transform = Matrix.makeTranslation(0, height / 2, 0) @ \
                Matrix.makeRotationY(-pi / 2) @ Matrix.makeRotationX(-pi / 2)
            topGeometry.applyMatrix(transform)
            self.merge(topGeometry)
        if closedBottom:
            bottomGeometry = PolygonGeometry(radialSegments, radiusBottom)
            transform = Matrix.makeTranslation(0, -height / 2, 0) @ \
                Matrix.makeRotationY(-pi / 2) @ Matrix.makeRotationX(pi / 2)
            bottomGeometry.applyMatrix(transform)
            self.merge(bottomGeometry)
