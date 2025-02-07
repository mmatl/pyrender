#include <pyrender/viewer.h>

#include <SDL.h>

#include <cstdint>
#include <string>
#include <utils/EntityManager.h>
#include <filament/Camera.h>
#include <filament/Engine.h>
#include <filament/Renderer.h>
#include <filament/RenderableManager.h>
#include <filament/Scene.h>
#include <filament/SwapChain.h>
#include <filament/View.h>
#include <filament/Viewport.h>

using utils::EntityManager;
using utils::Entity;
using filament::RenderableManager;
using filament::Engine;
using filament::SwapChain;
using filament::Renderer;
using filament::Camera;
using filament::View;
using filament::Scene;
using filament::Material;
using filament::MaterialInstance;

namespace pyrender {

Viewer::Viewer(const std::string& title, size_t width, size_t height)
  : mTitle(title)
  , mWidth(width)
  , mHeight(height) {
}

Viewer::~Viewer() {}

void Viewer::run() {
  const int x = SDL_WINDOWPOS_CENTERED;
  const int y = SDL_WINDOWPOS_CENTERED;
  uint32_t flags = SDL_WINDOW_SHOWN | SDL_WINDOW_ALLOW_HIGHDPI | SDL_WINDOW_RESIZABLE;
  auto window = SDL_CreateWindow(mTitle.c_str(), x, y, static_cast<int>(mWidth), static_cast<int>(mHeight), flags);

  void* nativeWindow = getNativeWindow(window);

  Engine* engine = Engine::create();
  SwapChain* swapChain = engine->createSwapChain(nativeWindow);
  Renderer* renderer = engine->createRenderer();
  Camera* camera = engine->createCamera(EntityManager::get().create());
  View* view = engine->createView();
  Scene* scene = engine->createScene();

  view->setCamera(camera);
  view->setScene(scene);

  Entity renderable = EntityManager::get().create();
  // build a quad
  auto vb = VertexBuffer::Builder()
    .vertexCount(3)
    .bufferCount(1)
    .attribute(VertexAttribute::POSITION, 0, VertexBuffer::AttributeType::FLOAT2, 0, 12)

  RenderableManager::Builder(1)
          .boundingBox({{ -1, -1, -1 }, { 1, 1, 1 }})
          .geometry(0, RenderableManager::PrimitiveType::TRIANGLES, vertexBuffer, indexBuffer, 0, 6)
          .culling(false)
          .build(*engine, renderable);
  scene->addEntity(renderable);
  // Material* material = Material::Builder()
  //       .package((void*) BAKED_MATERIAL_PACKAGE, sizeof(BAKED_MATERIAL_PACKAGE))
  //       .build(*engine);
  // MaterialInstance* materialInstance = material->createInstance();
  // beginFrame() returns false if we need to skip a frame
  if (renderer->beginFrame(swapChain)) {
      // for each View
      renderer->render(view);
      renderer->endFrame();
  }
}

} // namespace pyrender
