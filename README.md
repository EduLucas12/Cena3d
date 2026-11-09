# Cena3d — Base 6-19: Nave Espacial e Astronauta

Trabalho Prático de **Computação Gráfica** — UNIPAC, 2026/02
Aplicação 3D interativa em **Python + Pygame + PyOpenGL**, construída sobre o framework do livro
*Developing Graphics Frameworks with Python and OpenGL* (Stemkoski & Pascale, 2022).

---

## 1. Identificação

| | |
|---|---|
| **Integrante** | Lucas Eduardo Silva (trabalho individual) |
| **Tema 6** | Nave espacial — missão de exploração; desloca-se e altera a orientação para encontrar o segundo elemento (aproximação, reconhecimento e afastamento) |
| **Tema 19** | Astronauta estilizado — missão de reconhecimento; desloca-se e movimenta um braço para sinalizar/responder ao segundo elemento |

## 2. Descrição da cena e da interação

A cena se passa numa **base de lançamento** ao entardecer: pátio de concreto, plataforma
circular "BASE 6-19", torre de comando com cabine, porta e elevador externo, tanques de
combustível, cones de sinalização e céu estrelado.

A interação é uma sequência encadeada (~39 s), em que cada ação só começa quando a anterior termina:

| Tempo (s) | Fase |
|---|---|
| 0,0 – 1,5 | Base em espera; a nave está parada na plataforma, com a escotilha virada para o lado oposto ao da torre |
| 1,5 – 2,5 | A porta da cabine abre (rotação em torno da dobradiça) |
| 2,5 – 4,0 | O astronauta sai da cabine andando até o elevador |
| 4,0 – 8,8 | Ele vira para o público e desce junto com o elevador |
| 8,8 – 13,8 | Caminha até a frente da cena e vira para o público (câmera) |
| 13,8 – 17,3 | **Dá tchau para o público** (ombro ergue o braço, cotovelo balança) |
| 17,3 – 19,8 | **Reconhecimento:** a nave gira na plataforma até a escotilha apontar para o astronauta |
| 19,8 – 21,2 | A rampa da nave abre |
| 21,2 – 22,6 | **O astronauta responde** apontando para a nave |
| 22,6 – 27,3 | Caminha até a rampa, sobe e embarca |
| 27,3 – 28,8 | A rampa fecha |
| 28,8 – 31,0 | Ignição: a chama cresce, a nave treme e a luz do motor ilumina a plataforma |
| 31,0 – 39,0 | **Decolagem e afastamento:** sobe acelerando, inclina, gira em torno do próprio eixo e some no céu |

## 3. Instalação e execução

Requisitos: Python 3.9 ou superior e placa de vídeo/driver com **OpenGL 3.3**.
Testado com Python 3.13.18, pygame 2.6.1, PyOpenGL 3.1.10 e NumPy 2.5.3.

```bash
pip install -r requirements.txt
python cena.py
```

Arquivos auxiliares:
- `teste_framework.py`: cena mínima para conferir se o framework (luz, textura e sombra) funciona na máquina.
- `gerar_texturas.py`: regenera as imagens da pasta `images/`. **Não é preciso rodar**, porque as imagens já estão no repositório.

## 4. Controles

| Tecla | Ação |
|---|---|
| **W / S** | câmera para frente / para trás |
| **A / D** | câmera para a esquerda / direita |
| **R / F** | câmera sobe / desce |
| **Q / E** | gira a câmera para a esquerda / direita |
| **T / G** | olha para cima / para baixo |
| **P** | pausa / continua a animação (a câmera continua funcionando) |
| **C** | alterna entre a câmera livre e a câmera automática (que acompanha a ação) |
| **Enter** | reinicia a animação |

O título da janela mostra a fase atual, o tempo da animação e se está pausado.

## 5. Onde está cada recurso gráfico

