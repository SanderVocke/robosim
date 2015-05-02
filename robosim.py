from pygame.locals import *
import pygame
import math

screen = pygame.display.set_mode((1024, 768), DOUBLEBUF)
pygame.display.set_caption("EVC Robosim")
robo = pygame.transform.scale(pygame.image.load('robo.png'), (200,200))
roboaxiswidth = 350/800*200
clock = pygame.time.Clock()
FPS = 30
UPDATES_DIV = 2
DSPEED = 0.01
PIXPERMETER = 150
TARGETRADIUS = 20
#updates
frames_to_update = 0

#robot state
robolspeed = 0 #max +/- 255
roborspeed = 0 #max +/- 255
roboangle = 0;
robopos = (3,3) #in meters

#target state
targetFound = False
targetRelPos = (0,0)

#########################################################
## ROBOT BEHAVIOUR STARTS HERE
## The robot behaviour algorithm gets 15 updates of target
## position per second. When an update comes, the following
## function executes.
##
## You have the following information at your disposal:
## - boolean targetFound: true if a target was found
## - tuple targetRelPos: (x,y). Coordinates (cartesian) of
##     the target with respect to the robot, if found.
##
## You can do the following actions:
## - setSpeed(which, speed): sets the rotation speed of 
##    one robot wheel. <which> chooses the wheel: set it
##    to the string "LEFT" for left, or "RIGHT" for right.
##    <speed> sets the speed. It is in a range from 
##    -255 to 255.
##
#########################################################

def robot_behaviour():
	global targetFound, targetRelPos
	
	#is there a target?
	if not targetFound: #stand still if no target
		setSpeed("LEFT", 0)
		setSpeed("RIGHT", 0)
		return
		
	#are we going straight toward it? keep going!
	if abs(targetRelPos[0]/targetRelPos[1]) < 0.1 and targetRelPos[1]>0:
		setSpeed("LEFT", 255)
		setSpeed("RIGHT",255)
		return
	
	#else, awkwardly rotate towards the target
	if targetRelPos[0] > 0:
		setSpeed("LEFT", 255)
		setSpeed("RIGHT", -255)
	else:
		setSpeed("LEFT", -255)
		setSpeed("RIGHT", 255)

#########################################################
## ROBOT BEHAVIOUR ENDS HERE
#########################################################



def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

def drawBackground(color):
	global screen
	screen.fill(color)

def drawBot(position, angle):
	global robo, screen
	sz = robo.get_size()
	px = position[0]*PIXPERMETER - 0.5*sz[0]
	py = position[1]*PIXPERMETER - 0.5*sz[1]
	rotated = rot_center(robo, angle*180/math.pi)
	screen.blit(rotated, (px,py))

def drawTarget():
	global targetFound, targetRelPos, screen
	
	mpos = pygame.mouse.get_pos()
	buts = pygame.mouse.get_pressed()
	
	if (not pygame.mouse.get_focused()) or (not buts[0]): #no target
		targetFound = False
	else:
		targetFound = True		
		pygame.draw.circle(screen, (255,0,0), mpos, TARGETRADIUS)
		mpos = (mpos[0] / PIXPERMETER, mpos[1] / PIXPERMETER) #to meter conversion
		targetRelPos = ((mpos[0]-robopos[0])*math.cos(-roboangle) + (mpos[1]-robopos[1])*math.sin(-roboangle), (mpos[0]-robopos[0])*math.sin(-roboangle) - (mpos[1]-robopos[1])*math.cos(-roboangle))
	
def updateBot():
	global robopos, roboangle, roborspeed, robolspeed
	Sr = roborspeed * DSPEED
	Sl = robolspeed * DSPEED
	
	if abs(Sl-Sr) < 0.000001:
		print(str(Sl*math.cos(roboangle)))
		nx = robopos[0]*PIXPERMETER -Sl*math.sin(roboangle)
		ny = robopos[1]*PIXPERMETER -Sl*math.cos(roboangle)
		na = roboangle
	else:
		R = roboaxiswidth * (Sl + Sr) / (2* (Sr - Sl))
		wd = (Sr - Sl) / roboaxiswidth
		nx = robopos[0]*PIXPERMETER + R*math.cos(wd+roboangle) - R*math.cos(roboangle)
		ny = robopos[1]*PIXPERMETER  - R*math.sin(wd+roboangle) + R*math.sin(roboangle)
		
		na = roboangle + wd
		while na < 0:
			na = na + 2*math.pi
		while na > 2*math.pi:
			na = na - 2*math.pi
			
	roboangle = na
	robopos = (nx/PIXPERMETER , ny/PIXPERMETER)
	
def setSpeed(which, speed):
	global robolspeed, roborspeed
	
	if which == "LEFT": 
		robolspeed=speed
	elif which == "RIGHT":
		roborspeed=speed
	
	
#main:
pygame.init()
while True:
	drawBackground((80,80,80))
	updateBot()
	drawBot(robopos, roboangle)
	drawTarget()
	frames_to_update = frames_to_update - 1
	if frames_to_update <= 0:
		robot_behaviour()
		frames_to_update = UPDATES_DIV-1
		if frames_to_update < 0:
			frames_to_update = 0
	pygame.display.flip()
	clock.tick(FPS)
	
	
	for event in pygame.event.get():
		if event.type == QUIT:
			exit()
		elif event.type == KEYDOWN and event.key == K_ESCAPE:
			exit()
	
