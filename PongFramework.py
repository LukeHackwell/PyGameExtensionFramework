from GameFramework import *

class PongGM(GameManager):
    def __init__(self, screenSize, screenCaption, allowedEvents):
        super().__init__(screenSize, screenCaption, allowedEvents)

        #controlls
        self.wDown = False
        self.sDown = False
        self.upDown = False
        self.downDown = False

        self.currentScene = StartMenu(self)



"""
Scenes
"""
class StartMenu(Scene):
    def __init__(self, gameManager):
        super().__init__(gameManager)

        playButtonSize = Vector2(176, 96)
        playButton = Button(self, gameManager.screenSize / 2 - playButtonSize / 2, playButtonSize, Colour.black, Colour.grey, "PLAY", 60, Colour.white, "Times New Roman", Vector2(10, 10))
        playButton.scripts.append(OnButtonPressedChangeScene(playButton, TwoPlayer(self.gameManager)))


class TwoPlayer(Scene):
    def __init__(self, gameManager):
        super().__init__(gameManager)

        usedColours = []

        barrierColour = GetUniqueColour(usedColours)
        barrierOffset = Vector2(0, 70)
        barrierSize = Vector2(gameManager.screenSize.x, 30)

        topBarrier = Box(self, barrierOffset, barrierSize, barrierColour)
        topBarrier.collider = BoxCollider(topBarrier, barrierSize)

        bottomBarrierPosition = Vector2(0, gameManager.screenSize.y - barrierSize.y - barrierOffset.y)
        bottomBarrier = Box(self, bottomBarrierPosition, barrierSize, barrierColour)
        bottomBarrier.collider = BoxCollider(bottomBarrier, barrierSize)

        paddleSize = Vector2(16, 70)
        paddleYPosition = gameManager.screenSize.y / 2 - paddleSize.y / 2
        paddleXOffset = 30

        paddleLeftColour = GetUniqueColour(usedColours)
        paddleLeft = Box(self, Vector2(paddleXOffset, paddleYPosition), paddleSize, paddleLeftColour)
        paddleLeft.collider = BoxCollider(paddleLeft, paddleSize)
        paddleLeft.scripts.append(PlayerController(paddleLeft, 1))
        paddleLeft.rigidBody = RigidBody(paddleLeft)

        paddleRightColour = GetUniqueColour(usedColours)
        paddleRight = Box(self, Vector2(gameManager.screenSize.x - paddleXOffset - paddleSize.x, paddleYPosition),
                          paddleSize, paddleRightColour)
        paddleRight.collider = BoxCollider(paddleRight, paddleSize)
        paddleRight.scripts.append(PlayerController(paddleRight, 2))
        paddleRight.rigidBody = RigidBody(paddleRight)

        goalSize = Vector2(100, gameManager.screenSize.y)
        goalLeft = Box(self, Vector2(-goalSize.x, 0), goalSize, Colour.black)
        goalLeft.collider = BoxCollider(goalLeft, goalSize)

        goalRight = Box(self, Vector2(gameManager.screenSize.x, 0), goalSize, Colour.black)
        goalRight.collider = BoxCollider(goalRight, goalSize)

        scoreY = 8
        scoreXSeparation = 140
        scoreBoxSize = Vector2(50, 50)
        scoreFontSize = 42
        scoreTextOffset = Vector2(5, 5)
        scoreFont = "Times New Roman"
        scoreLeft = Counter(self, Vector2(gameManager.screenSize.x / 2 - scoreBoxSize.x / 2 - scoreXSeparation, scoreY), scoreBoxSize, Colour.black, 0, scoreFontSize, paddleLeftColour, scoreFont, scoreTextOffset)
        scoreRight = Counter(self, Vector2(gameManager.screenSize.x / 2 - scoreBoxSize.x / 2 + scoreXSeparation, scoreY), scoreBoxSize, Colour.black, 0, scoreFontSize, paddleRightColour, scoreFont, scoreTextOffset)

        puckSize = Vector2(10, 10)
        puckStartPosition = gameManager.screenSize / 2 - puckSize / 2
        puck = Box(self, puckStartPosition, puckSize, Colour.white)
        puck.collider = BoxCollider(puck, puckSize)
        puck.rigidBody = RigidBody(puck)
        puck.initialSpeed = 7
        puck.rigidBody.velocity = RandomVelocity(puck.initialSpeed)
        puck.scripts.append(PuckController(puck, topBarrier, bottomBarrier, paddleLeft, paddleRight, goalLeft, goalRight, scoreLeft, scoreRight))

        maxScore = 2
        scoreKeeper = GameObject(self)
        scoreKeeper.sprite.enabled = False
        scoreKeeper.scripts.append(ScoreKeeper(scoreKeeper, maxScore, "end menu", scoreLeft, scoreRight))


