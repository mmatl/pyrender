#version 330 core

out vec4 frag_color;

in vec3 frag_position_cam;

void main()
{
    frag_color = vec4(frag_position_cam, 1.0);
}
