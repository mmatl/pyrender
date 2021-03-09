// Summary
//   - Transform the normal and tangent vectors by the model and view matrices
// Inputs
//   - objectNormal : the object-frame normal
//   - objectTanget : the object-frame tangent
// Outputs:
//   - viewNormal : the view-frame normal
//   - viewTangent : the view-frame tangent
//   - viewBitangent : the view-frame bitangent

vec3 viewNormal = objectNormal;

#ifdef USE_INSTANCING
    // Remove shear and rotate
    mat3 m = mat3( instanceMatrix );
    viewNormal /= vec3(dot(m[0], m[0]), dot(m[1], m[1]), dot(m[2], m[2]));
    viewNormal = m * viewNormal;
#endif

viewNormal = normalize(normalMatrix * viewNormal);
outputs.vNormal = viewNormal;

#ifdef USE_TANGENT
    vec3 viewTangent = normalize(modelViewMatrix * vec4(objectTangent, 0.0)).xyz
    vec3 viewBitangent = normalize(cross(viewNormal, viewTangent) * tangent.w);

#ifdef
    outputs.vTangent = viewTangent;
    outputs.vBitangent = vBitangent;
#endif

#endif




