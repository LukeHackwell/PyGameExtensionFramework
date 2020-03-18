import pygame as pyg
from PongFramework import *

pyg.init()

#Initialise game manager, screen, and allowed events
screenSize = Vector2(1400, 800)
screenCaption = "Pong"
allowedEvents = [pyg.QUIT, pyg.MOUSEBUTTONUP, pyg.MOUSEBUTTONDOWN, pyg.MOUSEMOTION, pyg.KEYDOWN, pyg.KEYUP]

fps = 30

GM = PongGM(screenSize, screenCaption, allowedEvents)
GM.winBGColour = Colour.black



#main game loop
while True:
    GM.clock.tick(fps)

    #check for pygame events
    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            sys.exit()
        elif event.type == pyg.MOUSEMOTION:
            mouseX, mouseY = event.pos
            GM.mousePos = Vector2(mouseX, mouseY)
        elif event.type == pyg.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouseX, mouseY = event.pos
                GM.mousePos = Vector2(mouseX, mouseY)
                GM.mouseDown = True
        elif event.type == pyg.MOUSEBUTTONUP:
            if event.button == 1:
                mouseX, mouseY = event.pos
                GM.mousePos = Vector2(mouseX, mouseY)
                GM.mouseDown = False
        elif event.type == pyg.KEYDOWN:
            if event.key == pyg.K_ESCAPE:
                sys.exit()
            elif event.key == pyg.K_w:
                GM.wDown = True
            elif event.key == pyg.K_s:
                GM.sDown = True
            elif event.key == pyg.K_UP:
                GM.upDown = True
            elif event.key == pyg.K_DOWN:
                GM.downDown = True
        elif event.type == pyg.KEYUP:
            if event.key == pyg.K_w:
                GM.wDown = False
            elif event.key == pyg.K_s:
                GM.sDown = False
            elif event.key == pyg.K_UP:
                GM.upDown = False
            elif event.key == pyg.K_DOWN:
                GM.downDown = False

    GM.UpdateScripts()
    GM.CastRigidBodies()
    GM.UpdateCollisions()
    GM.MoveRigidBodies()
    GM.UpdateWindow()
