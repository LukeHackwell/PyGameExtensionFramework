import pygame as pyg
import random
import sys
import time



class Vector2:
# Store 2D vectors

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, factor):
        return Vector2(self.x * factor, self.y * factor)

    def __truediv__(self, factor):
        return Vector2(self.x / factor, self.y / factor)

    def __str__(self):
        return "[{}, {}]".format(self.x, self.y)

    def Tuple(self):
        return (self.x, self.y)

    @staticmethod
    def Zero():
        return Vector2(0, 0)
    
    @staticmethod
    def Up():
        return Vector2(0, 1)

    @staticmethod
    def Down():
        return Vector2(0, -1)
    
    @staticmethod
    def Right():
        return Vector2(1, 0)

    @staticmethod
    def Left():
        return Vector2(-1, 0)


class GameManager:
    """
    Base class for the game manager. Handles the updating of physics, controls, scripts, and graphics
    """

    def __init__(self, screenSize, screenCaption, allowedEvents):
        self.win =  pyg.display.set_mode(screenSize.Tuple(), pyg.FULLSCREEN)
        pyg.display.set_caption(screenCaption)
        self.winBGColour = Colour.white
        self.clock = pyg.time.Clock()
        self.allowedEvents = allowedEvents

        self.screenSize = screenSize

        self.previousFrameTime = 0
        self.currentFrameTime =0.01
        self.updateTime = 0

        self.mousePos = Vector2.Zero()
        self.mouseDown = False

       # def __init__(self, scene, topLeft, size, bGColour, text, textSize, textColour, font, textOffset):
        self.blits = [[] for _ in range(10)]
        self.scenes = {}
        pyg.event.set_allowed(allowedEvents)

        self.currentScene = None

    def GetUpdateTime(self):
        # gets the time since the last frame update
        self.currentFrameTime = time.time()
        self.updateTime = self.currentFrameTime - self.previousFrameTime

        self.previousFrameTime = time.time()


    def ChangeScene(self, newScene):
        del self.currentScene
        self.currentScene = newScene


    def UpdateScripts(self):
        #runs each scripts attached to each game object in the current scene

        gameObjects = self.currentScene.gameObjects

        for gameObject in gameObjects:
            gameObject.Update()

    def CastRigidBodies(self):
        #casts the new position of each rigid body

        for gameObject in self.currentScene.gameObjects:
            if gameObject.rigidBody != None:
                gameObject.rigidBody.Cast()


    def UpdateCollisions(self):
        #checks if pairs of game objects have colliders and sends them to CheckForCollisions()
        gameObjects = self.currentScene.gameObjects

        for primObj in gameObjects:
            if primObj.collider != None:
                if primObj.collider.enabled == True:
                    primObj.collider.collisions = []

                    for secObj in gameObjects:
                        if secObj != primObj and secObj.collider != None:

                            if secObj.collider.enabled == True:
                                self.CheckForCollision(primObj, secObj)

    @staticmethod
    def CheckForCollision(primObj, secObj):
        #checks if the casted rigid body(s) will collide

        if primObj.rigidBody == None:
            primPosition = primObj.transform.position
        else:
            primPosition = primObj.rigidBody.castPosition

        if secObj.rigidBody == None:
            secPosition = secObj.transform.position
        else:
            secPosition = secObj.rigidBody.castPosition

        primSize = primObj.collider.size
        secSize = secObj.collider.size

        if primPosition.x < secPosition.x + secSize.x and primPosition.x + primSize.x > secPosition.x:
            if primPosition.y < secPosition.y + secSize.y and primPosition.y + primSize.y > secPosition.y:
                primObj.collider.collisions.append(secObj.collider)


    def MoveRigidBodies(self):
        #moves rigid bodies to their casted positions if they have no collisions

        for gameObject in self.currentScene.gameObjects:
            if gameObject.rigidBody != None:
                if gameObject.collider != None:
                    if gameObject.collider.collisions == []:
                        gameObject.transform.position = gameObject.rigidBody.castPosition

                else:
                    gameObject.transform.position = gameObject.rigidBody.castPosition
                    gameObject.rigidBody.velocity = Vector2.Zero()

    def UpdateWindow(self):
        #If game object has a sprite add this game object to the corresponsing layer of blits[]. Update graphics on screen
        gameObjects = self.currentScene.gameObjects

        for gameObject in gameObjects:
            if type(gameObject.sprite) is Sprite:
                if gameObject.sprite.enabled:
                    self.blits[gameObject.sprite.layer].append(Blit(gameObject.sprite.image, gameObject.transform.position))

        self.win.fill(self.winBGColour)
        for layer in self.blits:
            for blit in layer:
                self.win.blit(blit.image, blit.position)

        pyg.display.update()
        self.blits = [[] for _ in range(10)]

        
