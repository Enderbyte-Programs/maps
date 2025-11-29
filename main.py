import pygame
import urllib.request
import json
import os
import threading

screensize_x = 500
screensize_y = 500

realdata = {}
inprogress:list[str] = []

if not os.path.isdir("tiles"):
    os.mkdir("tiles")

opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', "Enderbyte-Programs/Maps")]
urllib.request.install_opener(opener)

def write_3d(z,y,x,val):
    if not z in realdata:
        realdata[z] = {}
    if not y in realdata[z]:
        realdata[z][y] = {}
    realdata[z][y][x] = val

def grab_3d(z,y,x):
    """Attempt to load from this array, else return None"""
    try:
        return realdata[z][y][x]
    except:
        return None
    
def do_download(url:str,file:str):
    global needsupdate
    print(url)
    inprogress.append(url)
    os.makedirs(os.path.dirname(file),exist_ok=True)
    urllib.request.urlretrieve(url,file)
    inprogress.remove(url)
    needsupdate = True
    print("Completed",file)

class Source:
    def __init__(self,d:dict):
        self.url:str = d["url"]
        self.minzoom:int = d["minzoom"]
        self.maxzoom:int = d["maxzoom"]
        self.tilewidth:int = d["tilewidth"]
        self.tileheight:int = d["tileheight"]
        self.ext:str = d["ext"]
        self.uses_standard_tile_url_rules:bool = d["stdrules"]

    def load_url(self,z:int,y:int,x:int) -> pygame.Surface:
        image = grab_3d(z,y,x)
        if image is None:
            fileoutpath = os.path.abspath("tiles/"+str(z)+"/"+str(y)+"/"+str(x)+"."+self.ext)
            if not os.path.isfile(fileoutpath):
                try:
                    #Do a check for impossibilities
                    if self.uses_standard_tile_url_rules:
                        if z < 0 or y < 0 or x < 0:
                            raise Exception("Nonzero")
                        
                        if y > (2**z - 1) or x > (2**z - 1):
                            raise Exception("OOB")
                        
                    if z > self.maxzoom:
                        raise Exception("Overzoomed")

                    print(z,y,x,"Downloading")
                    parsedurl = self.url.replace(r"{z}",str(z)).replace(r"{y}",str(y)).replace(r"{x}",str(x))
                    if not parsedurl in inprogress:
                        print("NEW INIT")
                        threading.Thread(target=do_download,args=(parsedurl,fileoutpath)).start()
                    return loadingscreen
                except:
                    return errorscreen
            try:
                image = pygame.image.load(fileoutpath).convert()
            except:
                #Technically this should not be possible but sometimes it happens anyway
                return anomalyscreen
            write_3d(z,y,x,image)
        return image

pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([screensize_x, screensize_y],pygame.RESIZABLE)
font = pygame.font.SysFont("Arial",12)
pygame.display.set_caption("Maps")
pygame.display.set_icon(pygame.image.load("icon.png").convert())

xoffset = 0
yoffset = 0
zoom = 2
keyarray:dict = {}
errorscreen = pygame.image.load("error.png").convert()
loadingscreen = pygame.image.load("loading.png").convert()
anomalyscreen = pygame.image.load("anomaly.png").convert()
mouse_startclickpos = (0,0)
isdragging = False

def get_from_keyarray(key):
    if key in keyarray:
        return keyarray[key]
    else:
        return False

with open("config.json") as f:
    data = json.load(f)

currentsource = Source(data["sources"]["default"])

current_source_tiles_to_centre_x = round(screensize_x / 2 / currentsource.tilewidth)
current_source_tiles_to_centre_y = round(screensize_y / 2 / currentsource.tileheight)

# Run until the user asks to quit
running = True
clock = pygame.time.Clock()
needsupdate = True
mousestate = 0
ttk = 0
while running:
    ttk += 1
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            needsupdate = True
            keyarray[event.key] = True

            #Singleton fire events
            if event.key == pygame.K_q:
                running = False

            if event.key == pygame.K_EQUALS:
                zoom += 1
                xoffset *= 2
                xoffset += current_source_tiles_to_centre_x*currentsource.tilewidth
                yoffset *= 2
                yoffset += current_source_tiles_to_centre_y*currentsource.tileheight
            
            if event.key == pygame.K_MINUS:
                zoom -= 1
                xoffset -= current_source_tiles_to_centre_x*currentsource.tilewidth

                xoffset //= 2
                yoffset -= current_source_tiles_to_centre_y*currentsource.tileheight

                yoffset //= 2

        elif event.type == pygame.KEYUP:
            keyarray[event.key] = False

        elif event.type == pygame.VIDEORESIZE:
            screensize_x,screensize_y = event.size
            current_source_tiles_to_centre_x = round(screensize_x / 2 / currentsource.tilewidth)
            current_source_tiles_to_centre_y = round(screensize_y / 2 / currentsource.tileheight)
            needsupdate = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                isdragging = True
                mouse_startclickpos = pygame.mouse.get_pos()
        
        elif event.type == pygame.MOUSEWHEEL:
            if event.y == 1:
                zoom += 1
                xoffset *= 2
                xoffset += current_source_tiles_to_centre_x*currentsource.tilewidth
                yoffset *= 2
                yoffset += current_source_tiles_to_centre_y*currentsource.tileheight
            elif event.y == -1:
                zoom -= 1
                xoffset -= current_source_tiles_to_centre_x*currentsource.tilewidth

                xoffset //= 2
                yoffset -= current_source_tiles_to_centre_y*currentsource.tileheight

                yoffset //= 2
            needsupdate = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                isdragging = False

        elif event.type == pygame.MOUSEMOTION:
            if isdragging:
                xdiff = pygame.mouse.get_pos()[0] - mouse_startclickpos[0]
                ydiff = pygame.mouse.get_pos()[1] - mouse_startclickpos[1]
                xoffset -= xdiff
                yoffset -= ydiff
                mouse_startclickpos = pygame.mouse.get_pos()
                needsupdate = True

    if get_from_keyarray(pygame.K_DOWN):
        needsupdate = True
        yoffset += 5

    if get_from_keyarray(pygame.K_UP):
        needsupdate = True
        yoffset -= 5

    if get_from_keyarray(pygame.K_LEFT):
        needsupdate = True
        xoffset -= 5

    if get_from_keyarray(pygame.K_RIGHT):
        needsupdate = True
        xoffset += 5

    #Update any stragglers


    # Fill the background with white
    if needsupdate:
        screen.fill((255, 255, 255))

        nearest_tile_x = xoffset // currentsource.tilewidth 
        nearest_tile_y = yoffset // currentsource.tileheight 
        last_tile_x = (xoffset + screensize_x) // currentsource.tilewidth + 1
        last_tile_y = (yoffset + screensize_y) // currentsource.tileheight + 1

        for y in range(nearest_tile_y,last_tile_y):
            for x in range(nearest_tile_x,last_tile_x):
                screen.blit(currentsource.load_url(zoom,y,x),(((x - nearest_tile_x) * currentsource.tilewidth) - (xoffset % currentsource.tilewidth),((y - nearest_tile_y) * currentsource.tileheight)  - (yoffset % currentsource.tileheight)))

        screen.blit(font.render(f"X: {xoffset} Y: {yoffset} Z: {zoom} || {round(clock.get_fps())} FPS",True,(0,0,0)),(0,0))
        needsupdate = False

    # Flip the display
    clock.tick(30)
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()