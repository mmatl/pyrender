// Summary
//   - Update the object normals using morph targets
// Inputs
//   - objectNormal : the object-frame normal
// Outputs:
//   - objectNormal : the updated object-frame normal
//
#ifdef USE_MORPHNORMALS

objectNormal *= morphTargetBaseInfluence
objectNormal += morphTarget4 * morphTargetInfluences[0];
objectNormal += morphTarget5 * morphTargetInfluences[1];
objectNormal += morphTarget6 * morphTargetInfluences[2];
objectNormal += morphTarget7 * morphTargetInfluences[3];

#endif
