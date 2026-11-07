# Fonte: Stemkoski & Pascale (2022), seção 6.9.2
from material.material import Material


class DepthMaterial(Material):
    """Usado só na passada de sombra: pinta cada pixel com sua profundidade
    (0 = perto da luz / preto, 1 = longe / branco)."""

    def __init__(self):
        vertexShaderCode = """
        in vec3 vertexPosition;
        uniform mat4 projectionMatrix;
        uniform mat4 viewMatrix;
        uniform mat4 modelMatrix;
        void main()
        {
            gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1);
        }
        """
        fragmentShaderCode = """
        out vec4 fragColor;
        void main()
        {
            float z = gl_FragCoord.z;
            fragColor = vec4(z, z, z, 1);
        }
        """
        super().__init__(vertexShaderCode, fragmentShaderCode)
        self.locateUniforms()
