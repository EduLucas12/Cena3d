# Fonte: Stemkoski & Pascale (2022), seções 6.4.2 (Phong) e 6.9.2 (sombras)
from material.material import Material
from OpenGL.GL import *


class PhongMaterial(Material):
    """Material sensível à luz: ambiente + difusa + especular (modelo de Phong),
    com textura opcional e sombra opcional (shadow mapping).

    Atributos usados : vertexPosition, vertexUV, vertexNormal
    Uniforms         : model/view/projectionMatrix, light0..light3, viewPosition,
                       baseColor, useTexture, textureSampler, specularStrength,
                       shininess, useShadow, shadow0, repeatUV
    """

    def __init__(self, texture=None, properties={}, useShadow=False):

        vertexShaderCode = """
        uniform mat4 projectionMatrix;
        uniform mat4 viewMatrix;
        uniform mat4 modelMatrix;
        uniform vec2 repeatUV;
        in vec3 vertexPosition;
        in vec2 vertexUV;
        in vec3 vertexNormal;
        out vec3 position;
        out vec2 UV;
        out vec3 normal;

        struct Shadow
        {
            vec3 lightDirection;       // direção da luz que projeta a sombra
            mat4 projectionMatrix;     // câmera da sombra (ortográfica)
            mat4 viewMatrix;
            sampler2D depthTexture;    // mapa de profundidade
            float strength;            // quanto escurece
            float bias;                // evita "acne" de sombra
        };
        uniform bool useShadow;
        uniform Shadow shadow0;
        out vec3 shadowPosition0;

        void main()
        {
            gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1);
            // posição e normal no espaço do mundo (vão para o fragment shader)
            position = vec3(modelMatrix * vec4(vertexPosition, 1));
            UV = vertexUV * repeatUV;
            normal = normalize(mat3(modelMatrix) * vertexNormal);
            // posição do vértice vista pela câmera da luz
            if (useShadow)
            {
                vec4 temp0 = shadow0.projectionMatrix * shadow0.viewMatrix *
                             modelMatrix * vec4(vertexPosition, 1);
                shadowPosition0 = vec3(temp0);
            }
        }
        """

        fragmentShaderCode = """
        struct Light
        {
            int lightType;      // 1 = ambiente, 2 = direcional, 3 = pontual
            vec3 color;
            vec3 direction;
            vec3 position;
            vec3 attenuation;
        };
        uniform Light light0;
        uniform Light light1;
        uniform Light light2;
        uniform Light light3;

        uniform vec3 viewPosition;
        uniform float specularStrength;
        uniform float shininess;

        vec3 lightCalc(Light light, vec3 pointPosition, vec3 pointNormal)
        {
            float ambient = 0;
            float diffuse = 0;
            float specular = 0;
            float attenuation = 1;
            vec3 lightDirection = vec3(0, 0, 0);

            if (light.lightType == 1)            // luz ambiente
            {
                ambient = 1;
            }
            else if (light.lightType == 2)       // luz direcional
            {
                lightDirection = normalize(light.direction);
            }
            else if (light.lightType == 3)       // luz pontual
            {
                lightDirection = normalize(pointPosition - light.position);
                float distance = length(light.position - pointPosition);
                attenuation = 1.0 / (light.attenuation[0]
                                   + light.attenuation[1] * distance
                                   + light.attenuation[2] * distance * distance);
            }

            if (light.lightType > 1)
            {
                pointNormal = normalize(pointNormal);
                // difusa (Lambert): cosseno entre normal e luz = produto escalar
                diffuse = max(dot(pointNormal, -lightDirection), 0.0);
                diffuse *= attenuation;
                // especular (Phong): reflexo da luz comparado com a direção do olho
                if (diffuse > 0)
                {
                    vec3 viewDirection = normalize(viewPosition - pointPosition);
                    vec3 reflectDirection = reflect(lightDirection, pointNormal);
                    specular = max(dot(viewDirection, reflectDirection), 0.0);
                    specular = specularStrength * pow(specular, shininess);
                }
            }
            return light.color * (ambient + diffuse + specular);
        }

        uniform vec3 baseColor;
        uniform bool useTexture;
        uniform sampler2D textureSampler;

        struct Shadow
        {
            vec3 lightDirection;
            mat4 projectionMatrix;
            mat4 viewMatrix;
            sampler2D depthTexture;
            float strength;
            float bias;
        };
        uniform bool useShadow;
        uniform Shadow shadow0;
        in vec3 shadowPosition0;

        in vec3 position;
        in vec2 UV;
        in vec3 normal;
        out vec4 fragColor;

        void main()
        {
            vec4 color = vec4(baseColor, 1.0);
            if (useTexture)
                color *= texture(textureSampler, UV);   // ADAPTAÇÃO: texture2D -> texture

            // SOMBREAMENTO: efeito das luzes na própria superfície
            vec3 total = vec3(0, 0, 0);
            total += lightCalc(light0, position, normal);
            total += lightCalc(light1, position, normal);
            total += lightCalc(light2, position, normal);
            total += lightCalc(light3, position, normal);
            color *= vec4(total, 1);

            // SOMBRA PROJETADA: outro objeto está entre este ponto e a luz?
            if (useShadow)
            {
                // a superfície está virada para a luz?
                float cosAngle = dot(normalize(normal), -normalize(shadow0.lightDirection));
                bool facingLight = (cosAngle > 0.01);
                // converte de [-1, 1] (clip space) para [0, 1] (UV e profundidade)
                vec3 shadowCoord = (shadowPosition0.xyz + 1.0) / 2.0;
                float closestDistanceToLight = texture(shadow0.depthTexture, shadowCoord.xy).r;
                float fragmentDistanceToLight = clamp(shadowCoord.z, 0, 1);
                bool inShadow = (fragmentDistanceToLight > closestDistanceToLight + shadow0.bias);
                if (facingLight && inShadow)
                {
                    float s = 1.0 - shadow0.strength;
                    color *= vec4(s, s, s, 1);
                }
            }
            fragColor = color;
        }
        """

        super().__init__(vertexShaderCode, fragmentShaderCode)
        self.addUniform("vec3", "baseColor", [1.0, 1.0, 1.0])
        self.addUniform("Light", "light0", None)
        self.addUniform("Light", "light1", None)
        self.addUniform("Light", "light2", None)
        self.addUniform("Light", "light3", None)
        self.addUniform("vec3", "viewPosition", [0, 0, 0])
        self.addUniform("float", "specularStrength", 1)
        self.addUniform("float", "shininess", 32)
        # ADAPTAÇÃO: repetição da textura (como no TextureMaterial)
        self.addUniform("vec2", "repeatUV", [1.0, 1.0])
        if texture is None:
            self.addUniform("bool", "useTexture", False)
        else:
            self.addUniform("bool", "useTexture", True)
            self.addUniform("sampler2D", "textureSampler", [texture.textureRef, 1])
        if not useShadow:
            self.addUniform("bool", "useShadow", False)
        else:
            self.addUniform("bool", "useShadow", True)
            self.addUniform("Shadow", "shadow0", None)
        self.locateUniforms()

        self.settings["doubleSide"] = True
        self.settings["wireframe"] = False
        self.settings["lineWidth"] = 1
        self.setProperties(properties)

    def updateRenderSettings(self):
        if self.settings["doubleSide"]:
            glDisable(GL_CULL_FACE)
        else:
            glEnable(GL_CULL_FACE)
        if self.settings["wireframe"]:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glLineWidth(self.settings["lineWidth"])
