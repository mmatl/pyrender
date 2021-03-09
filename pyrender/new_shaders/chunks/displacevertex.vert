// Summary
//   - Apply displacement map to object-space vertex position
// Inputs
//   - objectPos : the object-frame position
// Outputs:
//   - objectPos : the object-frame position

#ifdef USE_DISPLACEMENT_MAP

    objectPos += (
        normalize(objectNormal) *
        (texture2D(displacementMap, vUV).x * displacementScale + displacementBias
    );

#endif
