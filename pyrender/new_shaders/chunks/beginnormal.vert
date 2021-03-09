// Summary
//   - Create object-space normal and tangent, and set up normal matrix
// Inputs
//   - None
// Outputs:
//   - objectNormal : the object-frame normal
//   - objectTanget : the object-frame tangent
//   - normalMatrix : the normal matrix

vec3 objectNormal = vec3(vNormal);

#ifdef USE_TANGENT
    vec3 objectTangent = vec3(vTangent.xyz);
#endif

mat3 normalMatrix = mat3(modelMatrix);

#ifdef USE_INSTANCING
normalMatrix = instanceMatrix * normalMatrix;
#endif

normalMatrix = transpose(inverse(normalMatrix));
