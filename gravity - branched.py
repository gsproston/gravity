#Author: George Sproston
#Started: 2016/08/12
#Last updated: 2016/08/13
#Gravity simulation

import pygame, sys
import math, random
from pygame.locals import *

pygame.init()

class Planet:
    m = 10000 #mass
    def __init__(self,xpos,ypos,radius):
        self.x = xpos #coordinates
        self.y = ypos
        self.r = radius
    
class Asteroid:
    r = 5 #radius
    m = 10 #mass
    lineSpeed = 10 #change to 1 for no orbits
    
    def __init__(self,xpos,ypos):
        self.x = xpos #coordinates
        self.y = ypos
        self.vx = random.random()/2-0.25 #give randomised velocity
        self.vy = random.random()/2-0.25
        self.orbitalPath = []
        self.crashing = False
        self.orbiting = False
        self.ocount = 0 #orbit count, used to determine next position
        self.ox = xpos #orbital coordinates
        self.oy = ypos
        self.ovx = self.vx #orbital path velocity
        self.ovy = self.vy
        self.olimit = 0
        self.recolCount = 0 #used to recolour the line
        
    def calcPath(self): #generate orbital path
        #if not self.crashing and not self.orbiting and len(self.orbitalPath) < 100000:
        if not self.crashing and not self.orbiting:
            i = 0
            while i < self.lineSpeed:
                fx = 0.0 #cardinal forces
                fy = 0.0
                for planet in planets:
                    #first check collisions
                    d = math.sqrt(pow(self.ox-planet.x,2)+pow(self.oy-planet.y,2)) #distance between asteroid and planet
                    if (d < self.r+planet.r-3): #on a collision course
                        self.crashing = True
                        break
                    try: #find angle between asteroid and planet
                        ang = math.atan((self.ox-planet.x)/(self.oy-planet.y)) #tan(a)=o/a
                    except ZeroDivisionError: #possible to divide by zero here due to sloppy coding
                        ang = math.pi/2 #much better
                    #rate of change of position
                    #find gravitational force
                    f = G*(self.m*planet.m/pow(d,2)) #gravitational force
                    pfx = math.sin(ang)*f #sin(a)=o/h, vertical g force from this planet
                    pfy = math.cos(ang)*f #cos(a)=a/h, horizontal g force from this planet
                    if (self.ox < planet.x and pfx < 0) or (self.ox > planet.x and pfx > 0):
                        pfx = pfx*-1
                    if (self.oy < planet.y and pfy < 0) or (self.oy > planet.y and pfy > 0):
                        pfy = pfy*-1                
                    fx += pfx
                    fy += pfy
                ax = fx/self.m
                ay = fy/self.m
                self.ovx += ax
                self.ovy += ay
                self.ox += self.ovx
                self.oy += self.ovy
                self.olimit = int(len(self.orbitalPath)*0.1)
                if self.olimit > 1000:
                    self.olimit = 1000
                if len(self.orbitalPath) > 1000 and closeCompare((self.ox,self.oy),self.orbitalPath[self.olimit],1): #check if an orbit has been formed
                    self.orbiting = True
                    for j in range(0,self.olimit):
                        if not closeCompare(self.orbitalPath[len(self.orbitalPath)-2-j],self.orbitalPath[self.olimit-1-j],2):
                            self.orbiting = False 
                            break
                    if self.orbiting:
                        for j in range(0,self.olimit):
                            self.orbitalPath.pop()
                if not self.orbiting:
                    self.orbitalPath.append((round(self.ox,6),round(self.oy,6)))
                    pscreen.set_at((int(self.ox),int(self.oy)),green)
                i += 1
        if self.orbiting: #when orbiting, choose next position
            self.x = self.orbitalPath[self.ocount][0]
            self.y = self.orbitalPath[self.ocount][1]
            self.ocount += 1
            if self.ocount >= len(self.orbitalPath):
                self.ocount = 0
        else: #choose next position when falling
            self.x = self.orbitalPath[0][0]
            self.y = self.orbitalPath[0][1]
            pscreen.set_at(ipoint(self.orbitalPath[0]),background)
            self.orbitalPath.pop(0)    
            
        #recolour the line
        if self.orbiting:
            i = 0
            while i < self.lineSpeed and self.recolCount < len(self.orbitalPath):
                oscreen.set_at(ipoint(self.orbitalPath[self.recolCount]),blue)
                self.recolCount += 1
                i += 1
            if self.recolCount >= len(self.orbitalPath): #continue drawing orbit
                self.recolCount = 0
        elif self.crashing:
            i = 0
            while i < self.lineSpeed and self.recolCount < len(self.orbitalPath):
                pscreen.set_at(ipoint(self.orbitalPath[len(self.orbitalPath)-1-self.recolCount]),red)
                self.recolCount += 1
                i += 1

def draw(): #called when screen needs to be updated
    screen.fill(white)
    if showPaths:
        screen.blit(pscreen,(0,0))
    if showOrbits:
        screen.blit(oscreen,(0,0))
    for ast in asteroids:        
        pygame.draw.circle(screen,white,(int(ast.x),int(ast.y)),ast.r-1,0)
        pygame.display.update(pygame.draw.circle(screen,black,(int(ast.x),int(ast.y)),ast.r,1).inflate(5,5))
    for planet in planets:
        pygame.draw.circle(screen,white,(int(planet.x),int(planet.y)),planet.r-1,0)
        pygame.display.update(pygame.draw.circle(screen,black,(int(planet.x),int(planet.y)),planet.r,1))
    #pygame.display.flip()

