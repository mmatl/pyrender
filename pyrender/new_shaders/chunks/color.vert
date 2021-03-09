#ifdef (USE_COLOR || USE_INSTANCING_COLOR)
    outputs.vColor = vec3(1.0);
#endif
#ifdef USE_COLOR
    outputs.vColor *= vColor.xyz;
#endif
#ifdef USE_INSTANCE_COLOR
    outputs.vColor *= instanceColor.xyz;
#endif

