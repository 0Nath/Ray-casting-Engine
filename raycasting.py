import pygame
from math import cos,sin,radians,sqrt,floor,inf
import numpy as np




class Engine:
    def __init__(self,dimensions: tuple[int,int],rendering_resolution:int ,map: list[int], textures: dict,fps: int = 50 ,render_distance: int = 100,FOV: int  = 80):

        if dimensions[0] < 0 or dimensions[1] < 0 :
            raise ValueError("Invalid dimensions")
        if rendering_resolution < 1 or rendering_resolution > dimensions[0]:
            raise ValueError("Invalid rendering resolution (Should be between 1 and the horizontal resolution).")
        pygame.init()
        self.__dimensions = dimensions
        self.__rendering_resolution = rendering_resolution
        self.__fps = fps
        self.__screen = pygame.display.set_mode(self.__dimensions, pygame.RESIZABLE)
        pygame.display.set_caption("Raycasting Engine")
        self.__clock = pygame.time.Clock()

        self.__font = pygame.font.SysFont("consolas", 40)

        self.__end = False
        self.__focal_lenght = round(dimensions[0]/6.4)
        self.__map = map

        self.__position = [2,2]
        self.__rotation = 0
        self.__FOV = radians(FOV)
        self.__walls_size = 5
        self.__render_distance = render_distance
        self.__ground_color = (100,100,100)
        self.__textures = textures
        self.__v_speed = 0
        self.__v_position = 0
        self.__jump_height = 1

        self.__minimap = False

        while not self.__end:


            self.__handle_events__()
            self.__screen.fill((0, 0, 0))

            self.__draw_ground__()
            self.__renderv2__()

            if self.__minimap:
                self.__draw_minimap__(5)

            pygame.display.flip()

            self.__clock.tick(fps)

    def __draw_minimap__(self, scale=20):
        for y, row in enumerate(self.__map):
            for x, cell in enumerate(row):
                color = (200, 200, 200) if cell != 0 else (50, 50, 50)
                pygame.draw.rect(self.__screen,color,(x * scale, y * scale, scale, scale))
        px, py = self.__position
        pygame.draw.circle(self.__screen,(0, 255, 0),(int(px * scale), int(py * scale)),max(3, scale // 3))

        for line in self.__create_lines__():
            p1, v1 = line
            touching = False
            min = 1

            wall = self.__check_grid__( p1, v1)
            if wall != 0:
                vector_walls = self.__determine_walls__(wall[0],wall[1])
                for position,p2, v2 in vector_walls:

                    result ,part_of_wall,temp = self.__intersection__(p1, v1, p2, v2)

                    if result != 0:
                        touching = True
                        if result<min:
                            min = result
                if touching:
                    len_v = sqrt(v1[0]**2+v1[1]**2)
                    modifier = min

                    pygame.draw.line(
                        self.__screen,
                        (255, 0,0),
                        (p1[0] * scale, p1[1] * scale),
                        ((p1[0]+v1[0]*modifier)*scale, (p1[1]+v1[1]*modifier)*scale),
                        1
                    )

            else:

                pygame.draw.line(
                    self.__screen,
                    (255, 255,255),
                    (p1[0] * scale, p1[1] * scale),
                    ((p1[0]+v1[0])*scale, (p1[1]+v1[1])*scale),
                    1
                )

    def __renderv2__(self):
        rect_width = self.__dimensions[0] / self.__rendering_resolution

        for i,line in enumerate(self.__create_lines__()):
            p1, v1 = line
            touching = False
            minimum_result = 1

            wall = self.__check_grid__( p1, v1)

            if wall != 0:
                vector_walls = self.__determine_walls__(wall[0],wall[1])
                for position,p2, v2 in vector_walls:

                    result ,temp_part_of_wall,temp_dot_product = self.__intersection__(p1, v1, p2, v2)

                    if result != 0 :
                        touching = True
                        if result<minimum_result:
                            minimum_result = result
                            dot_product = abs(temp_dot_product/100)
                            part_of_wall = temp_part_of_wall
                            xy_coord_of_touched_wall = position
                if touching:


                    x = (p1[0] + v1[0])
                    x -= self.__position[0]
                    y = (p1[1] + v1[1])
                    y -= self.__position[1]
                    x *= minimum_result
                    y *= minimum_result

                    modifier = dot_product * (1 - (minimum_result * 0.3))
                    image = self.__textures[self.__map[xy_coord_of_touched_wall[0]][xy_coord_of_touched_wall[1]]]
                    distance = sqrt(x ** 2 + y ** 2)
                    distance = max(0.1,distance)


                    rect_height = self.__determine_size__(self.__walls_size, distance)
                    rect_x = round((i) * rect_width)
                    rect_y = self.__dimensions[1] // 2 - rect_height // 2

                    if type(image) == tuple:

                        r, g, b = image

                        r *= modifier
                        g *= modifier
                        b *= modifier
                        pygame.draw.rect(self.__screen, (round(r), round(g), round(b)),
                                         (rect_x, rect_y + (self.__v_position * self.__dimensions[1]) , rect_width + 1, rect_height))



                    else:
                        taille = int(rect_height)

                        if taille>self.__dimensions[0]:
                            largeur, hauteur = image.get_size()
                            part_out = ((taille - self.__dimensions[0])/taille)*largeur
                            image = image.subsurface(0, part_out/2, largeur,hauteur-part_out/2)


                        taille = int(rect_height)



                        largeur, hauteur = image.get_size()
                        image_offset = largeur*(1-part_of_wall)
                        if image_offset + rect_width < largeur:
                            image = image.subsurface(image_offset, 0, rect_width, hauteur)
                        else:
                            image = image.subsurface(largeur-rect_width, 0, rect_width, hauteur)

                        image = pygame.transform.scale(image, (rect_width,taille))

                        colonne = image
                        colonne.fill(
                            (modifier * 255, modifier * 255, modifier * 255),
                            special_flags=pygame.BLEND_RGB_MULT
                        )
                        self.__screen.blit(colonne, (rect_x, rect_y + (self.__v_position * self.__dimensions[1])))



        text = self.__font.render(str(round(self.__clock.get_fps())) + " FPS", True, (255,255,255))
        self.__screen.blit(text, (10, 10))

    def __draw_ground__(self):
        pygame.draw.rect(self.__screen,self.__ground_color,(0,(self.__dimensions[1]//2) + (self.__v_position * self.__dimensions[1]) ,self.__dimensions[0],self.__dimensions[1]//2))

    def __handle_events__(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__end = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.__minimap = (self.__minimap == False)



        fps = self.__clock.get_fps()
        if fps and self.__v_position >= 0:
            self.__v_position += self.__v_speed / fps
            self.__v_speed -= 9.81/ fps
        if self.__v_position <= 0:
            self.__v_position = 0
            self.__v_speed = 0



        keys = pygame.key.get_pressed()

        if  keys[pygame.K_SPACE] and self.__v_speed==0 and self.__v_position==0:
            self.__v_speed += self.__jump_height
        if fps != 0:
            speed_multiplier = 10/fps
        else:
            speed_multiplier = 1
        moving = False
        if keys[pygame.K_z]:
            next_positionx = self.__position[0] - cos(self.__rotation) * speed_multiplier
            next_positiony = self.__position[1] - sin(self.__rotation) * speed_multiplier
            moving = True

        if keys[pygame.K_s]:

            next_positionx = self.__position[0] + cos(self.__rotation) * speed_multiplier
            next_positiony = self.__position[1] + sin(self.__rotation) * speed_multiplier
            moving = True


        if keys[pygame.K_d]:
            next_positionx = self.__position[0] + sin(self.__rotation) * speed_multiplier
            next_positiony = self.__position[1] - cos(self.__rotation) * speed_multiplier
            moving = True


        if keys[pygame.K_q]:
            next_positionx = self.__position[0] - sin(self.__rotation) * speed_multiplier
            next_positiony = self.__position[1] + cos(self.__rotation) * speed_multiplier
            moving = True

        if moving:
            try:

                #checking if not out of the map
                if 0 < next_positionx <= len(self.__map) + 1.9 :
                    if self.__map[floor(self.__position[1])][floor(next_positionx)] == 0:  # isn't in a wall
                        self.__position[0] = next_positionx
                elif 0 < next_positionx:
                    self.__position[0] = len(self.__map) + 1.9
                else:
                    self.__position[0] = 0.1

                # checking if not out of the map
                if 0 < next_positiony <= len(self.__map[0]) - 2.1:
                    if self.__map[floor(next_positiony)][floor(self.__position[0])] == 0:  # isn't in a wall
                        self.__position[1] = next_positiony
                elif 0 < next_positiony:
                    self.__position[1] = len(self.__map[0]) - 2.1
                else:
                    self.__position[1] = 0.1
            except:
                pass
                
        if keys[pygame.K_RIGHT]:
            self.__rotation+=0.1
        if keys[pygame.K_LEFT]:
            self.__rotation-=0.1

    def __determine_size__(self,size,distance):
        if distance != 0:
            return (size * self.__focal_lenght)/distance
        return 0

    def __create_lines__(self):
        offset = self.__FOV / 2
        nb_of_lines = self.__rendering_resolution
        line_offset = (offset / self.__rendering_resolution)*2

        lines = []

        for i in range(nb_of_lines):

            angle = self.__rotation + (i * line_offset) - offset
            p1 = self.__position
            p2 = (p1[0] + self.__render_distance * cos(angle), p1[1] + self.__render_distance * sin(angle))
            lines.append((p1, (p1[0]-p2[0], p1[1]-p2[1]) ))
        return lines

    def __intersection__(self,p1,v1,p2,v2):

        def cross(a, b):
            return a[0] * b[1] - a[1] * b[0]

        a = np.array(p1)
        r = np.array(v1)
        c = np.array(p2)
        s=np.array(v2)
        rxs = cross(r, s)
        if rxs == 0:
            return 0,0,0

        t = cross(c - a, s) / rxs
        u = cross(c - a, r) / rxs
        if 0<=t<=1 and 0<=u<=1:
            return t,u,rxs

        return 0,0,0

    def __determine_walls__(self,x,y):
        vectors = []


        if self.__position[0] < y:
            vectors.append(((x,y),[y,x], (0, 1)))
        elif self.__position[0] > y:
            vectors.append(((x, y), [y + 1, x], (0, 1)))

        if self.__position[1] < x:
            vectors.append(((x,y),[y,x], (1, 0)))
        elif self.__position[1] > x:
            vectors.append(((x,y),[y,x + 1], (1, 0)))

        return vectors

    def __check_grid__(self, p, v):# An implementation of the DDA algorithm. used to determine which wall colide with the ray without testings them all
        x1, y1 = p
        dx, dy = v

        mapX = int(floor(x1))
        mapY = int(floor(y1))

        stepX = 1 if dx > 0 else -1
        stepY = 1 if dy > 0 else -1

        deltaDistX = abs(1 / dx) if dx != 0 else inf
        deltaDistY = abs(1 / dy) if dy != 0 else inf

        if dx > 0:
            sideDistX = (mapX + 1 - x1) * deltaDistX
        else:
            sideDistX = (x1 - mapX) * deltaDistX

        if dy > 0:
            sideDistY = (mapY + 1 - y1) * deltaDistY
        else:
            sideDistY = (y1 - mapY) * deltaDistY

        max_steps = 100

        for _ in range(max_steps):

            if not (0 <= mapX < len(self.__map[0]) and 0 <= mapY < len(self.__map)):
                return 0

            if self.__map[mapY][mapX] != 0:
                return mapY, mapX

            if sideDistX < sideDistY:
                sideDistX += deltaDistX
                mapX += stepX
            else:
                sideDistY += deltaDistY
                mapY += stepY

        return 0





def load_map(dir: str= "map.txt"):
    map = []
    with open(dir,"r") as f:
        for i in f.readlines():
            temp = []
            for j in i.split(" "):
                if j!="\n" and j!=" " and j != "":
                    temp.append(int(j))
            map.append(temp)
    return map

def generate_textures(textures:dict):
    dic = {}
    for key,value in textures.items():
        if type(value) == tuple:
            dic[key] = value
        else:
            dic[key] = pygame.image.load(value)
    return dic

if __name__ == "__main__":

    map = load_map("map/map.txt")
    textures = generate_textures( { 1: "textures/brick.bmp" , 2: "textures/test.bmp" , 3: "textures/brick3.bmp" , 4: "textures/brick2.png" , 5: (100,100,0) } )


    Engine((1080,720),1080,map,textures,30)
