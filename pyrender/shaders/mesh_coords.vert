#version 330 core

// Inputs
layout(location = 0) in vec3 position;
layout(location = NORMAL_LOC) in vec3 normal;
layout(location = INST_M_LOC) in mat4 inst_m;

// Output data
out vec3 frag_position_cam;

// Uniform data
uniform mat4 M;
uniform mat4 V;
uniform mat4 P;

// Render loop
void main() {
    frag_position_cam = vec3(V * M * inst_m * vec4(position, 1.0));
    gl_Position = P * V * M * inst_m * vec4(position, 1);
}
