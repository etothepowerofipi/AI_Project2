# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"
        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        foodList = newFood.asList()
        if len(foodList) == 0:
            return successorGameState.getScore()

        oldFood = currentGameState.getFood()
        oldFoodList = oldFood.asList()

        #if there are fewer dots of food in the new state, that means one was consumed
        contains_food = len(foodList) < len(oldFoodList)

        #list of all the positions of the ghosts
        ghostList = []
        for s in newGhostStates:
            ghostList.append(s.getPosition())

        #Computes distance to closest ghost
        distToGhost = manhattanDistance(newPos,ghostList[0])
        for g in ghostList:
            dist = manhattanDistance(newPos,g)
            if (dist < distToGhost):
                distToGhost = dist

        #If there is a ghost in the new state, then it is obviously a bad move to go there, unless it is the last piece of food and PacMan immediately wins.
        #However, that case is already taken care of in the <if len(foodList) == 0> check
        if newPos in ghostList:
            return -9999

        #Moving to a state where food is consumed is most of the time better than the alternatives
        if contains_food:
            return 9999

        #The distance to the closest food dot. It is obviously never 0, because if there were food in this state, it has already been consumed
        min = 0
        if newPos not in foodList:
            min = manhattanDistance(newPos,foodList[0])
            for f in foodList[1:]:
                dist = manhattanDistance(newPos,f)
                if (dist < min):
                    min = dist
        

        #Distance to closest piece of food is much more important than distance to closest ghost
        return distToGhost/(min*min*min)
        


def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """


    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        depth =  self.depth
        pacMan = self.index

        firstGhost = 1
        bestMove = None
        #Useful for finding maximum score
        a = -999999
        #Useful for finding minimum score
        b = 999999

        agents = gameState.getNumAgents()
        pacManActions = gameState.getLegalActions(pacMan)
        for pAct in pacManActions:
            pacManSuccessor = gameState.generateSuccessor(pacMan,pAct)
            #The ghosts all act as one player, each calling self.min() recursively until all ghosts have been checked. Hence, it starts with the first ghost.
            score = self.min(a,b,firstGhost,pacManSuccessor,depth)
            if (score > a):
                a = score
                bestMove = pAct

        return bestMove

        util.raiseNotDefined()

    def max(self,a,b,gameState:GameState,depth):
        if gameState.isWin() or gameState.isLose() or depth == 0:
            return self.evaluationFunction(gameState)
        agents = gameState.getNumAgents()
        max = a
        pacManActions = gameState.getLegalActions(0)
        for pAct in pacManActions:
            pacManSuccessor = gameState.generateSuccessor(0,pAct)
            score = self.min(max,b,1,pacManSuccessor,depth)
            if score > max:
                max = score
        return max

                    
    def min(self,a,b,agentNo,gameState:GameState,depth):
        if gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState)
        min = b
        lastGhost = gameState.getNumAgents() - 1
        ghostActions = gameState.getLegalActions(agentNo)
        for gAct in ghostActions:
            ghostSuccessor = gameState.generateSuccessor(agentNo,gAct)
            score = 0
            if agentNo == lastGhost:
                score = self.max(a,min,ghostSuccessor,depth-1)
            else:
                nextAgent = agentNo + 1
                score = self.min(a,min,nextAgent,ghostSuccessor,depth)
            if score < min:
                min = score
        return min



class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def maxValue(self,gameState:GameState, a, b, depth):
        if gameState.isWin() or gameState.isLose() or depth == 0:
            return self.evaluationFunction(gameState)
        v = -999999
        agents = gameState.getNumAgents()
        pacManActions = gameState.getLegalActions(0)
        for action in pacManActions:
            pacManSuccessor = gameState.generateSuccessor(0,action)
            temp = self.minValue(pacManSuccessor,a,b,depth,1)
            v = max(v,temp)
            if v > b:
                return v
            a = max(a,v)
        return v
    
    def minValue(self,gameState:GameState, a, b, depth, agentNo):
        if gameState.isWin() or gameState.isLose() or depth == 0:
            return self.evaluationFunction(gameState)
        v = 999999
        agents = gameState.getNumAgents()
        lastGhost = agents - 1
        ghostActions = gameState.getLegalActions(agentNo)
        for action in ghostActions:
            ghostSuccessor = gameState.generateSuccessor(agentNo,action)
            if agentNo < lastGhost:
                nextAgent = agentNo + 1
                temp = self.minValue(ghostSuccessor,a,b,depth,nextAgent)
                v = min(v,temp)
            else:
                v = min(v,self.maxValue(ghostSuccessor,a,b,depth-1))
            if v < a:
                return v
            b = min(v,b)
        return v

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        a = -999999
        b = 999999
        bestMove = None
        pacManActions = gameState.getLegalActions(0)
        for action in pacManActions:
            pacManSuccessor = gameState.generateSuccessor(0,action)
            value = self.minValue(pacManSuccessor,a,b,self.depth,1)
            if value > a:
                a = value
                bestMove = action
        return bestMove

        util.raiseNotDefined()

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """
    
    def expectiMax(self, gameState : GameState, depth, agentNo):
        if gameState.isWin() or gameState.isLose() or depth == 0:
            return self.evaluationFunction(gameState)
        isPacman = agentNo == 0
        actions = gameState.getLegalActions(agentNo)
        if isPacman:
            max = -999999
            for action in actions:
                pacManSuccessor = gameState.generateSuccessor(agentNo,action)
                v = self.expectiMax(pacManSuccessor,depth,(agentNo+1))
                if v > max:
                    max = v
            return max
        n = len(actions)
        avg = 0
        agents = gameState.getNumAgents()
        lastGhost = agents - 1
        if agentNo < lastGhost:
            for action in actions:
                ghostSuccessor = gameState.generateSuccessor(agentNo,action)
                v = self.expectiMax(ghostSuccessor,depth,(agentNo+1))
                avg += v / n
            return avg
        for action in actions:
            ghostSuccessor = gameState.generateSuccessor(agentNo,action)
            v = self.expectiMax(ghostSuccessor,(depth-1),0)
            avg += v / n
        return avg



    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        bestMove = None
        max = -999999
        pacManActions = gameState.getLegalActions(0)
        for action in pacManActions:
            pacManSuccessor = gameState.generateSuccessor(0,action)
            value = self.expectiMax(pacManSuccessor,self.depth,1)
            if value > max:
                max = value
                bestMove = action
        return bestMove


        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    The function simply returns current score minus the distance to the closest food pellet.
    Thus, PacMan is motivated to always minimize the distance to said pellet, meaning
    it will more often than not path towards it
    """
    "*** YOUR CODE HERE ***"
    pacManPos = currentGameState.getPacmanPosition()
    foodList = currentGameState.getFood().asList()

    if len(foodList) == 0:
        return currentGameState.getScore()

    minDist = manhattanDistance(pacManPos,foodList[0])
    for f in foodList[1:]:
        dist = manhattanDistance(pacManPos,f)
        if dist < minDist:
            minDist = dist
    #Very similar to the function from q1, only this one is even simpler to understand (and compute).
    return currentGameState.getScore() - minDist

    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