| Requisito | Arquivo / classe / função |
|---|---|
| Janela, laço principal, `deltaTime` | `core/base.py` (`Base.run`) |
| Teclado | `core/input.py` (`Input`); controle de câmera em `extras/movementRig.py` (`MovementRig`) |
| Compilação de shaders | `core/openGLUtils.py` (`initializeShader`, `initializeProgram`) |
| **Atributos de vértice** (VBO) | `core/attribute.py` (`Attribute`); dados criados em `geometry/*.py` |
| **Uniforms** | `core/uniform.py` (`Uniform`: int, float, vec3, mat4, sampler2D, structs `Light` e `Shadow`) |
| Matrizes (translação, rotação, escala, perspectiva, ortográfica, lookAt) | `core/matrix.py` (`Matrix`) |
| **Grafo de cena / hierarquia** | `core/object3D.py` (`getWorldMatrix`), `core/group.py`, `core/mesh.py` |
| Modelo da nave | `modelos/nave.py` (`Nave`; `setTransform`, `setRampa`, `setChama`) |
| Modelo do astronauta | `modelos/astronauta.py` (`Astronauta`; `setPose`, `poseAndando`, `poseAceno`, `poseSinal`) |
| Ambiente | `modelos/cenario.py` (`criarCenario`) |
| **Animação por tempo + interação** | `animacao.py` (`FASES`, `fase`, `suave`, `Sequencia.aplicar`) |
| **Pausa** e câmeras | `cena.py` (`Cena.update`, `tAnim`, `pausado`, `alvoCameraAuto`) |
| Câmera em perspectiva | `core/camera.py` (`Camera`, `Matrix.makePerspective`) |
| **Texturas e coordenadas UV** | `core/texture.py` (`Texture`); UV em `geometry/*.py`; `repeatUV` em `material/phongMaterial.py` e `material/textureMaterial.py` |
| **Iluminação** (ambiente, direcional, pontual) | `light/*.py`; cálculo em `material/phongMaterial.py` (função GLSL `lightCalc`) |
| **Normais** | `geometry/parametricGeometry.py` (`calcNormal`), `boxGeometry.py`, `polygonGeometry.py` |
| Materiais | `material/phongMaterial.py` (difusa + especular), `material/lambertMaterial.py` (fosco), `material/surfaceMaterial.py` (sem luz: chama) |
| **Sombras (shadow mapping, seção 6.9)** | `light/shadow.py` (`Shadow`), `material/depthMaterial.py`, `core/renderTarget.py`, passada de sombra em `core/renderer.py` (`render`) e teste de sombra no fragment shader de `phongMaterial.py` |

### Transformações utilizadas
- **Translação:** caminhada do astronauta, descida do elevador, subida da nave.
- **Rotação:** porta (Y, na dobradiça), giro da nave para encontrar o astronauta (Y), inclinação na decolagem (Z), rampa (X), articulações do astronauta (X e Z).
- **Escala:** astronauta (`ESCALA = 0.75` no nó raiz) e chama do motor (cresce e tremula).
- **Hierárquicas:**
  - astronauta: `raiz → ombro → braço → cotovelo → antebraço → luva`, e `raiz → quadril → perna → bota`;
  - nave: `raiz → rampaPivo → rampa`, `raiz → suporte → aleta`, `raiz → chama`;
  - torre: `torre → portaPivo → porta` e `torre → elevador → piso/corrimão`.

### Shaders, atributos e uniforms (material principal: `PhongMaterial`)
- **Atributos** (por vértice): `vertexPosition` (vec3), `vertexUV` (vec2), `vertexNormal` (vec3).
- **Uniforms** (iguais para todo o objeto):
  - `modelMatrix`, `viewMatrix`, `projectionMatrix`;
  - `light0..light3` (struct `Light`);
  - `viewPosition`, `baseColor`, `useTexture`, `textureSampler`, `repeatUV`, `specularStrength`, `shininess`;
  - `useShadow` e `shadow0` (struct `Shadow`).
- **Vertex shader:** calcula `gl_Position = projection · view · model · posição`. Envia ao fragment shader a posição e a normal no mundo, a UV e a posição do vértice vista pela câmera da luz.
- **Fragment shader:**
  1. cor base × textura;
  2. soma das luzes (ambiente + difusa `max(dot(N, −L), 0)` + especular `pow(max(dot(V, R), 0), shininess)`);
  3. teste de sombra: se a profundidade do fragmento vista pela luz for maior que a gravada no mapa (+ `bias`), o fragmento é escurecido por `strength`.
- **Sombreamento × sombra projetada:** o lado escuro de um objeto vem da normal (`lightCalc`). A sombra no chão vem do mapa de profundidade, gerado numa passada extra do ponto de vista da luz com câmera ortográfica.

