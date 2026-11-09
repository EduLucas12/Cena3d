# Sequência de animação da cena (requisito 2: animação baseada no tempo + interação).
#
# IDEIA: tudo é calculado a partir de UM número, o tempo da animação t (segundos).
# Cada fase tem início e fim; fase(t, ini, fim) diz quanto daquela fase já passou (0..1).
# Como a pose depende só de t, pausar = parar de avançar t; reiniciar = t = 0.
from math import pi, sin, cos, atan2, sqrt
from core.matrix import Matrix
from modelos.nave import RAIO, ANGULO_RAMPA_ABERTA
from modelos.cenario import TORRE_X, TORRE_Z, ALTURA_CABINE

# --------------------------------------------------------------------------
# Linha do tempo (segundos)
# --------------------------------------------------------------------------
FASES = [
    ("Base em espera",                       0.0,  1.5),
    ("Porta da cabine abre",                 1.5,  2.5),
    ("Astronauta sai da cabine",             2.5,  4.0),
    ("Vira para o publico",                  4.0,  4.8),
    ("Elevador desce",                       4.8,  8.8),
    ("Caminha ate o publico",                8.8, 13.3),
    ("Vira para o publico",                 13.3, 13.8),
    ("Da tchau para o publico",             13.8, 17.3),
    ("Nave gira e reconhece o astronauta",  17.3, 19.8),
    ("Rampa abre",                          19.8, 21.2),
    ("Astronauta responde com sinal",       21.2, 22.6),
    ("Caminha ate a nave",                  22.6, 25.0),
    ("Sobe a rampa e embarca",              25.0, 27.3),
    ("Rampa fecha",                         27.3, 28.8),
    ("Ignicao dos motores",                 28.8, 31.0),
    ("Decolagem e afastamento",             31.0, 39.0),
]
DURACAO = 39.0

# pontos importantes do percurso (mundo)
ELEV_X = TORRE_X + 2.4                 # centro do elevador
DENTRO_CABINE = TORRE_X + 0.8          # astronauta escondido dentro da cabine
PONTO_PUBLICO = (-2.2, 5.0)            # onde ele para para dar tchau
RAIO_PLATAFORMA = 3.4
ALTURA_PLATAFORMA = 0.3


# --------------------------------------------------------------------------
# Funções auxiliares
# --------------------------------------------------------------------------
def fase(t, inicio, fim):
    """Fração (0..1) da fase já percorrida."""
    if t <= inicio:
        return 0.0
    if t >= fim:
        return 1.0
    return (t - inicio) / (fim - inicio)


def suave(x):
    """Ease-in/ease-out (smoothstep): começa e termina devagar, sem tranco."""
    return x * x * (3 - 2 * x)


def lerp(a, b, x):
    return a + (b - a) * x


def lerpAngulo(a, b, x):
    """Interpola ângulos pelo caminho mais curto."""
    d = (b - a + pi) % (2 * pi) - pi
    return a + d * x


def direcao(origem, destino):
    """Guinada (yaw) para olhar de origem até destino no plano xz."""
    return atan2(destino[0] - origem[0], destino[1] - origem[1])


def alturaDoChao(x, z):
    """O astronauta sobe 0,3 ao pisar na plataforma (transição curta na borda)."""
    r = sqrt(x * x + z * z)
    return ALTURA_PLATAFORMA * suave(min(1.0, max(0.0, (RAIO_PLATAFORMA + 0.1 - r) / 0.25)))


