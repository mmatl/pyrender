// Summary
//   - Update the object-frame normal and tangent by applying skinning matrices
// Inputs
//   - None
// Outputs:
//   - boneMatX : the first bone matrix
//   - boneMatY : the first bone matrix
//   - boneMatZ : the first bone matrix
//   - boneMatW : the first bone matrix
//
#ifdef USE_SKINNING

    mat4 boneMatX = getBoneMatrix(skinIndex.x);
    mat4 boneMatY = getBoneMatrix(skinIndex.y);
    mat4 boneMatZ = getBoneMatrix(skinIndex.z);
    mat4 boneMatW = getBoneMatrix(skinIndex.w);

#endif
