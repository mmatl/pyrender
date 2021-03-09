// Summary
//   - Project the object-space position into
// Inputs
//   - objectPos : the object-frame position
// Outputs:
//   - viewPos : the view-frame position
//   - worldPos : the world-frame position
//   - gl_Position : the projected position

vec4 worldPos = vec4(objectPos, 1.0);

#ifdef USE_INSTANCING

    worldPos = instanceMatrix * viewPos;

#endif

vec4 viewPos = modelViewMatrix * worldPos;
worldPos = modelMatrix * worldPos;
gl_Position = projectionMatrix * viewPos;
output.vPosition = viewPos;
