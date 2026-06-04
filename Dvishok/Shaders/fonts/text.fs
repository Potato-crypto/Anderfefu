#version 330 core

in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D text;
uniform vec4 textColor;

void main()
{
    float alpha = texture(text, TexCoord).r;
    FragColor = vec4(textColor.rgb, alpha * textColor.a);

    if(FragColor.a < 0.01)
        discard;
}