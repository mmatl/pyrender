// Summary
//   - Apply skinning to object-space vertex position
// Inputs
//   - objectPos : the object-frame position
// Outputs:
//   - objectPos : the object-frame position

#ifdef USE_SKINNING

    vec4 skinVertex = bindMatrix * vec4(objectPos, 1.0);
    vec4 skinned = vec4(0.0);
    skinned += boneMatX * skinVertex * skinWeight.x;
    skinned += boneMatY * skinVertex * skinWeight.y;
    skinned += boneMatZ * skinVertex * skinWeight.z;
    skinned += boneMatW * skinVertex * skinWeight.w;
    objectPos = (bindMatrixInverse * skinned).xyz;

#endif