def wresize(): #screen is resized, recalculate some variables
    global cxpos,cypos
    cxpos = int(screen.get_width()/2)
    cypos = int(screen.get_height()/2)

def resetFlags(): #new display flags set, fullscreen, borderless
    if fscreen:
        w = wInfo.current_w
        h = wInfo.current_h
        if bwindow:
            flags = FULLSCREEN|NOFRAME
        else:
            flags = FULLSCREEN
    else:
        w = windowWidth
        h = windowHeight
        if bwindow:
            flags = NOFRAME
        else:
            flags = 0
    screen = pygame.display.set_mode((w,h),flags)

def ipoint(p): #returns point as integer
    return((int(p[0]),int(p[1])))

def closeCompare(p1,p2,t): #sees if two points are close to each other
    tol = t #tolerance
    x1 = int(p1[0])
    x2 = int(p2[0])
    y1 = int(p1[1])
    y2 = int(p2[1])
    xr1 = range(x1-tol,x1+tol)
    xr2 = range(x2-tol,x2+tol)
    yr1 = range(y1-tol,y1+tol)
    yr2 = range(y2-tol,y2+tol)
    if (len(list(set(xr1)&set(xr2)))>0) and (len(list(set(yr1)&set(yr2)))>0):
        return True
    else:
        return False

def astRect(ast): #returns rectangle of asteroid
    return pygame.Rect((ast.x-ast.r,ast.y-ast.r),(ast.r*2,ast.r*2))

def spawnPlanets(num): #randomly spawn num planets
    global planets
    padding = 50
    while num > 0:
        x = random.randint(50+padding,windowWidth-50-padding)
        y = random.randint(50+padding,windowHeight-50-padding)
        inPlanet = False
        for planet in planets:
            d = math.sqrt(pow(x-planet.x,2)+pow(y-planet.y,2))
            if (d <= planet.r+50): #planet in a planet
                inPlanet = True
                break
        if not inPlanet:
            planets.append(Planet(x,y,50))
            num -= 1

def spawnAsteroids(num): #randomly spawn num asteroids
    global asteroids
    while num > 0:
        x = random.randint(5,windowWidth-5)
        y = random.randint(5,windowHeight-5)
        inPlanet = False
        for planet in planets:
            d = math.sqrt(pow(x-planet.x,2)+pow(y-planet.y,2))
            if (d <= planet.r+5): #asteroid in a planet
                inPlanet = True
                break
        if not inPlanet:
            asteroids.append(Asteroid(x,y))
            num -= 1
    
if __name__ == "__main__":
    #gets monitor info, used when resizing
    wInfo = pygame.display.Info()
    #constants
    G = 7*pow(10,-3) #in reality is 6.674*10^-11

    #variables
    shutdown = False
    windowWidth = 1024
    windowHeight = 576
    flags = 0
    #menu variables
    fscreen = False #fullscreen
    bwindow = False #borderless
    ratios = ["16:9","16:10","4:3"] #ratios
    ress = [[],[],[]] #holds various resolution options
    res169 = [[1024,576],[1152,648],[1280,720],[1366,768],[1600,900],[1920,1080]]
    res1610 = [[1280,800],[1440,900],[1680,1050]]
    res43 = [[960,720],[1024,768],[1280,960],[1400,1050],[1440,1080],[1600,1200],[1856,1392]]
    ress[0] = res169
    ress[1] = res1610
    ress[2] = res43
    #game options
    showOrbits = True
    showPaths = False
    
    #colours
    lightBack = True
    white = Color(255,255,255)
    black = Color(0,0,0)
    if lightBack:
        background = white
        green = Color(0,255,0)
        blue = Color(0,0,255)
        red = Color(255,0,0)
    else:
        background = Color(20,10,50)
        green = Color(150,255,150)
        blue = Color(150,150,255)
        red = Color(255,150,150)

    #init screen
    screen = pygame.display.set_mode((windowWidth, windowHeight),flags)
    cxpos = int(screen.get_width()/2) #central coords
    cypos = int(screen.get_height()/2)
    screen.fill(background)
    oscreen = pygame.Surface((windowWidth,windowHeight)) #orbit screen
    oscreen.fill(background)
    oscreen.set_colorkey(background)
    pscreen = pygame.Surface((windowWidth,windowHeight)) #path screen
    pscreen.fill(background)
    pscreen.set_colorkey(background)
    pygame.display.update()
    
    planets = []
    #planets.append(Planet(512,288,50))
    asteroids = []
    spawnPlanets(2)
    spawnAsteroids(1000)
    
    clock = pygame.time.Clock()

    draw()

    #main game loop
    while (not shutdown):        
        for event in pygame.event.get(): #runs when an event occurs
            if event.type == QUIT: #quit called
                shutdown = True #end loop
                
            elif event.type == MOUSEBUTTONDOWN: #mouse clicked
                showPaths = not showPaths
                #create asteroid at mouse click
                #asteroids.append(Asteroid(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]))

        i = 0
        while i < len(asteroids):
            #check for collisions
            for planet in planets:
                d = math.sqrt(pow(asteroids[i].x-planet.x,2)+pow(asteroids[i].y-planet.y,2))
                if d < asteroids[i].r+planet.r-3: #collision, remove from queue
                    for point in asteroids[i].orbitalPath:
                        pscreen.set_at(ipoint(point),background)
                    draw()
                    pygame.display.update(astRect(asteroids.pop(i)))
                    i -= 1
                    break
            if len(asteroids) > 0:
                asteroids[i].calcPath()
            i += 1
            
        draw()
        clock.tick(144) #update x times a second, determines FPS

    #main loop ends, exit
    pygame.quit()    
