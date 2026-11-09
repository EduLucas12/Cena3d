# Ambiente da cena: pátio de concreto, plataforma de lançamento,
# torre de comando (com porta e elevador animáveis), tanques e céu.
# Tudo composto com as geometrias do framework (Stemkoski & Pascale, cap. 4).
from math import pi
from core.mesh import Mesh
from core.group import Group
from core.texture import Texture
from geometry.boxGeometry import BoxGeometry
from geometry.rectangleGeometry import RectangleGeometry
from geometry.polygonGeometry import PolygonGeometry
from geometry.cylinderGeometry import CylinderGeometry
from geometry.coneGeometry import ConeGeometry
from geometry.sphereGeometry import SphereGeometry
from material.phongMaterial import PhongMaterial
from material.lambertMaterial import LambertMaterial
from material.textureMaterial import TextureMaterial

# posição da torre de comando no mundo
TORRE_X, TORRE_Z = -8.0, -2.0
ALTURA_CABINE = 8.0          # altura do piso da cabine


def criarCenario(scene):
    """Monta o ambiente e devolve as peças que serão animadas depois."""

    # ---------------- texturas (geradas por gerar_texturas.py) ----------------
    texConcreto = Texture("images/concreto.png")
    texPlataforma = Texture("images/plataforma.png")
    texMetal = Texture("images/metal.png")
    texCeu = Texture("images/ceu.png")

    # ---------------- céu ----------------
    # esfera gigante com a textura por dentro; não recebe luz (TextureMaterial)
    ceu = Mesh(SphereGeometry(radius=90, radiusSegments=48, heightSegments=24),
               TextureMaterial(texCeu))
    ceu.castShadow = False       # o céu não deve aparecer no mapa de sombra
    scene.add(ceu)

    # ---------------- chão ----------------
    # retângulo 200x200 deitado (rotação de -90° em X); maior que o céu para não sobrar borda
    # a textura repete 100x (placas de 2 m)
    chao = Mesh(RectangleGeometry(200, 200),
                LambertMaterial(texture=texConcreto, useShadow=True,
                                properties={"repeatUV": [100, 100]}))
    chao.rotateX(-pi / 2)
    scene.add(chao)

    # ---------------- plataforma de lançamento ----------------
    plataforma = Group()
    scene.add(plataforma)
    base = Mesh(CylinderGeometry(radius=3.4, height=0.3, radialSegments=48),
                PhongMaterial(useShadow=True, properties={"baseColor": [0.35, 0.36, 0.38],
                                                          "specularStrength": 0.2}))
    base.setPosition([0, 0.15, 0])
    plataforma.add(base)
    # disco de cima com a textura (as coordenadas UV do polígono "recortam" um círculo da imagem)
    disco = Mesh(PolygonGeometry(sides=48, radius=3.4),
                 LambertMaterial(texture=texPlataforma, useShadow=True))
    disco.setPosition([0, 0.301, 0])
    disco.rotateX(-pi / 2)
    plataforma.add(disco)

    # ---------------- torre de comando ----------------
    torre = Group()
    torre.setPosition([TORRE_X, 0, TORRE_Z])
    scene.add(torre)

    matMetal = PhongMaterial(texture=texMetal, useShadow=True,
                             properties={"repeatUV": [1, 4], "specularStrength": 0.5})
    pilar = Mesh(BoxGeometry(1.6, ALTURA_CABINE, 1.6), matMetal)
    pilar.setPosition([0, ALTURA_CABINE / 2, 0])
    torre.add(pilar)

    # cabine no topo
    matCabine = PhongMaterial(texture=texMetal, useShadow=True,
                              properties={"baseColor": [0.95, 0.95, 1.0], "specularStrength": 0.5})
    cabine = Mesh(BoxGeometry(3.2, 2.0, 3.2), matCabine)
    cabine.setPosition([0, ALTURA_CABINE + 1.0, 0])
    torre.add(cabine)
    # faixa de vidro (janelas) em volta da cabine
    vidro = Mesh(BoxGeometry(3.26, 0.6, 3.26),
                 PhongMaterial(useShadow=True, properties={"baseColor": [0.15, 0.3, 0.45],
                                                           "shininess": 64}))
    vidro.setPosition([0, ALTURA_CABINE + 1.45, 0])
    torre.add(vidro)
    # teto e antena
    teto = Mesh(BoxGeometry(3.6, 0.2, 3.6),
                PhongMaterial(useShadow=True, properties={"baseColor": [0.8, 0.25, 0.2]}))
    teto.setPosition([0, ALTURA_CABINE + 2.1, 0])
    torre.add(teto)
    antena = Mesh(CylinderGeometry(radius=0.05, height=1.5),
                  PhongMaterial(properties={"baseColor": [0.7, 0.7, 0.7]}))
    antena.setPosition([0.8, ALTURA_CABINE + 2.95, 0.8])
    torre.add(antena)
    luzAntena = Mesh(SphereGeometry(0.12),
                     PhongMaterial(properties={"baseColor": [1.0, 0.1, 0.1]}))
    luzAntena.setPosition([0.8, ALTURA_CABINE + 3.75, 0.8])
    torre.add(luzAntena)

    # porta da cabine, na face +x (virada para a plataforma).
    # HIERARQUIA: o pivô fica na dobradiça; girar o pivô gira a porta em torno dela.
    portaPivo = Group()
    portaPivo.setPosition([1.62, ALTURA_CABINE, 0.45])
    torre.add(portaPivo)
    porta = Mesh(BoxGeometry(0.06, 1.5, 0.9),
                 PhongMaterial(useShadow=True, properties={"baseColor": [0.9, 0.55, 0.1]}))
    porta.setPosition([0, 0.75, -0.45])
    portaPivo.add(porta)

    # elevador externo: trilhos fixos + plataforma móvel
    matTrilho = PhongMaterial(useShadow=True, properties={"baseColor": [0.25, 0.25, 0.28]})
    for dz in (-0.8, 0.8):
        trilho = Mesh(BoxGeometry(0.12, ALTURA_CABINE + 0.5, 0.12), matTrilho)
        trilho.setPosition([3.15, (ALTURA_CABINE + 0.5) / 2, dz])
        torre.add(trilho)
    elevador = Group()
    elevador.setPosition([2.4, ALTURA_CABINE, 0])  # começa lá em cima, na porta
    torre.add(elevador)
    piso = Mesh(BoxGeometry(1.5, 0.12, 1.5),
                PhongMaterial(useShadow=True, properties={"baseColor": [0.95, 0.75, 0.1]}))
    piso.setPosition([0, -0.06, 0])
    elevador.add(piso)
    for dz in (-0.72, 0.72):
        corrimao = Mesh(BoxGeometry(1.5, 0.05, 0.05), matTrilho)
        corrimao.setPosition([0, 0.9, dz])
        elevador.add(corrimao)
        for dx in (-0.72, 0.72):
            poste = Mesh(BoxGeometry(0.05, 0.9, 0.05), matTrilho)
            poste.setPosition([dx, 0.45, dz])
            elevador.add(poste)

    # ---------------- tanques de combustível ----------------
    matTanque = PhongMaterial(useShadow=True, properties={"baseColor": [0.92, 0.92, 0.9]})
    for (x, z) in [(7.5, -6.0), (9.6, -4.2)]:
        tanque = Group()
        tanque.setPosition([x, 0, z])
        scene.add(tanque)
        corpo = Mesh(CylinderGeometry(radius=0.9, height=3.0), matTanque)
        corpo.setPosition([0, 1.5, 0])
        tanque.add(corpo)
        topo = Mesh(SphereGeometry(0.9), matTanque)
        topo.setPosition([0, 3.0, 0])
        tanque.add(topo)
        faixa = Mesh(CylinderGeometry(radius=0.92, height=0.25),
                     PhongMaterial(useShadow=True, properties={"baseColor": [0.85, 0.2, 0.15]}))
        faixa.setPosition([0, 2.2, 0])
        tanque.add(faixa)

    # ---------------- cones de sinalização ----------------
    matCone = PhongMaterial(useShadow=True, properties={"baseColor": [1.0, 0.45, 0.05]})
    for (x, z) in [(-4.4, 4.2), (3.5, 3.8), (4.6, 0.0), (-4.2, -4.0)]:
        cone = Mesh(ConeGeometry(radius=0.2, height=0.5), matCone)
        cone.setPosition([x, 0.25, z])
        scene.add(cone)

    return {
        "portaPivo": portaPivo,
        "elevador": elevador,
    }
