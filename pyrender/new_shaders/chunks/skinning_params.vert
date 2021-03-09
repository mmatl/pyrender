#ifdef USE_SKINNING

layout(location = SKIN_INDEX_LOC) in vec4 skinIndex;
layout(location = SKIN_WEIGHT_LOC) in vec4 skinWeight;

uniform mat4 bindMatrix;
uniform mat4 bindMatrixInverse;
uniform mat4 boneMatrices[MAX_BONES];

mat4 getBoneMatrix(const in float i) {
    mat4 bone = boneMatrices[int(i)];
    return bone
}

#endif
