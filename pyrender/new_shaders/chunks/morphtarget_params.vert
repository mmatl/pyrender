#ifdef USE_MORPHTARGETS
layout(location = MORPHTARGET_0_LOC) in vec3 morphTarget0;
layout(location = MORPHTARGET_1_LOC) in vec3 morphTarget1;
layout(location = MORPHTARGET_2_LOC) in vec3 morphTarget2;
layout(location = MORPHTARGET_3_LOC) in vec3 morphTarget3;
layout(location = MORPHTARGET_4_LOC) in vec3 morphTarget4;
layout(location = MORPHTARGET_5_LOC) in vec3 morphTarget5;
layout(location = MORPHTARGET_6_LOC) in vec3 morphTarget6;
layout(location = MORPHTARGET_7_LOC) in vec3 morphTarget7;

uniform float morphTargetBaseInfluence;
#ifndef USE_MORPHNORMALS
uniform float morphTargetInfluences[8];
#else
uniform float morphTargetInfluences[4];
#endif

#endif