class EndMenu(Scene):
    def __init__(self, gameManager):
        super().__init__(gameManager)

        playAgainButtonSize = Vector2(370, 96)
        playAgainButton = Button(self, gameManager.screenSize / 2 - playAgainButtonSize / 2, playAgainButtonSize, Colour.black, Colour.grey, "PLAY AGAIN", 60, Colour.white, "Times New Roman", Vector2(10, 10))
        playAgainButton.scripts.append(OnButtonPressedChangeScene(playAgainButton, TwoPlayer(self.gameManager)))



"""
Custom Game Objects
"""



"""
Custom Scripts
"""
class PlayerController(Script):
    #Script to be attached to paddles. Handles player controls.

    speed = 10

    def __init__(self, parent, playerNum):
        super().__init__(parent)

        self.playerNum = playerNum

        gameManager = self.parent.gameManager

        if playerNum == 1:
            self.up = gameManager.wDown
            self.down = gameManager.sDown

        elif playerNum == 2:
            self.up = gameManager.upDown
            self.down = gameManager.downDown


    def Update(self):
        rigidBody = self.parent.rigidBody

        gameManager = self.parent.gameManager

        if self.playerNum == 1:
            self.up = gameManager.wDown
            self.down = gameManager.sDown

        elif self.playerNum == 2:
            self.up = gameManager.upDown
            self.down = gameManager.downDown


        if self.down:
            rigidBody.velocity = Vector2.Up() * PlayerController.speed
        elif self.up:
            rigidBody.velocity = Vector2.Down() * PlayerController.speed
        else:
            rigidBody.velocity = Vector2.Zero()


class PuckController(Script):
    #script to be attached to puck. Handles puck physics and scoring

    def __init__(self, parent, top, bottom, paddleLeft, paddleRight, goalLeft, goalRight, scoreLeft, scoreRight):
        super().__init__(parent)

        self.top = top
        self.bottom = bottom
        self.paddleL = paddleLeft
        self.paddleR = paddleRight
        self.goalL = goalLeft
        self.goalR = goalRight
        self.scoreL = scoreLeft
        self.scoreR = scoreRight

    def Update(self):
        if self.parent.collider.collisions != []:

            for collision in self.parent.collider.collisions:
                if collision.parent == self.top or collision.parent == self.bottom:
                    self.parent.rigidBody.velocity.y *= -1

                if collision.parent == self.paddleL or collision.parent == self.paddleR:
                    IncreaseSpeed(self.parent.rigidBody.velocity)
                    self.parent.rigidBody.velocity.x *= -1

                if collision.parent == self.goalL:
                    ResetPuck(self.parent)
                    self.scoreR.count +=1
                    self.scoreR.UpdateCount()

                elif collision.parent == self.goalR:
                    ResetPuck(self.parent)
                    self.scoreL.count += 1
                    self.scoreL.UpdateCount()


class ScoreKeeper(Script):
    #Checks if the max score is exeeded, if true changes scene to end menu

    def __init__(self, parent, maxScore, nextScene, scoreLeft, scoreRight):
        super().__init__(parent)

        self.maxScore = maxScore
        self.nextScene = nextScene
        self.scoreL = scoreLeft
        self.scoreR = scoreRight

    def Update(self):
        if self.scoreL.count == self.maxScore:
            self.parent.scene.gameManager.ChangeScene(EndMenu(self.parent.scene.gameManager))
        elif self.scoreR.count == self.maxScore:
            self.parent.scene.gameManager.ChangeScene(EndMenu(self.parent.scene.gameManager))


"""
Custom functions
"""
def RandomVelocity(speed):
    #gives the puck a random diagonal velocity when a new point is started

    rand = random.random()
    if rand > 0.5:
        x = speed
    else:
        x = -speed

    rand = random.random()
    if rand > 0.5:
        y = speed
    else:
        y = -speed

    return Vector2(x, y)


def IncreaseSpeed(velocity):
    #increases the speed of the puck 
    increase = 0.75
    if velocity.x > 0:
        velocity.x += increase
    elif velocity.x < 0:
        velocity.x -= increase

    if velocity.y > 0:
        velocity.y += increase
    elif velocity.y < 0:
        velocity.y -= increase


def ResetPuck(puck):
    #resets puck for a new point
    screenSize = puck.scene.gameManager.screenSize
    puck.rigidBody.velocity = RandomVelocity(puck.initialSpeed)

    puck.transform.position = screenSize / 2


def GetUniqueColour(usedColours):
    #returns a colour that has not been used
    colour = Colour.Random()

    while colour in usedColours:
        colour = Colour.Random()

    usedColours.append(colour)
    return colour
