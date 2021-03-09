#ifdef USE_INSTANCING
layout(location = INSTANCE_MATRIX_LOC) in mat4 instanceMatrix;

#ifdef USE_INSTANCE_COLOR
layout(location = INSTANCE_COLOR) in mat4 instanceColor;
#endif

#endif
