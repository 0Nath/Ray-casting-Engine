# Ray-casting-Engine
A python implementation of a DOOM-like ray-casting engine
---
## Usage
To be launched, the engine need a map and a textures dic.
Those variables can be generated like this:
```
from raycasting import Engine, load_map, generate_textures
map = load_map("map/map.txt")
textures = generate_textures( { 1: "textures/brick.bmp" , 2: "textures/test.bmp" , 3: "textures/brick3.bmp" , 4: "textures/brick2.png" , 5: (100,100,0) } )
```
with a map looking like [this](map/map.txt), where each number will be associated with a texture in the dictionnary.

The Engine class can then be launched like this:
```
Engine((1080,720),1080,map,textures,30)
```
taking in arguments a tuple of resolution, a number of ray to be casted should be equal to horizontal resolution to better result, but can be less ( but not more ), a map and textures (see above) and a max framerate.

## Controls

You can use ZQSD and space to move, m for the mini map.
