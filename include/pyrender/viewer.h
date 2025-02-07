#ifndef PYRENDER_VIEWER_H
#define PYRENDER_VIEWER_H

struct SDL_Window;

extern "C" void* getNativeWindow(SDL_Window* sdlWindow);

#if defined(__APPLE__)
// Add a backing CAMetalLayer to the NSView and return the layer.
extern "C" void* setUpMetalLayer(void* nativeWindow);
// Setup the window the way Filament expects (color space, etc.).
extern "C" void prepareNativeWindow(SDL_Window* sdlWindow);
// Resize the backing CAMetalLayer's drawable to match the new view's size. Returns the layer.
extern "C" void* resizeMetalLayer(void* nativeView);
#endif

#include <SDL.h>
#include <filament/Engine.h>
#include <filament/Viewport.h>
#include <filament/Renderer.h>
#include <filament/SwapChain.h>

#include <string>

namespace pyrender {

class Viewer {
 public:
  Viewer(const std::string& title, size_t width, size_t height);
  ~Viewer();
  void run();
 private:
  size_t mWidth { 0 };
  size_t mHeight { 0 };
  const std::string mTitle;
  SDL_Window* mWindow { nullptr };
  filament::Renderer* mRenderer { nullptr };
  filament::Engine::Backend mBackend;
  filament::SwapChain* mSwapChain { nullptr };
};

} // namespace pyrender


#endif  // PYRENDER_VIEWER_H