class Scene:
    #base class for scenes 

    def __init__(self, gameManager):
        self.gameObjects = []
        self.gameManager = gameManager

    def AppendGameObject(self, gameObject):
        self.gameObjects.append(gameObject)
    
    def RemoveGameObject(self, gameObject):
        self.gameObjects.remove(gameObject)


class Component():
    # base class for components attached to game objects

    def __init__(self, parent):
        self.parent = parent


class Script(Component):
    # base class for scripts attached to game objects

    def __init__(self, parent):
        super().__init__(parent)
        self.enabled = True

    def Update(self):
        pass


class GameObject:
    # base class for game objects within a scene

    def __init__(self, scene):
        #get reference to the game manager and add self to its gameObjects[]
        self.scene = scene
        self.scene.AppendGameObject(self)
        self.gameManager = self.scene.gameManager

        self.scripts = []

        self.transform = Transform(self)
        self.sprite = Sprite(self, None)
        self.collider = None
        self.rigidBody = None


    def Update(self):
        # calls all scripts attached to this game object

        for script in self.scripts:
            if script.enabled:
                script.Update()


    def Enable(self):
        # enables all scripts and components on this game object

        self.sprite.enabled = True

        for script in self.scripts:
            script.enabled = True

        if self.collider != None:
            self.collider.enabled = True

        if self.rigidBody != None:
            self.rigidBody.enabled = True

    def Disable(self):
        # disables all scripts and components on this game object

        self.sprite.enabled = False

        for script in self.scripts:
            script.enabled = False

        if self.collider != None:
            self.collider.enabled = False

        if self.rigidBody != None:
            self.rigidBody.enabled = False


class Blit:
    # stores images that are to be printed to the screen

    def __init__(self, image, position):
        self.image = image
        self.position = position.Tuple()





class Transform (Component):
    def __init__(self, parent, position= Vector2.Zero()):
        super().__init__(parent)
        self.position = position


class Sprite(Component):
    def __init__(self, parent, image, enabled = True):
        super().__init__(parent)

        self.image = image
        #higher layers are printed to the screen after lower layers
        self.layer = 0
        self.enabled = enabled


class RigidBody(Component):
    def __init__(self, parent):
        super().__init__(parent)

        #velocity in pixels/frame
        self.velocity = Vector2.Zero()
        self.castPosition = Vector2.Zero()

    def Cast(self):
        self.castPosition = self.parent.transform.position + self.velocity


class BoxCollider(Component):
    def __init__(self, parent, size):
        super().__init__(parent)

        self.enabled = True
        self.size = size

        #store each game object that collided with self
        self.collisions = []


class Box(GameObject):
    def __init__(self, scene, position, size, colour):
        super().__init__(scene)

        self.transform.position = position
        self.size = size

        image = pyg.Surface((size.x, size.y))
        image.fill(colour)
        self.sprite = Sprite(self, image, enabled= True)


class TextBox(Box):
    def __init__(self, scene, position, size, bGColour1, text, textSize, textColour, font, textOffset, bGColour2 = None):
        super().__init__(scene, position, size, bGColour1)

        self.bGColour1 = bGColour1
        self.bGColour2 = bGColour2
        self.text = text
        self.textSize = textSize
        self.textColour = textColour
        self.font = font
        self.textOffset = textOffset

        image = pyg.Surface(self.size.Tuple())
        image.fill(self.bGColour1)
        fontObj = pyg.font.SysFont(self.font, self.textSize)
        textObj = fontObj.render(self.text, True, self.textColour)
        image.blit(textObj, self.textOffset.Tuple())

        self.sprite = Sprite(self, image)

    def UpdateText(self, text):
        # updates sprite to display new text

        image = pyg.Surface(self.size.Tuple())
        image.fill(self.bGColour1)
        fontObj = pyg.font.SysFont(self.font, self.textSize)
        textObj = fontObj.render(text, True, self.textColour)
        image.blit(textObj, self.textOffset.Tuple())

        self.sprite = Sprite(self, image)


