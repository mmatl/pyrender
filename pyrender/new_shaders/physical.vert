#include <common>

// Standard Uniforms
#include <uniforms>

// Inputs
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
#include <uv_params>
#include <color_params>
#include <tangent_params>
#include <morphtarget_params>
#include <skinning_params>
#include <instancing_params>
#include <displacement_params>

// Outputs
#include <output_block>

void main() {

    // Parse uv and color data
    #include <uv>
    #include <color>

    // Compute normal, tangent, and bitangent
    #include <beginnormal>
    #include <morphnormal>
    #include <skinbase>
    #include <skinnormal>
    #include <defaultnormal>

    // Compute position
    #include <beginvertex>
    #include <morphvertex>
    #include <skinvertex>
    #include <displacevertex>
    #include <project>
}
