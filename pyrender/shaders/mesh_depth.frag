#version 330 core

out vec4 frag_color;

void main()
{
    frag_color = vec4(vec3(clamp(gl_FragDepth, 0.0, 1.0)), 1.0);
}
