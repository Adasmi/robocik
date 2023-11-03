import requests
import pygame

ADDRESS = "http://localhost:8000"
SIZE = 500
MARGIN_TOP = 100

class Board:
    def __init__(self, size, margin_top):    
        self.margin_top = margin_top
        
        pygame.init()
        self.screen = pygame.display.set_mode((size, size + self.margin_top))
        self.tab = requests.get(ADDRESS).json()['game_state']
        self.route_tab = self.tab.copy()
        self.tile_size = size / 10

        self.img_info = pygame.image.load("img/info.png")
        self.img_blue = pygame.image.load("img/tile_1.png")
        self.img_red = pygame.image.load("img/tile_2.png")
        self.img_green = pygame.image.load("img/tile_3.png")
        self.img_rov = pygame.image.load("img/tile_4.png")
        self.img_path = pygame.image.load("img/tile_5.png")

    def display(self):
        self.tab = requests.get(ADDRESS).json()['game_state']
        for i in range(0,10):
            for j in range(0,10):
                if self.tab[i][j]==" ": 
                    if self.route_tab[i][j]=="p":
                        img = self.img_path
                    else: img = self.img_blue
                elif self.tab[i][j]=="o": img = self.img_red
                elif self.tab[i][j]=="x": img = self.img_green
                else: img = self.img_rov
                self.screen.blit(img, (j*self.tile_size, i*self.tile_size+self.margin_top))

        self.screen.blit(self.img_info, (0, 0))
        pygame.display.flip()

    def move(self, action):
        result = requests.post(ADDRESS, json={"action":action}).json()['result']
        if result == 3:      
            self.display()
            return True
        else: 
            if result == 2: print("Failure")
            else: print("Success!")  
            return False

class Route:
    def get_tab(self, tab_in):
        self.tab = tab_in.copy()

        # replacing " " with -1 and "r" with 0, so that other methods can work
        for i in range (0,10):
            for j in range(0,10):
                if self.tab[i][j]==" ":
                    self.tab[i][j] = -1
                elif self.tab[i][j]=="r":
                    self.tab[i][j] = 0
                    self.start_x = j
                    self.start_y = i
                elif self.tab[i][j]=="x":
                    self.end_x = j
                    self.end_y = i
    
    def lines(self, x, y, step):
        goal = False

        # marking each tile from which you can travel in a straight line to (x, y)
        for i in range(x+1, 10):
            if type(self.tab[y][i]) is not int: 
                if self.tab[y][i] == "x": goal = True
                break
            elif self.tab[y][i] == -1: self.tab[y][i] = step+1
            elif self.tab[y][i] == step: break

        for i in range(x-1, -1, -1):
            if type(self.tab[y][i]) is not int: 
                if self.tab[y][i] == "x": goal = True
                break
            elif self.tab[y][i] == -1: self.tab[y][i] = step+1
            elif self.tab[y][i] == step: break

        for i in range(y+1, 10):
            if type(self.tab[i][x]) is not int: 
                if self.tab[i][x] == "x": goal = True
                break
            elif self.tab[i][x] == -1: self.tab[i][x] = step+1
            elif self.tab[i][x] == step: break
            
        for i in range(y-1, -1, -1):
            if type(self.tab[i][x]) is not int: 
                if self.tab[i][x] == "x": goal = True
                break
            elif self.tab[i][x] == -1: self.tab[i][x] = step+1
            elif self.tab[i][x] == step: break

        return goal
    
    def create_path(self, x, y, step):

        # looking for a straight line path to a tile marked with the specified number (step), marking that path with "p"
        for i in range(x+1, 10):
            if type(self.tab[y][i]) is not int: break
            elif self.tab[y][i] == step: 
                for j in range(x, i+1):
                    self.tab[y][j] = "p"
                return (y, i)

        for i in range(x-1, -1, -1):
            if type(self.tab[y][i]) is not int: break
            elif self.tab[y][i] == step: 
                for j in range(x, i-1, -1):
                    self.tab[y][j] = "p"
                return (y, i)

        for i in range(y+1, 10):
            if type(self.tab[i][x]) is not int: break
            elif self.tab[i][x] == step: 
                for j in range(y, i+1):
                    self.tab[j][x] = "p"
                return (i, x)

        for i in range(y-1, -1, -1):
            if type(self.tab[i][x]) is not int: break
            elif self.tab[i][x] == step: 
                for j in range(y, i-1, -1):
                    self.tab[j][x] = "p"
                return (i, x)

    def search(self):
        stop = self.lines(self.start_x, self.start_y, 0)

        # creating "lines", starting from ROV position, then from every marked tile, and so on, until the doc is reached
        k=0
        while stop == False:
            k+=1
            for i in range(0,10):
                for j in range(0,10):
                    if self.tab[i][j] == k: 
                        found = self.lines(j,i,k)
                        if found: stop = True
            
        # recreating the path by finding straight line paths to tiles marekd with numbers of previous steps from "lines"
        next = self.create_path(self.end_x, self.end_y, k)
        for i in range(k-1, -1, -1):
            next = self.create_path(next[1], next[0], i)

def main():
    board = Board(SIZE, MARGIN_TOP)
    board.display()
    route = Route()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: running = board.move(1)
                elif event.key == pygame.K_UP: running = board.move(2)
                elif event.key == pygame.K_RIGHT: running = board.move(3)
                elif event.key == pygame.K_DOWN: running = board.move(4)
                elif event.key == pygame.K_SPACE: 
                    route.get_tab(board.tab)
                    route.search()
                    board.route_tab = route.tab
                    board.display()            

if __name__=="__main__":
    main()