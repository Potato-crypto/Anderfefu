#version 330 core

in vec4 ourColor;
in vec2 TexCoord;

out vec4 FragColor;

uniform sampler2D texture1;
uniform bool useTexture;

void main()
{
    if(useTexture)
    {
        vec4 tex = texture(texture1, TexCoord);
        FragColor = tex * ourColor;
    }
    else
    {
        FragColor = ourColor;
    }
}