import pygame.font

def draw_text_middle(surface:pygame.Surface, dfont:str, text:str, size:int, colour:list|tuple):
    font = pygame.font.SysFont(dfont,size)
    label = font.render(text, True, colour)
    lx,ly = label.get_size()
    sx,sy = surface.get_size()

    surface.blit(label,(sx/2 - lx / 2,sy/2 - ly/2))

    #return bottom of y
    return (sy/2 + ly/2)
    

def confirm(win:pygame.Surface,fontname:str,fontsize:int,msg:str):
    pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW))
    clk = pygame.time.Clock()
    run = True
    while run:
        win.fill((0,0,128))
        ev = pygame.event.get()
        by = draw_text_middle(win,fontname,msg + " [Y/N]",fontsize,(255,255,255))
        yesbutton = Button((0,255,0),win.get_size()[0]/2-100,by,100,50,"YES")
        nobutton = Button((255,0,0),win.get_size()[0]/2,by,100,50,"NO")
        if yesbutton.isOver(ev):
            return True
        if nobutton.isOver(ev):
            return False
        yesbutton.draw(win)
        nobutton.draw(win)

        for event in ev:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_n:
                    return False
        
        clk.tick(30)    
        pygame.display.update()

class Button():
    def __init__(self, color, x, y, width, height, text='',imagepath = ''):
        self.color = color
        self.ogcol = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.juston = False
        self.on = False

        if imagepath != '':
            self.image:pygame.Surface = pygame.image.load(imagepath).convert()
        else:
            self.image:pygame.Surface = None # type: ignore

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont('Arial', 24)
            text = font.render(self.text, True, (0, 0, 0))

        else:
            text = self.image
        
        win.blit(text, (
        self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, ev):
        pos = pygame.mouse.get_pos()

        # Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND))
                self.color = (128, 128, 128)
                self.on = True

            else:
                self.color = self.ogcol
                self.on = False

        else:
            self.color = self.ogcol
            self.on = False

        if not self.on and self.juston:
            pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW))
        self.juston = self.on

        for event in ev:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pos[0] > self.x and pos[0] < self.x + self.width:
                    if pos[1] > self.y and pos[1] < self.y + self.height:
                        return True
