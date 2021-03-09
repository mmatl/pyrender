// Summary
//   - Apply morph to object-space vertex position
// Inputs
//   - objectPos : the object-frame position
// Outputs:
//   - objectPos : the object-frame position
//
#ifdef USE_MORPHTARGETS

    objectPos *= morphTargetBaseInfluence;
    objectPos += morphTarget0 * morphTargetInfluences[0];
    objectPos += morphTarget1 * morphTargetInfluences[1];
    objectPos += morphTarget2 * morphTargetInfluences[2];
    objectPos += morphTarget3 * morphTargetInfluences[3];

#ifndef USE_MORPHNORMALS
    objectPos += morphTarget4 * morphTargetInfluences[4];
    objectPos += morphTarget5 * morphTargetInfluences[5];
    objectPos += morphTarget6 * morphTargetInfluences[6];
    objectPos += morphTarget7 * morphTargetInfluences[7];
#endif

#endif
