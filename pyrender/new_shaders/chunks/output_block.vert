out VertexOutputs {
    vec3 vPosition;
    vec3 vNormal;

#ifdef USE_TANGENT
    vec3 vTangent;
    vec3 vBitangent;
#endif

#ifdef USE_UV
    vec2 vUV;
#endif

#ifdef USE_UV2
    vec2 vUV2;
#endif

#ifdef (USE_COLOR || USE_INSTANCING_COLOR)
    vec3 vColor;
#endif

} outputs;
