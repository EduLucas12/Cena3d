# Fonte: Stemkoski & Pascale (2022), seções 4.3.4, 5.2.4 e 6.3.4
import numpy
from geometry.geometry import Geometry


class ParametricGeometry(Geometry):
    """Superfície definida por S(u, v) = (x, y, z).
    Base da esfera, elipsoide, cilindro, cone e plano."""

    def __init__(self, uStart, uEnd, uResolution, vStart, vEnd, vResolution, surfaceFunction):
        super().__init__()
        deltaU = (uEnd - uStart) / uResolution
        deltaV = (vEnd - vStart) / vResolution

        # pontos da superfície
        positions = []
        for uIndex in range(uResolution + 1):
            vArray = []
            for vIndex in range(vResolution + 1):
                u = uStart + uIndex * deltaU
                v = vStart + vIndex * deltaV
                vArray.append(surfaceFunction(u, v))
            positions.append(vArray)

        # coordenadas de textura: (u, v) reescalados para [0, 1]
        uvs = []
        for uIndex in range(uResolution + 1):
            vArray = []
            for vIndex in range(vResolution + 1):
                vArray.append([uIndex / uResolution, vIndex / vResolution])
            uvs.append(vArray)

        # normal = produto vetorial de duas arestas, normalizado
        def calcNormal(P0, P1, P2):
            v1 = numpy.array(P1) - numpy.array(P0)
            v2 = numpy.array(P2) - numpy.array(P0)
            normal = numpy.cross(v1, v2)
            length = numpy.linalg.norm(normal)
            # ADAPTAÇÃO: em pontos degenerados (ponta do cone) o vetor é nulo
            # e a divisão daria NaN; nesse caso devolvemos None
            if length < 1e-12:
                return None
            return normal / length

        # normal no vértice: usa pontos muito próximos (u+h, v+h)
        h = 0.0001
        vertexNormals = []
        for uIndex in range(uResolution + 1):
            vArray = []
            for vIndex in range(vResolution + 1):
                u = uStart + uIndex * deltaU
                v = vStart + vIndex * deltaV
                normal = calcNormal(surfaceFunction(u, v),
                                    surfaceFunction(u + h, v),
                                    surfaceFunction(u, v + h))
                # ADAPTAÇÃO: se degenerou, calcula um pouco para dentro da superfície
                if normal is None:
                    vv = v - 0.001 if vIndex > 0 else v + 0.001
                    normal = calcNormal(surfaceFunction(u, vv),
                                        surfaceFunction(u + h, vv),
                                        surfaceFunction(u, vv + h))
                if normal is None:
                    normal = numpy.array([0.0, 1.0, 0.0])
                vArray.append(normal)
            vertexNormals.append(vArray)

        positionData = []
        colorData = []
        uvData = []
        vertexNormalData = []
        faceNormalData = []
        C1, C2, C3 = [1, 0, 0], [0, 1, 0], [0, 0, 1]
        C4, C5, C6 = [0, 1, 1], [1, 0, 1], [1, 1, 0]

        # agrupa em triângulos (cada "quadradinho" do domínio vira 2 triângulos)
        for xIndex in range(uResolution):
            for yIndex in range(vResolution):
                pA = positions[xIndex + 0][yIndex + 0]
                pB = positions[xIndex + 1][yIndex + 0]
                pD = positions[xIndex + 0][yIndex + 1]
                pC = positions[xIndex + 1][yIndex + 1]
                positionData += [pA.copy(), pB.copy(), pC.copy(),
                                 pA.copy(), pC.copy(), pD.copy()]
                colorData += [C1, C2, C3, C4, C5, C6]
                uvA = uvs[xIndex + 0][yIndex + 0]
                uvB = uvs[xIndex + 1][yIndex + 0]
                uvD = uvs[xIndex + 0][yIndex + 1]
                uvC = uvs[xIndex + 1][yIndex + 1]
                uvData += [uvA, uvB, uvC, uvA, uvC, uvD]
                nA = vertexNormals[xIndex + 0][yIndex + 0]
                nB = vertexNormals[xIndex + 1][yIndex + 0]
                nD = vertexNormals[xIndex + 0][yIndex + 1]
                nC = vertexNormals[xIndex + 1][yIndex + 1]
                vertexNormalData += [nA, nB, nC, nA, nC, nD]
                fn0 = calcNormal(pA, pB, pC)
                fn1 = calcNormal(pA, pC, pD)
                if fn0 is None:
                    fn0 = fn1 if fn1 is not None else nA
                if fn1 is None:
                    fn1 = fn0
                faceNormalData += [fn0, fn0, fn0, fn1, fn1, fn1]

        self.addAttribute("vec3", "vertexPosition", positionData)
        self.addAttribute("vec3", "vertexColor", colorData)
        self.addAttribute("vec2", "vertexUV", uvData)
        self.addAttribute("vec3", "vertexNormal", vertexNormalData)
        self.addAttribute("vec3", "faceNormal", faceNormalData)
        self.countVertices()