class Sequencia(object):

    def __init__(self, cena):
        self.nave = cena.nave
        self.astro = cena.astronauta
        self.portaPivo = cena.pecas["portaPivo"]
        self.elevador = cena.pecas["elevador"]
        self.luzMotor = cena.luzMotor
        self.posPorta = self.portaPivo.getPosition()

        # ângulos e pontos calculados uma vez (dependem da posição do astronauta)
        self.guinadaNaveInicial = pi / 2                                  # escotilha para +x
        self.guinadaNaveFinal = direcao((0, 0), PONTO_PUBLICO)           # escotilha para ele
        self.guinadaParaNave = direcao(PONTO_PUBLICO, (0, 0))
        # ponta da rampa aberta e dobradiça, no mundo (ao longo da direção da escotilha)
        dx, dz = sin(self.guinadaNaveFinal), cos(self.guinadaNaveFinal)
        rPonta = RAIO + 0.03 + 1.4 * sin(ANGULO_RAMPA_ABERTA)
        self.pontaRampa = (dx * rPonta, dz * rPonta)
        self.dobradica = (dx * (RAIO + 0.03), dz * (RAIO + 0.03))
        self.interior = (dx * 0.15, dz * 0.15)
        self.faseAtual = FASES[0][0]

    # ----------------------------------------------------------------------
    def aplicar(self, t):
        """Coloca todos os objetos na configuração do instante t."""
        for nome, ini, fim in FASES:
            if ini <= t < fim:
                self.faseAtual = nome
        if t >= DURACAO:
            self.faseAtual = "Fim (Enter reinicia)"

        self._porta(t)
        self._elevadorEAstronauta(t)
        self._nave(t)

    # ----------------------------------------------------------------------
    def _porta(self, t):
        # abre em 1.5-2.5 s e fecha em 4.0-5.0 s (rotação em torno da dobradiça)
        abertura = suave(fase(t, 1.5, 2.5)) - suave(fase(t, 4.0, 5.0))
        self.portaPivo.transform = (Matrix.makeTranslation(*self.posPorta)
                                    @ Matrix.makeRotationY(-1.75 * abertura))

    # ----------------------------------------------------------------------
    def _elevadorEAstronauta(self, t):
        a = self.astro

        # elevador: desce de ALTURA_CABINE até 0 (o astronauta vai junto)
        yElev = lerp(ALTURA_CABINE, 0.0, suave(fase(t, 4.8, 8.8)))
        self.elevador.setPosition([2.4, yElev, 0])

        a.setVisivel(t < 27.3)
        if t < 2.5:                                         # dentro da cabine
            a.setTransform([DENTRO_CABINE, ALTURA_CABINE, TORRE_Z], pi / 2)
            a.posePadrao()
        elif t < 4.0:                                       # sai andando até o elevador
            x = lerp(DENTRO_CABINE, ELEV_X, fase(t, 2.5, 4.0))
            a.setTransform([x, ALTURA_CABINE, TORRE_Z], pi / 2)
            a.poseAndando(t)
        elif t < 8.8:                                       # vira e desce com o elevador
            g = lerpAngulo(pi / 2, 0.0, suave(fase(t, 4.0, 4.8)))
            a.setTransform([ELEV_X, yElev, TORRE_Z], g)
            a.posePadrao()
        elif t < 13.3:                                      # caminha até o público
            ini, fim = (ELEV_X, TORRE_Z), PONTO_PUBLICO
            k = fase(t, 8.8, 13.3)
            x, z = lerp(ini[0], fim[0], k), lerp(ini[1], fim[1], k)
            g = lerpAngulo(0.0, direcao(ini, fim), fase(t, 8.8, 9.2))
            a.setTransform([x, alturaDoChao(x, z), z], g)
            a.poseAndando(t)
        elif t < 13.8:                                      # vira de frente para a câmera
            g = lerpAngulo(direcao((ELEV_X, TORRE_Z), PONTO_PUBLICO), 0.0,
                           suave(fase(t, 13.3, 13.8)))
            a.setTransform([PONTO_PUBLICO[0], 0, PONTO_PUBLICO[1]], g)
            a.posePadrao()
        elif t < 17.3:                                      # TCHAU
            k = fase(t, 13.8, 17.3)
            levantar = suave(min(1.0, k / 0.12)) * suave(min(1.0, (1 - k) / 0.12))
            a.setTransform([PONTO_PUBLICO[0], 0, PONTO_PUBLICO[1]], 0.0)
            a.poseAceno(t, levantar)
        elif t < 21.2:                                      # vira para a nave e observa
            g = lerpAngulo(0.0, self.guinadaParaNave, suave(fase(t, 17.3, 17.9)))
            a.setTransform([PONTO_PUBLICO[0], 0, PONTO_PUBLICO[1]], g)
            a.posePadrao()
        elif t < 22.6:                                      # responde à nave (sinal)
            k = fase(t, 21.2, 22.6)
            levantar = suave(min(1.0, k / 0.25)) * suave(min(1.0, (1 - k) / 0.25))
            a.setTransform([PONTO_PUBLICO[0], 0, PONTO_PUBLICO[1]], self.guinadaParaNave)
            a.poseSinal(levantar)
        elif t < 25.0:                                      # anda até a ponta da rampa
            k = fase(t, 22.6, 25.0)
            x = lerp(PONTO_PUBLICO[0], self.pontaRampa[0], k)
            z = lerp(PONTO_PUBLICO[1], self.pontaRampa[1], k)
            a.setTransform([x, alturaDoChao(x, z), z], self.guinadaParaNave)
            a.poseAndando(t)
        elif t < 26.6:                                      # sobe a rampa (y aumenta)
            k = fase(t, 25.0, 26.6)
            x = lerp(self.pontaRampa[0], self.dobradica[0], k)
            z = lerp(self.pontaRampa[1], self.dobradica[1], k)
            y = lerp(ALTURA_PLATAFORMA, ALTURA_PLATAFORMA + 0.95, k)
            a.setTransform([x, y, z], self.guinadaParaNave)
            a.poseAndando(t)
        else:                                               # entra na nave
            k = fase(t, 26.6, 27.3)
            x = lerp(self.dobradica[0], self.interior[0], k)
            z = lerp(self.dobradica[1], self.interior[1], k)
            a.setTransform([x, ALTURA_PLATAFORMA + 0.95, z], self.guinadaParaNave)
            a.poseAndando(t)

    # ----------------------------------------------------------------------
    def _nave(self, t):
        n = self.nave
        # reconhecimento: gira na plataforma até a escotilha apontar para o astronauta
        guinada = lerpAngulo(self.guinadaNaveInicial, self.guinadaNaveFinal,
                             suave(fase(t, 17.3, 19.8)))
        pos = [0.0, ALTURA_PLATAFORMA, 0.0]
        inclinacao = 0.0

        # rampa: abre 19.8-21.2, fecha 27.3-28.8
        n.setRampa(suave(fase(t, 19.8, 21.2)) - suave(fase(t, 27.3, 28.8)))

        # ignição: chama cresce e a nave treme
        intensidade = suave(fase(t, 28.8, 31.0))
        if 28.8 <= t < 31.0:
            pos[0] += 0.03 * sin(t * 60) * intensidade

        # decolagem/afastamento: aceleração constante para cima (y = a·t²/2),
        # depois inclina e se afasta em +x girando em torno do próprio eixo
        if t >= 31.0:
            td = t - 31.0
            pos[1] += 0.55 * td * td
            if td > 2.0:
                pos[0] += 0.12 * (td - 2.0) ** 3
                inclinacao = min(1.0, 0.22 * (td - 2.0))
            guinada += 0.12 * td * td                # rolagem em torno do próprio eixo
            intensidade = 1.0 + 0.3 * min(1.0, td / 2)

        n.setTransform(pos, guinada, inclinacao)
        n.setChama(intensidade, t)

        # luz pontual alaranjada do motor (ilumina a plataforma na ignição)
        self.luzMotor.color = [1.0 * intensidade, 0.55 * intensidade, 0.15 * intensidade]
        self.luzMotor.setPosition([pos[0], pos[1] - 0.4, pos[2]])