class Button(Box):
    def __init__(self, scene, position, size, bGColour1, bGColour2, text, textSize, textColour, font, textOffset):
        super().__init__(scene, position, size, bGColour1)

        self.pressed = False
        self.releasedIn = False
        self.releasedOut = False
        self.colourSwapEnabled =True

        self.scripts = [CheckPressed(self), CheckReleased(self)]

        self.bGColour1 = bGColour1
        self.bGColour2 = bGColour2
        self.text = text
        self.textSize = textSize
        self.textColour = textColour
        self.font = font
        self.textOffset = textOffset

        self.sprite = self.CreateSprite(self.bGColour1)

    def DisableButton(self):
        # disables the button to be pressed

        self.colourSwapEnabled = False
        self.sprite = self.CreateSprite(self.bGColour1)


    def CreateSprite(self, colour):
        # creates a new sprite with a different background colour

        sprite = pyg.Surface(self.size.Tuple())
        sprite.fill(colour)
        fontObj = pyg.font.SysFont(self.font, self.textSize)
        textObj = fontObj.render(self.text, True, self.textColour)
        sprite.blit(textObj, self.textOffset.Tuple())

        return Sprite(self, sprite)

    def Reset(self):
        #sets the sprite colour to the initial background colour

        self.sprite = self.CreateSprite(self.bGColour1)


class CheckPressed(Script):
    #Script to be attached to a Button object. Checks if the button is pressed by the mouse

    def __init__(self, parent):
        super().__init__(parent)

    def Update(self):
        parent = self.parent
        gM = parent.gameManager

        if parent.pressed == False:
            if gM.mouseDown == True:
                if gM.mousePos.x > parent.transform.position.x and gM.mousePos.x < parent.transform.position.x + parent.size.x:
                    if gM.mousePos.y > parent.transform.position.y and gM.mousePos.y < parent.transform.position.y + parent.size.y:
                        parent.pressed = True

                        if parent.colourSwapEnabled:
                            parent.sprite = parent.CreateSprite(parent.bGColour2)


class CheckReleased(Script):
    # Script to be attached to a Button object. Checks if the mouse is released in or out of the button.

    def __init__(self, parent):
        super().__init__(parent)

    def Update(self):
        parent = self.parent
        gM = parent.gameManager

        parent.releasedIn = False
        parent.releasedOut = False

        if parent.pressed:
            if gM.mouseDown == False:
                parent.releasedOut = True
                parent.pressed = False


                if parent.colourSwapEnabled:
                    parent.sprite = parent.CreateSprite(parent.bGColour1)

                if gM.mousePos.x > parent.transform.position.x and gM.mousePos.x < parent.transform.position.x + parent.size.x:
                    if gM.mousePos.y > parent.transform.position.y and gM.mousePos.y < parent.transform.position.y + parent.size.y:
                        parent.releasedOut = False
                        parent.releasedIn = True


class OnButtonPressedChangeScene(Script):
    #Script to be added to Button. Changes the current scene if mouse is released within button

    def __init__(self, parent, newScene):
        super().__init__(parent)

        self.newScene = newScene

    def Update(self):
        if self.parent.releasedIn == True:
            self.parent.scene.gameManager.ChangeScene(self.newScene)


class Counter(TextBox):
    # counter that can be used as a score

    def __init__(self, scene, topLeft, size, bGColour1, initialCount, textSize, textColour, font, textOffset, bGColour2 = None):
        super().__init__(scene, topLeft, size, bGColour1, str(initialCount), textSize, textColour, font, textOffset)

        self.count = initialCount

    def UpdateCount(self):
        super().UpdateText(str(self.count))


class Colour:
    white = (255, 255, 255)
    grey = (140, 140, 140)
    black = (0, 0, 0)
    green = (0, 249, 42)
    blue = (19, 111, 249)
    turqoise = (0, 255, 162)
    red = (249, 19, 19)
    orange = (255, 85, 0)
    yellow = (239, 195, 21)
    pink = (255, 0, 196)
    purple = (171, 0, 255)


    @staticmethod
    def Random():
        colours = [Colour.green, Colour.blue, Colour.red, Colour.yellow, Colour.turqoise, Colour.orange, Colour.pink, Colour.purple]
        return colours[random.randint(0, len(colours) -1)]
