#version 330 core

// Vertex Attributes
layout(location = 0) in vec3 position;
layout(location = INST_M_LOC) in mat4 inst_m;

// Uniforms
uniform mat4 M;
uniform mat4 V;
uniform mat4 P;

void main()
{
    gl_Position = P * V * M * inst_m * vec4(position, 1);
}