## 6. Adaptações em relação ao livro

Todas estão marcadas no código com o comentário `# ADAPTAÇÃO`:
- `numpy.itemset` (removido no NumPy 2) trocado por indexação, em `Object3D.setPosition`.
- `texture2D` trocado por `texture()`, porque não existe no perfil core do GLSL 330. Por isso o sampler passou a se chamar `textureSampler`.
- `pygame.image.tostring` (obsoleto) trocado por `tobytes`.
- Proteção contra normal nula (NaN) na ponta do cone, em `ParametricGeometry`.
- O renderer restaura a cor de fundo e o framebuffer da janela depois da passada de sombra.
- **Mapa de sombra em ponto flutuante (`GL_R32F`)**, no lugar da textura RGBA de 8 bits do livro, e limiar `facingLight` 0,15. Isso elimina a *shadow acne* (listras) nas superfícies curvas.
- `castShadow = False` para objetos que não devem projetar sombra (céu e chama).
- `LambertMaterial` herda de `PhongMaterial` com `specularStrength = 0`, para não duplicar o shader.
- Pedido explícito de contexto OpenGL 3.3 core em `Base`.

## 7. Contribuições individuais

Trabalho realizado individualmente por **Lucas Eduardo Silva**: definição da cena e da
interação, modelagem da nave, do astronauta e do cenário, animação, controles, texturas,
iluminação, sombras, testes e documentação (com apoio de IA, conforme a seção 9).

## 8. Fontes consultadas

- STEMKOSKI, Lee; PASCALE, Michael. *Developing Graphics Frameworks with Python and OpenGL*. Boca Raton: CRC Press, 2022. Caps. 2 a 6, em especial 4 (grafo de cena e geometrias), 5.1–5.3 (texturas), 5.7–5.8 (lookAt, câmera ortográfica e render target), 6 (iluminação) e 6.9 (shadow mapping). Cada arquivo do framework indica no cabeçalho a seção de origem.
- Documentação do Pygame: https://www.pygame.org/docs/
- Documentação do PyOpenGL: https://pyopengl.sourceforge.net/documentation/
- **Texturas:** todas as imagens da pasta `images/` (`concreto.png`, `plataforma.png`, `metal.png`, `ceu.png`) foram **geradas pelo script próprio `gerar_texturas.py`**. Nenhuma imagem externa foi utilizada.

## 9. Declaração de uso de Inteligência Artificial

- **Ferramenta:** Claude (Anthropic).
- **Finalidade:** apoio na leitura do enunciado e do livro, transcrição e adaptação do framework do livro para as versões atuais das bibliotecas, sugestão da estrutura da cena e da sequência de animação, geração de rascunhos de código, testes e redação desta documentação.
- **Trechos desenvolvidos ou revisados com apoio da IA:**
  - transcrição/adaptação das classes do framework (`core/`, `geometry/`, `material/`, `light/`, `extras/`) e as correções marcadas como `# ADAPTAÇÃO`;
  - `modelos/cenario.py`, `modelos/nave.py`, `modelos/astronauta.py`, `animacao.py`, `cena.py`, `gerar_texturas.py`, `teste_framework.py` e este README.
- O código foi revisado, executado e testado pelo autor, que é responsável por explicar seu funcionamento na apresentação.

## 10. Estrutura do projeto

```
Cena3d/
├── cena.py              # programa principal (janela, câmeras, luzes, sombra, pausa)
├── animacao.py          # linha do tempo e interação entre nave e astronauta
├── modelos/
│   ├── cenario.py       # base de lançamento, torre, elevador, céu
│   ├── nave.py          # modelo da nave (tema 6)
│   └── astronauta.py    # modelo do astronauta (tema 19)
├── core/                # framework: base, input, attribute, uniform, matrix, object3D, camera, mesh, renderer, texture, renderTarget
├── geometry/            # retângulo, caixa, polígono, paramétrica, esfera, elipsoide, cilindro, cone, plano
├── material/            # basic, surface, texture, phong, lambert, depth
├── light/               # ambient, directional, point, shadow
├── extras/              # movementRig (câmera pelo teclado)
├── images/              # texturas geradas por gerar_texturas.py
├── gerar_texturas.py
├── teste_framework.py
└── requirements.txt
```
