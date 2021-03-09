// Summary
//   - Update the object-frame normal and tangent by applying skinning matrices
// Inputs
//   - objectNormal : the object-frame normal
//   - objectTanget : the object-frame tangent
// Outputs:
//   - objectNormal : the updated object-frame normal
//   - objectTanget : the updated object-frame tangent
//
#ifdef USE_SKINNING

    mat4 skinMatrix = mat4(0.0);
    skinMatrix += skinWeight.x * boneMatX;
    skinMatrix += skinWeight.y * boneMatY;
    skinMatrix += skinWeight.z * boneMatZ;
    skinMatrix += skinWeight.w * boneMatW;
    skinMatrix = bindMatrixInverse * skinMatrix * bindMatrix;

    objectNormal = vec4(skinMatrix * vec4(objectNormal, 0.0)).xyz;

    #ifdef USE_TANGENT

        objectTangent = vec4(skinMatrix * vec4(objectTangent, 0.0)).xyz;

    #endif

#endif
