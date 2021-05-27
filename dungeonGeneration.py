#   Author      -   Jack Manning/dhp18hgu
#   Name        -   dungeonGeneration.py
#   Description -   Python file to handle generation of a Dungeon Layout.
#                   Generation is handled via the Dungeon class and can be displayed in the Grid class as a 2D Array.
#                   Grid Class also handles exporting of dungeon to JPG.
#
#   Notes       -   Basic BSP Tree Algorithm is modified from the code found at https://gamedevelopment.tutsplus.com/tutorials/how-to-use-bsp-trees-to-generate-game-maps--gamedev-12268
#
#   Changelog   -   31/10/20    -   Created basic BSP Tree Algorithm
#                   05/11/20    -   Created Grid Class for display to console
#                   12/11/20    -   Corridors (Class) can now be 1 or 2 tiles wide
#                   13/11/20    -   Added simple seed function (8 digit)
#                   18/11/20    -   Added code to export to JPG with correct tile sprites
#                   15/01/21    -   Changed Main to take Positional arguments rather than using sys.argv
#                   18/01/21    -   Dungeon Image is now saved locally when generated
#                   19/01/21    -   Encounter info is returned via main to server file
#                   26/01/21    -   Added PopulationDensity Variable
#                   29/01/21    -   Altered logic to split rooms - Maximum room size parameter
#                   03/02/21    -   Added Shape parameter (Rectangle, Square)
#                               -   Added Drunkard's Walk as alternative Corridor Algorithm  
#                   18/02/21    -   Added movement of rooms to look more "organic"
#                   22/02/21    -   Added code to "merge" overlapping rooms
#                   23/02/21    -   Increased overall Dungeon size to allow movement of rooms from centre -> outward
#                   25/02/21    -   Room size now dependant on overall size of Dungeon (scalable)
#                   17/03/21    -   Dungeon Image can now display different Tilesets
#                   25/03/21    -   Room sizes are now determined via a Gaussian Normal Distribution



import random
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from dungeonPopulation import populateDungeon
from scipy.stats import truncnorm



#Grid class
#Used to make 2D grid for Dungeon map
class Grid:
    grid = None
    width = None
    height = None
    
    #Constructor
    #In -> Width, Height, list of rooms in Dungeon, list of corridors in Dungeon, list of child rooms
    def __init__(self, Width, Height, roomList, corridorList, childRooms):
        #Create grid
        self.grid = []
        self.width = Width
        self.height = Height
        #Populate with 0 in each cell
        for i in range(0, self.width):
            new = []
            for i in range(0, self.height):
                new.append(0)
            self.grid.append(new)
        #Now place Rooms into grid
        self.placeRooms(roomList, childRooms)
        #Now place Corridors into grid
        self.placeCorridors(corridorList)
        #Print grid to console for Debugging
        #for row in self.grid:
            #print(row)
    
    #Getter method
    def getGrid(self):
        return self.grid
    
    #Method to place dungeon rooms into 2D grid
    #In -> List of rooms, List of child rooms
    #Out -> None
    def placeRooms(self, roomList, childRooms):
        #Put each bottom-level leaf into grid
        #0 = Empty
        #1 = Normal         (Room tiles on each side)
        #2 = Left           (Left wall border)
        #3 = Right          (Right wall border)
        #4 = Bottom         (Bottom wall border)
        #5 = Top            (Top wall border)
        #6 = TopLeft        (Top left walls)
        #7 = TopRight       (Top right walls)
        #8 = BottomLeft     (Bottom left walls)
        #9 = BottomRight    (Bottom right walls)
        
        #First put 1 where each tile is to indicate that a room tile is there
        for room in roomList:
            for i in range(room.getX(), room.getX() + room.getWidth()):
                for j in range(room.getY(), room.getY() + room.getHeight()):
                        #print(i, j)
                        self.grid[i][j] = 1
                        
        
        #Repeat for all child rooms
        for room in childRooms:
            for i in range(room.getX(), room.getX() + room.getWidth()):
                for j in range(room.getY(), room.getY() + room.getHeight()):
                        self.grid[i][j] = 1                
                    
        
        #Now change each tile to correct value based on surroundings
        for i in range(0, len(self.grid)):
            row = self.grid[i]
            for j in range(0, len(row)):
            
                #Booleans to decide what tile to place
                leftEnd = False
                rightEnd = False
                topEnd = False
                bottomEnd = False
                
                if self.grid[i][j] == 1:
                    #Check left
                    if self.grid[i][j-1] == 0:
                        #Left blocked
                        leftEnd = True
                    #Check Right
                    if self.grid[i][j+1] == 0:
                        #Right Blocked
                        rightEnd = True
                    #Check Top
                    if self.grid[i-1][j] == 0:
                        #Top Blocked
                        topEnd = True
                    #Check Bottom
                    if self.grid[i+1][j] == 0:
                        #Bottom Blocked
                        bottomEnd = True
                        
                    #Now set value based on booleans
                    if topEnd and leftEnd:
                        self.grid[i][j] = 6
                    elif topEnd and rightEnd:
                        self.grid[i][j] = 7
                    elif topEnd:
                        self.grid[i][j] = 5
                    elif bottomEnd and leftEnd:
                        self.grid[i][j] = 8
                    elif bottomEnd and rightEnd:
                        self.grid[i][j] = 9
                    elif bottomEnd:
                        self.grid[i][j] = 4
                    elif leftEnd:
                        self.grid[i][j] = 2
                    elif rightEnd:
                        self.grid[i][j] = 3
                    else:
                        self.grid[i][j] = 1
    
    #Method to place Dungeon Corridors into Grid
    #In -> List of corridors
    #Out -> None 
    def placeCorridors(self, corridorList):
        #Corridor tiles
        #10 = Single Vertical
        #11 = Single Horizontal
        #12 = Double Vertial Left
        #13 = Double Vertical Right
        #14 = Double Horizontal Top
        #15 = Double Horizontal Bottom
        #16 = Top Left Corner
        #17 = Top Right Corner
        #18 = Bottom Left Corner
        #19 = Bottom Right Corner
        #20 = Crossroads
        #21 = Not Left
        #22 = Not Right
        #23 = Not Up
        #24 = Not Down
        #25 = Undefined
        
        #Put each corridor into grid as undefined corridorTile
        for corridor in corridorList:
            #For each x coord in corridor
            for i in range(corridor.getX(), corridor.getX() + corridor.getWidth()):
                #For each y coord in corridor
                for j in range(corridor.getY(), corridor.getY() + corridor.getHeight()):
                    #print("Corridor tile: {0},{1}".format(i, j))
                    #Check if current grid tile is not placed
                    if self.grid[i][j] == 0:
                        #If not placed then set to an undefined corridor tile
                        self.grid[i][j] = 25
        
        #Now adjust corridor tiles based on surroundings
        for i in range(0, len(self.grid)):
            row = self.grid[i]
            for j in range(0, len(row)):
                #Booleans to decide which corridor tile to place
                corridorLeft = False
                corridorRight = False
                corridorUp = False
                corridorDown = False
                roomUp = False
                roomDown = False
                roomLeft = False
                roomRight = False
                
                diagonalTR = False
                diagonalTL = False
                diagonalBR = False
                diagonalBL = False
                
                #If tile is undefined corridor
                if self.grid[i][j] == 25:
                    #If corridor is to the left
                    if self.grid[i][j-1] != 0 and self.grid[i][j-1] > 9:
                        corridorLeft = True
                    #If corridor is to the right
                    if self.grid[i][j+1] != 0 and self.grid[i][j+1] > 9:
                        corridorRight = True
                    #If corridor is above
                    if self.grid[i-1][j] != 0 and self.grid[i-1][j] > 9:
                        corridorUp = True
                    #If corridor is below
                    if self.grid[i+1][j] != 0 and self.grid[i+1][j] > 9:
                        corridorDown = True
                    #If room is to the left
                    if self.grid[i][j-1] != 0 and self.grid[i][j-1] < 10:
                        roomLeft = True
                    #If room is to the right
                    if self.grid[i][j+1] != 0 and self.grid[i][j+1] < 10:
                        roomRight = True
                    #If room is above
                    if self.grid[i-1][j] != 0 and self.grid[i-1][j] < 10:
                        roomUp = True
                    #If room is below
                    if self.grid[i+1][j] != 0 and self.grid[i+1][j] < 10:
                        roomDown = True
                    if self.grid[i-1][j+1] > 9:
                        diagonalTR = True
                    if self.grid[i-1][j-1] > 9:
                        diagonalTL = True
                    if self.grid[i+1][j+1] > 9:
                        diagonalBR = True
                    if self.grid[i+1][j-1] > 9:
                        diagonalBL = True
                        
                    #Now set value based on booleans
                    
                    #Double wide corridors
                    #Vertical Right
                    if (corridorUp or roomUp) and (corridorDown or roomDown) and (corridorLeft or roomLeft) and (diagonalBL or diagonalTL):
                        self.grid[i][j] = 13
                    #vertical left
                    elif (corridorUp or roomUp) and (corridorDown or roomDown) and (corridorRight or roomRight) and (diagonalBR or diagonalTR):
                        self.grid[i][j] = 12
                    #Horizontal Top
                    elif (corridorRight or roomRight) and (corridorLeft or roomLeft) and (corridorDown or roomDown) and (diagonalBL or diagonalBR):
                        self.grid[i][j] = 14
                    elif (corridorRight or roomRight) and (corridorLeft or roomLeft) and (corridorUp or roomUp) and (diagonalTL or diagonalTR):
                        self.grid[i][j] = 15
                    
                    
                    
                    
                    
                    #Corridor on all sides
                    elif corridorLeft and corridorRight and corridorDown and corridorUp:
                        #Crossroads - Corridor on all sides
                        self.grid[i][j] = 20
                    #Don't need Room on all sides as this would be inside a room and not a corridor tile
                    
                    #Corridor on 3 sides with room on the other
                    elif corridorLeft and corridorRight and corridorDown and roomUp:
                        #Crossroads bordering on room above
                        self.grid[i][j] = 20    
                    elif corridorLeft and corridorRight and roomDown and corridorUp:
                        #Crossroads bordering on room below
                        self.grid[i][j] = 20 
                    elif roomLeft and corridorRight and corridorDown and corridorUp:
                        #Crossroads bordering on room left
                        self.grid[i][j] = 20    
                    elif corridorLeft and roomRight and corridorDown and corridorUp:
                        #Crossroads bordering on room right
                        self.grid[i][j] = 20    
                    
                    
                    
                    #Corridor on 3 sides with nothing on other    
                    elif corridorLeft and corridorRight and corridorUp and not corridorDown:
                        #Not Down
                        self.grid[i][j] = 24
                    elif corridorLeft and corridorRight and not corridorUp and corridorDown:
                        #Not Up
                        self.grid[i][j] = 23
                    elif corridorLeft and not corridorRight and corridorUp and corridorDown:
                        #Not right
                        self.grid[i][j] = 22
                    elif not corridorLeft and corridorRight and corridorUp and corridorDown:
                        #Not Left
                        self.grid[i][j] = 21
                        
                    
                    #Corridor on just two sides
                    elif corridorLeft and corridorUp:
                        #TopLeft
                        self.grid[i][j] = 16
                    elif corridorLeft and corridorDown:
                        #BottomLeft
                        self.grid[i][j] = 18
                    elif corridorRight and corridorUp:
                        #TopRight
                        self.grid[i][j] = 17
                    elif corridorRight and corridorDown:
                        #BottomRight
                        self.grid[i][j] = 19
                    elif corridorRight and corridorLeft:
                        #Horizontal
                        self.grid[i][j] = 11
                    elif corridorUp and corridorDown:
                        #Vertical
                        self.grid[i][j] = 10
                        
                    #Corridor on one side and room on one side
                    elif roomUp and corridorDown:
                        #Vertical
                        self.grid[i][j] = 10
                    elif roomDown and corridorUp:
                        #Vertical
                        self.grid[i][j] = 10
                    elif roomLeft and corridorRight:
                        #Horizontal
                        self.grid[i][j] = 11
                    elif roomRight and corridorLeft:
                        #Horizontal
                        self.grid[i][j] = 11
                    
                    elif (roomUp or corridorUp) and (roomRight or corridorRight):
                        #Top right Corner tile
                        self.grid[i][j] = 17
                    elif (roomUp or corridorUp) and (roomLeft or corridorLeft):
                        #Top left corner tile
                        self.grid[i][j] = 16
                    elif (roomDown or corridorDown) and (roomRight or corridorRight):
                        #Bottom Right corner tile
                        self.grid[i][j] = 19
                    elif (roomDown or corridorDown) and (roomLeft or corridorLeft):
                        #Bottom left corner tile
                        self.grid[i][j] = 18
                        
                    elif roomLeft and roomRight:
                        #Horizontal tile
                        self.grid[i][j] = 11
                    elif roomUp and roomDown:
                        #Vertical tile
                        self.grid[i][j] = 10
                        
                    else:
                        print("Error tile at {0},{1}".format(i,j))

    
#Room class
#Used to contain information for Dungeon rooms
class Room:
    x = None
    y = None
    height = None
    width = None
    childRoom = None
    size = None

    #Constructor
    #In -> Room x co-ordinate, Room y co-ordinate, Room width, Room Height
    def __init__(self, X, Y, Width, Height):
        self.x = X
        self.y = Y
        self.width = Width
        self.height = Height
        self.size = self.width * self.height
        
    #Getter methods
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y 
    
    def getHeight(self):
        return self.height 
    
    def getWidth(self):
        return self.width
    
    #ToString method for bug fixing in console
    def __str__(self):
        return "Room at: (" + str(self.x) + "," + str(self.y) + ") " + str(self.width) + "x" + str(self.height)
        
        
#Corridor class
#Used to contain information about Dungeon Corridors
class Corridor:
    x = None
    y = None
    height = None
    width = None
    
    #Constructor
    #In -> Corridor x co-ordinate, Corridor y co-ordinate, Corridor width, Corridor height
    def __init__(self, X, Y, Width, Height):
        self.x = X
        self.y = Y
        self.width = Width
        self.height = Height
    
    #Getter methods
    def getX(self):
        return self.x 
    
    def getY(self):
        return self.y
    
    def getWidth(self):
        return self.width
    
    def getHeight(self):
        return self.height
    
    #ToString method
    def __str__(self):
        return "Corridor at: (" + str(self.x) + "," + str(self.y) + ") " + str(self.width) + "x" + str(self.height)
       
#BSP Leaf Class       
class Leaf:
    #Positional variables
    x = None
    y = None
    width = None
    height = None
    #Child variables
    leftChild = None
    rightChild = None
    room = None
    #Size restriction variables
    minimumSize = None
    maximumLeafSize = None
    
    corridorAlgorithm = None
    
    dungeonWidth = None
    dungeonHeight = None
    
    #Constructor
    #In -> Leaf X co-ordinate, Leaf Y co-ordinate, Leaf width, Leaf height, selected Corridor-placing algorithm, Dungeon Width, Dungeon Height
    def __init__(self, X, Y, Width, Height, CorridorAlg, DunWidth, DunHeight):
        self.x = X
        self.y = Y
        self.width = Width
        self.height = Height
        self.corridorAlgorithm = CorridorAlg
        self.dungeonWidth = DunWidth
        self.dungeonHeight = DunHeight
        #Set minimum leaf size based on Size of Dungeon
        self.minimumSize = 6    #Always have minimum size of 4x4
        if DunWidth == 25:
            self.maximumLeafSize = 12 #Allows 10x10 rooms
        elif DunWidth == 51:
            self.maximumLeafSize = 18 #Allows 16x16 rooms
        elif DunWidth == 70:
            self.maximumLeafSize = 22 #Allows for 20x20 rooms
        else:                         #Default
            self.maximumLeafSize = 16 #Allows for 14x14 rooms
  
        
    def __str__(self):
        return "{0},{1} {2}x{3}".format(self.x, self.y, self.width, self.height)
    
    #Getter methods
    def getX(self):
        return self.x 
    
    def getY(self):
        return self.y
    
    def getWidth(self):
        return self.width
    
    def getHeight(self):
        return self.height
        
    def getLeftChild(self):
        return self.leftChild
    
    def getRightChild(self):
        return self.rightChild
        
    def getMinimumSize(self):
        return self.minimumSize
        
    def getMaximumLeafSize(self):
        return self.maximumLeafSize
    
    #Method to get a room from a leaf
    #Doesn't work the same as other getters, as this leaf might not have a room
    #So child leaves are also checked to see if they have a room
    #In -> None
    #Out -> Child Room
    def getRoom(self):
        #If leaf has a room -> return it
        if self.room != None:
            return self.room
        #Otherwise find a room below
        else:
            leftRoom = None
            rightRoom = None
            #Check if left child exists
            if self.leftChild != None:
                #Find room from left side
                leftRoom = self.leftChild.getRoom()
            #Check if right child exists
            if self.rightChild != None:
                rightRoom = self.rightChild.getRoom()
            
            #Check if both rooms are null
            if leftRoom == None and rightRoom == None:
                return None
            elif rightRoom == None:
                return leftRoom
            elif leftRoom == None:
                return rightRoom
            #50 percent chance to return left or right from here
            rand = random.randint(0,1)
            if rand == 0:
                return leftRoom
            else:
                return rightRoom
                
        
    #ToString method
    def __str__(self):
        return "Leaf at: (" + str(self.x) + "," + str(self.y) + ") " + str(self.width) + "x" + str(self.height)
    
    #Split method to break leaf into sub leaves
    #In -> None
    #Out -> Boolean of whether current Leaf has been split
    def split(self):
        #Check if both children are null
        if self.leftChild == None and self.rightChild == None:
            #Then able to split into children
            #Decide which way to split:
            #If height > 25% larger than width -> Split horizontally (1)
            #If width > 25% larger than width -> split vertically (2)
            #Otherwise split randomly
            splitDirection = None
            #If the leaf can be split either way -> Follow split algorithm
            if self.height > self.maximumLeafSize and self.width > self.maximumLeafSize:
                if self.height > self.width and (self.height / self.width) >= 1.25:
                    splitDirection = 1 #Horizontal
                elif self.width > self.height and (self.width / self.height) >= 1.25:
                    splitDirection = 2 #Vertical
                else:
                    splitDirection = random.randint(1,2) #Random direction
            else:
                #Otherwise split the only way it can be
                if self.height > self.maximumLeafSize:
                    splitDirection = 1 #Horizontal
                elif self.width > self.maximumLeafSize:
                    splitDirection = 2 #Vertical
                else:
                    #If room doesn't NEED to be split, randomly decide whether to split anyway if possible
                    #This is based on the size of the dungeon
                    if self.maximumLeafSize == 12:
                        temp = random.randint(1,2)
                        if temp == 1:
                            #Dont split
                            return false
                    elif self.maximumLeafSize == 16:
                        temp = random.randint(1,3)
                        if temp == 1:
                            #Dont split
                            return false
                    elif self.maximumLeafSize == 18:
                        temp = random.randint(1,4)
                        if temp == 1:
                               #Dont split
                               return false
                    else:
                        temp = random.randint(1,5)
                        if temp == 1:
                            #Don't split
                            return false
                        
                    #Now decide how to split
                    
                    if self.height > (self.minimumSize * 2) and self.width > (self.minimumSize * 2):
                        #Split randomly
                        splitDirection = random.randint(1,2)
                    elif self.height > (self.minimumSize * 2):
                        splitDirection = 1
                    elif self.width > (self.minimumSize * 2):
                        splitDirection = 2
                    else:
                        #Otherwise dont split
                        return False
            #print("split direction = " + str(splitDirection))
            #Determine maximum split point
            #Eg: Cant split 15 into 5 and 10 as 5 is less than minimum leaf size
            maxSplit = None
            if splitDirection == 1:
                maxSplit = self.height - self.minimumSize
            else:
                maxSplit = self.width - self.minimumSize
            #print(maxSplit)
            #Determine where to split current leaf
            splitPoint = None
            if maxSplit == self.minimumSize:
                splitPoint = self.minimumSize
            elif maxSplit < self.minimumSize:
                return False
            else:
                splitPoint = random.randint(self.minimumSize, maxSplit)
            #print("Split Point: " + str(splitPoint))
            #Create children based on split point
            if splitDirection == 1:
                #Split horizontally
                self.leftChild = Leaf(self.x, self.y, self.width, splitPoint, self.corridorAlgorithm, self.dungeonWidth, self.dungeonHeight)
                self.rightChild = Leaf(self.x, self.y + splitPoint, self.width, self.height - splitPoint, self.corridorAlgorithm, self.dungeonWidth, self.dungeonHeight)
                
            else:
                #Split Vertically
                self.leftChild = Leaf(self.x, self.y, splitPoint, self.height, self.corridorAlgorithm, self.dungeonWidth, self.dungeonHeight)
                self.rightChild = Leaf(self.x + splitPoint, self.y, self.width - splitPoint, self.height, self.corridorAlgorithm, self.dungeonWidth, self.dungeonHeight)
            #print(self.leftChild)
            #print(self.rightChild)
            #Return complete
            return True
        
        else:
            #If both children aren't null then don't split further
            return False
        
    #Service method to create a normal distribution for the chosen room size
    def create_truncated_normal(self, mean, sd, low, upp):
        return truncnorm(
            (low-mean) / sd, (upp - mean) / sd, loc = mean, scale = sd)
        
    #Method to iterate through this leaf and child leaves, and create rooms for each bottom-level child leaf
    #In -> List of corridors, list of Rooms
    #Out-> None (Adds rooms to list)
    def createRooms(self,corridorList, roomList):
        #Check leaf to see if it has already been split
        if self.leftChild != None or self.rightChild != None:
            #Check left child
            if self.leftChild != None:
                self.leftChild.createRooms(corridorList, roomList)
            #Check right child
            if self.rightChild != None:
                self.rightChild.createRooms(corridorList, roomList)
                
            #If left and right children -> connect them with corridor
            if self.leftChild != None and self.rightChild != None:
                #Call Corridor method from Dungeon Class
                self.createCorridor(self.leftChild.getRoom(), self.rightChild.getRoom(), corridorList)
        else:
            #Ready to make a room
            #At bottom-level leaf
            roomHeight = None
            roomWidth = None
            roomPosX = None #Top left corner of room
            roomPosY = None
            
            #Middle value in range
            meanWidth = round(((self.width - 2) + (self.minimumSize - 2)) / 2)
            meanHeight = round(((self.height - 2) + (self.minimumSize - 2)) / 2)
            upperBoundWidth = self.width - 2
            upperBoundHeight = self.height - 2
            
            lowerBound = self.minimumSize - 2
            
            standardDeviation = 1
            
            if(upperBoundWidth == lowerBound):
                roomWidth = lowerBound
            else:
                #print("Width Normal :", meanWidth, standardDeviation, lowerBound, upperBoundWidth)
                widthNormal = self.create_truncated_normal(meanWidth, standardDeviation, lowerBound, upperBoundWidth)
                roomWidth = round(widthNormal.rvs())
            if(upperBoundHeight == lowerBound):
                roomHeight = lowerBound
            else:
                #print("Height Normal: ", meanHeight, standardDeviation, lowerBound, upperBoundHeight)
                heightNormal = self.create_truncated_normal(meanHeight, standardDeviation, lowerBound, upperBoundHeight)
                roomHeight = round(heightNormal.rvs())
            
            #Gaussian selection of room sizes
            #print("Size: " + str(roomWidth) + "x" + str(roomHeight))
            
            #Determine room Position inside of leaf
            roomPosX = random.randint(1, self.width - roomWidth - 1)
            roomPosY = random.randint(1, self.height - roomHeight - 1)
            
            
            #Adjust room position at random - Shift Up, Down, Left, or Right up to 10 tiles at random
            #Decide whether this room will be moved (2/3 chance)
            move = random.randint(0,2)
            if (move != 0):
                #Determine how far to move this room - differs depending on dungeon Size
                #Tiny : 1-3
                #Small: 2-5
                #Normal:3-7
                #Large: 4-10
                moveAmount = None
                if (self.dungeonWidth == 25):
                    moveAmount = random.randint(1,5)
                elif (self.dungeonWidth == 35):
                    moveAmount = random.randint(1,5)
                elif (self.dungeonWidth == 51):
                    moveAmount = random.randint(1,7)
                elif (self.dungeonWidth == 70):
                    moveAmount = random.randint(1,10)
                
                #Determine which directions this room can move
                moveableHorizontal = []
                moveableVertical = []
                #Check if room can move left - 
                if (((self.x + roomPosX) - moveAmount) >= 1):
                    moveableHorizontal.append("left")
                if (self.dungeonWidth > (self.x + roomPosX + roomWidth + moveAmount)):
                    moveableHorizontal.append("right")
                if ((self.y + roomPosY - moveAmount) >= 1):
                    moveableVertical.append("up")
                if (self.dungeonHeight > (self.y + roomPosY + roomHeight + moveAmount)):
                    moveableVertical.append("down")
                    
                #Get random x and y direction from list of possible directions
                ind = random.randint(0, len(moveableHorizontal) - 1)
                moveDirH = moveableHorizontal[ind]
                
                ind = random.randint(0, len(moveableVertical) - 1)
                moveDirV = moveableVertical[ind]
                
                #Move room by specified amount in correct direction
                if (moveDirH == "left"):
                    roomPosX -= moveAmount
                else:
                    roomPosX += moveAmount
                    
                if (moveDirV == "up"):
                    roomPosY -= moveAmount
                else:
                    roomPosY += moveAmount
            #Create Room
            self.room = Room(self.x + roomPosX, self.y + roomPosY, roomWidth, roomHeight)
            #Add to rooms list
            roomList.append(self.room)
            
    #Method to create corridor between two rooms (Can use 1 of 2 corridor algorithms)
    #In -> Room1, Room2, List of Corridors
    #Out-> None (Adds corridors to list)
    def createCorridor(self, room1, room2, corridorList):
        #Decide which corridor algorithm to use
        #Drunkards Walk -> Randomly move until you hit the chosen room
        if self.corridorAlgorithm == "Drunkard":
            #print("Not implemented yet")
            #Pick random point inside each room
            point1X = random.randint(room1.getX() + 1 , room1.getX() + room1.getWidth() - 2)
            point1Y = random.randint(room1.getY() + 1, room1.getY() + room1.getHeight() - 2)
            point2X = random.randint(room2.getX() + 1, room2.getX() + room2.getWidth() - 2)
            point2Y = random.randint(room2.getY() + 1, room2.getY() + room2.getHeight() - 2)
            #print("Making corridor from {0},{1} to {2},{3}".format(point1X, point1Y, point2X, point2Y))
            #Move randomly from Point1
            currentX = point1X
            currentY = point1Y
            
            direction1 = None
            direction2 = None
            #Decide which 2 directions to move
            if point1X <= point2X:
                direction1 = 1
            else:
                direction1 = -1
            if point1Y <= point2Y:
                direction2 = 1
            else:
                direction2 = -1
                
            while(currentX != point2X or currentY != point2Y):
                #Decide whether to move in X or Y
                if currentX == point2X:
                    #Move Y
                    currentY += direction2
                elif currentY == point2Y:
                    #Move X
                    currentX += direction1
                #Otherwise move randomly
                else:
                    if(random.randint(1,2) == 1):
                        #Move in X
                        currentX += direction1
                    else:
                        #Move in Y
                        currentY += direction2
                #print("Tile at {0},{1}".format(currentX, currentY))
                corridorList.append(Corridor(currentX, currentY, 1, 1))
            
            
        #BSP Corridor Algorithm
        else:
            #Pick random point inside each room
            point1X = random.randint(room1.getX() + 1 , room1.getX() + room1.getWidth() - 2)
            point1Y = random.randint(room1.getY() + 1, room1.getY() + room1.getHeight() - 2)
            point2X = random.randint(room2.getX() + 1, room2.getX() + room2.getWidth() - 2)
            point2Y = random.randint(room2.getY() + 1, room2.getY() + room2.getHeight() - 2)
            
            #Calculate width and height between points
            w = point2X - point1X
            h = point2Y - point1Y
            
            #print("Corridor {0}x{1}".format(w, h))
            #print("From {0},{1} to {2},{3}".format(point1X, point1Y, point2X, point2Y))
            #If width is negative (room 2 is left of room 1)
            if w < 0:
                #If height is negative (room 2 is above room 1)
                if h < 0:
                    #2/3 chance for single 1/3 chance for double
                    if random.randint(0, 2) == 2:
                        corridorList.append(Corridor(point2X, point1Y, np.abs(w), 1))
                        corridorList.append(Corridor(point2X, point2Y, 1, np.abs(h)))
                    else:
                        corridorList.append(Corridor(point2X, point2Y, np.abs(w), 1))
                        corridorList.append(Corridor(point1X, point2Y, 1, np.abs(h)))
                        
                #If height is positive (room 2 is below room 1)
                elif h > 0:
                    #2/3 chance for single 1/3 chance for double
                    if random.randint(0, 2) == 2:
                        corridorList.append(Corridor(point2X, point1Y, np.abs(w), 1))
                        corridorList.append(Corridor(point2X, point1Y, 1, np.abs(h)))
                    else:
                        corridorList.append(Corridor(point2X, point2Y, np.abs(w), 1))
                        corridorList.append(Corridor(point1X, point1Y, 1, np.abs(h+1))) #+1 here is a temp fix which may be removed if it causes errors
                #If height is 0 (room 2 is at same height as room 1)
                else:
                    corridorList.append(Corridor(point2X, point2Y, np.abs(w), 1))
            #If width is positive (room 2 is right of room 1)
            elif w > 0:
                #If height is negative (room 2 is above room 1)
                if h < 0:
                    #2/3 chance for single 1/3 chance for double
                    if random.randint(0, 2) == 2:
                        corridorList.append(Corridor(point1X, point2Y, np.abs(w), 1))
                        corridorList.append(Corridor(point1X, point2Y, 1, np.abs(h)))
                    else:
                        corridorList.append(Corridor(point1X, point1Y, np.abs(w+1), 1)) #Another temp fix
                        corridorList.append(Corridor(point2X, point2Y, 1, np.abs(h)))
                #If height is positive (room 2 is below room 1)
                elif h > 0:
                    #2/3 chance for single 1/3 chance for double
                    if random.randint(0, 2) == 2:
                        corridorList.append(Corridor(point1X, point1Y, np.abs(w), 1))
                        corridorList.append(Corridor(point2X, point1Y, 1, np.abs(h)))
                    else:
                        corridorList.append(Corridor(point1X, point2Y, np.abs(w), 1))
                        corridorList.append(Corridor(point1X, point1Y, 1, np.abs(h)))
                #If height is 0 (room 2 is same height as room 1)
                else:
                    corridorList.append(Corridor(point1X, point1Y, np.abs(w), 1))
            #If width is 0 (Room 2 is at same x as room 1)
            else:
                if h < 0:
                    corridorList.append(Corridor(point2X, point2Y, 1, np.abs(h)))
                else:
                    corridorList.append(Corridor(point1X, point1Y, 1, np.abs(h)))
                

            
#Dungeon class to hold a complete dungeon
class Dungeon:
    width = None
    height = None
    leaves = None
    rooms = None
    
    childRooms = None
    corridors = None
    rootLeaf = None
    grid = None
    seed = None
    imageBase = None
    imageEnemies = None
    splitOccured = None
    encounterText = None
    shape = None
    populationDensity = None
    
    tileset = None
    
    
    
    #Constructor
    #In -> Dungeon size, Dungeon Shape, CorridorAlgorithm, Tileset
    #Out -> Nothing
    def __init__(self, Size, Shape, CorridorAlg, Tileset):
        
        #Shapes
        #Square: AxA
        #Rectangular: Ax2A/3
        rootX = None
        rootY = None
        rootHeight = None
        rootWidth = None
        
        if Shape == "Square":
            #Sizes
            #Tiny: 15x15 (25x25) + 5 each side
            #Small 25x25    (35x35) + 5 each side
            #Medium 35x35   (51x51) + 8 each side
            #Large 50x50    (70x70) + 10 each side
            if Size == "1":
                self.width = 25
                self.height = 25
                rootX = 5
                rootY = 5
                rootHeight = 15
                rootWidth = 15
            elif Size == "2":
                self.width = 35
                self.height = 35
                rootX = 5
                rootY = 5
                rootHeight = 25
                rootWidth = 25
            elif Size == "3":
                self.width = 51
                self.height = 51
                rootX = 8
                rootY = 8
                rootHeight = 35
                rootWidth = 35
            elif Size == "4":
                self.width = 70
                self.height = 70
                rootX = 10
                rootY = 10
                rootHeight = 50
                rootWidth = 50
            else:
                #Default to small
                self.width = 35
                self.height = 35
                rootX = 5
                rootY = 5
                rootHeight = 25
                rootWidth = 25
        elif Shape == "Rectangle":
            #Sizes
            #Tiny: 15x12 (25x22) + 5 each side
            #Small: 25x15   (35x25) + 5 each side
            #Medium: 35x20  (51x36) + 8 each side
            #Large: 50x30   (70x50) + 10 each side
            if Size == "1":
                self.width = 25
                self.height = 22
                rootX = 5
                rootY = 5
                rootHeight = 12
                rootWidth = 15
            elif Size == "2":
                self.width = 35
                self.height = 25
                rootX = 5
                rootY = 5
                rootHeight = 15
                rootWidth = 25
            elif Size == "3":
                self.width = 51
                self.height = 36
                rootX = 8
                rootY = 8
                rootHeight = 20
                rootWidth = 35
            elif Size == "4":
                self.width = 70
                self.height = 50
                rootX = 10
                rootY = 10
                rootHeight = 30
                rootWidth = 50
            else:
                #Default to small
                self.width = 35
                self.height = 25
                rootX = 5
                rootY = 5
                rootHeight = 15
                rootWidth = 25
        else:
            print("Error")
        #Set Seed
        #self.seed = random.randint(0,999999)
        #print("Seed: {0}".format(self.seed))
        #random.seed = self.seed
        #Create empty lists
        self.leaves = []
        self.rooms = []
        self.childRooms = []
        self.corridors = []
        
        #Set Tileset
        self.tileset = Tileset
        
        #Create root leaf
        self.rootLeaf = Leaf(rootX, rootY, rootWidth, rootHeight, CorridorAlg, self.width, self.height)
        #Add root leaf to leaves list
        self.leaves.append(self.rootLeaf)
        #Start generating dungeon
        self.generateDungeon()
        
    #Getter methods
    def getWidth(self):
        return self.width
        
    def getHeight(self):
        return self.height
        
    def getLeaves(self):
        return self.leaves
     
    def getRooms(self):
        return self.rooms
    
    def getRootLeaf(self):
        return self.rootLeaf
    
    def getGrid(self):
        return self.grid
        
    def getSeed(self):
        return self.seed
        
    def getImage(self):
        return self.imageBase
    
    def getEncounterText(self):
        return self.encounterText
    
   #Method to create image from grid
   #In -> List of Rooms, Chosen tileset
   #Out -> None (Creates image and saves to static folder)
    def createImage(self, rooms, tileset):
    
        #print("Tileset: {0}".format(tileset))
        #Dimensions of a single tile
        imHeight = 16
        imWidth = 16
        #Room Tiles
        #0 = None
        #1 = Normal
        #2 = Left
        #3 = Right
        #4 = Down
        #5 = Top
        #6 = TopLeft
        #7 = TopRight
        #8 = BottomLeft
        #9 = BottomRight
        
        #Corridor tiles
        #10 = Single Vertical
        #11 = Single Horizontal
        #12 = Double Vertial Left
        #13 = Double Vertical Right
        #14 = Double Horizontal Top
        #15 = Double Horizontal Bottom
        #16 = Top Left Corner
        #17 = Top Right Corner
        #18 = Bottom Left Corner
        #19 = Bottom Right Corner
        #20 = Crossroads
        #21 = Not Left
        #22 = Not Right
        #23 = Not Up
        #24 = Not Down
        #25 = Undefined
        
        #Create images
        blank = Image.open("sprites/" + tileset + "Tiles/blank.png")
        center = Image.open("sprites/" + tileset + "Tiles/Tile.png")
        bottom = Image.open("sprites/" + tileset + "Tiles/Bottom.png")
        top = Image.open("sprites/" + tileset + "Tiles/Top.png")
        left = Image.open("sprites/" + tileset + "Tiles/Left.png")
        right = Image.open("sprites/" + tileset + "Tiles/Right.png")
        topleft = Image.open("sprites/" + tileset + "Tiles/Topleft.png")
        topright = Image.open("sprites/" + tileset + "Tiles/Topright.png")
        bottomleft = Image.open("sprites/" + tileset + "Tiles/Bottomleft.png")
        bottomright = Image.open("sprites/" + tileset + "Tiles/Bottomright.png")
        
        vertical = Image.open("sprites/" + tileset + "Tiles/CorridorSingleVertical.png")
        horizontal = Image.open("sprites/" + tileset + "Tiles/CorridorSingleHorizontal.png")
        
        topleftCorridor = Image.open("sprites/" + tileset + "Tiles/CorridorTopLeftCorner.png")
        toprightCorridor = Image.open("sprites/" + tileset + "Tiles/CorridorTopRightCorner.png")
        bottomleftCorridor = Image.open("sprites/" + tileset + "Tiles/CorridorBottomLeftCorner.png")
        bottomrightCorridor = Image.open("sprites/" + tileset + "Tiles/CorridorBottomRightCorner.png")
        
        crossroad = Image.open("sprites/" + tileset + "Tiles/CorridorCrossroad.png")
        
        notleft = Image.open("sprites/" + tileset + "Tiles/CorridorNotLeft.png")
        notright = Image.open("sprites/" + tileset + "Tiles/CorridorNotRight.png")
        notup = Image.open("sprites/" + tileset + "Tiles/CorridorNotUp.png")
        notdown = Image.open("sprites/" + tileset + "Tiles/CorridorNotDown.png")
        
        doubleVLeft = Image.open("sprites/" + tileset + "Tiles/CorridorDoubleVerticalLeft.png")
        doubleVRight = Image.open("sprites/" + tileset + "Tiles/CorridorDoubleVerticalRight.png")
        doubleHTop = Image.open("sprites/" + tileset + "Tiles/CorridorDoubleHorizontalTop.png")
        doubleHBottom = Image.open("sprites/" + tileset + "Tiles/CorridorDoubleHorizontalBottom.png")
        
          
        #Create empty picture grid
        pics = []
        #Create an image for each row
        for row in self.grid.getGrid():
            #Create image from list
            pic = Image.new("RGB", (len(row) * imWidth, imHeight))
            for i in range(0, len(row)):
                im = row[i]
                if im == 0:
                    pic.paste(blank, (i * imWidth, 0))
                elif im == 1:
                    pic.paste(center, (i * imWidth, 0))
                elif im == 2:
                    pic.paste(left, (i * imWidth, 0))
                elif im == 3:
                    pic.paste(right, (i * imWidth, 0))
                elif im == 5:
                    pic.paste(top, (i * imWidth, 0))
                elif im == 4:
                    pic.paste(bottom, (i * imWidth, 0))
                elif im == 6:
                    pic.paste(topleft, (i * imWidth, 0))
                elif im == 7:
                    pic.paste(topright, (i * imWidth, 0))
                elif im == 8:
                    pic.paste(bottomleft, (i * imWidth, 0))
                elif im == 9:
                    pic.paste(bottomright, (i * imWidth, 0))
                elif im == 10:
                    pic.paste(vertical, (i * imWidth, 0))
                elif im == 11:
                    pic.paste(horizontal, (i * imWidth, 0))
                elif im == 12:
                    pic.paste(doubleVLeft, (i * imWidth, 0))
                elif im == 13:
                    pic.paste(doubleVRight, (i * imWidth, 0))
                elif im == 14:
                    pic.paste(doubleHTop, (i * imWidth, 0))
                elif im == 15:
                    pic.paste(doubleHBottom, (i * imWidth, 0))
                elif im == 16:
                    pic.paste(topleftCorridor, (i * imWidth, 0))
                elif im == 17:
                    pic.paste(toprightCorridor, (i * imWidth, 0))
                elif im == 18:
                    pic.paste(bottomleftCorridor, (i * imWidth, 0))
                elif im == 19:
                    pic.paste(bottomrightCorridor, (i * imWidth, 0))
                elif im == 20:
                    pic.paste(crossroad, (i * imWidth, 0))
                elif im == 21:
                    pic.paste(notleft, (i * imWidth, 0))
                elif im == 22:
                    pic.paste(notright, (i * imWidth, 0))
                elif im == 23:
                    pic.paste(notup, (i * imWidth, 0))
                elif im == 24:
                    pic.paste(notdown, (i * imWidth, 0))
            #pic.show()
            pics.append(pic)
        #Concatenate row image together
        pic = Image.new("RGB", (pics[0].width, pics[0].height * len(pics)))
        for i in range(0, len(pics)):
            pic.paste(pics[i], (0, i * pics[i].height))
        
        
        font = ImageFont.truetype("times-ro.ttf", 12)
        d = ImageDraw.Draw(pic)
        #Label rooms with Numbers
        for room in rooms:
            ind = rooms.index(room) + 1
            posX = (room.getY() * imHeight) + (imHeight/5 * 2)
            posY = (room.getX() * imWidth) + (imWidth/5 * 2)
            d.text((posX, posY), str(ind), (0,0,0), font=font)
            
        
        imageBase = pic
        imageBase.save('static/LatestDungeon.PNG', 'PNG')
        #imageBase.show()
        
   
    #Dungeon generation method
    #In -> None
    #Out -> None
    def generateDungeon(self):
    
        #Set splitOccured boolean to True to start splitting
        self.splitOccured = True
        
        #Whilst a new split has happened
        while(self.splitOccured):
            #Set splitOccured to false until a split happens
            self.splitOccured = False
            #Iterate over every leaf checking if they can be split
            for leaf in self.leaves:
                #Check if both children are Null
                if leaf.getLeftChild() == None and leaf.getRightChild() == None:
                    #Check if leaf is too large
                    if leaf.getHeight() > leaf.getMaximumLeafSize() or leaf.getWidth() > leaf.getMaximumLeafSize():
                        #Split Leaf
                        temp = leaf.split()
                        #Check if split actually happened
                        if temp:
                            #Add child leaves to leafList
                            self.leaves.append(leaf.getLeftChild())
                            self.leaves.append(leaf.getRightChild())
                            #Set splitOccured to true
                            self.splitOccured = True
        
        #Now start creating rooms from rootLeaf -> This will automatically start creating corridors as well
        self.rootLeaf.createRooms(self.corridors, self.rooms)
        
        touchingRooms = []
        toRemove = []
        #Now determine whether any rooms are overlapping
        for i in range(0, len(self.rooms)):
            #Get current room
            room1 = self.rooms[i]
            #Check current rooms co-ords against every other room after it 
            for j in range (i + 1, len(self.rooms)):
                room2 = self.rooms[j]
                r1x1 = room1.getX()
                r1y1 = room1.getY()
                r1x2 = r1x1 + room1.getWidth()
                r1y2 = r1y1 + room1.getHeight()
                #print("Room 1: ", r1x, ",", r1y)
                
                r2x1 = room2.getX()
                r2y1 = room2.getY()
                r2x2 = r2x1+ room2.getWidth()
                r2y2 = r2y1 + room2.getHeight()
                #print("Room 2: ", r2x, ",", r2y)
                
                #Check for overlap of rooms
                if(r1x1 >= r2x2 or r2x1 >= r1x2 or r1y1 >= r2y2 or r2y1 >= r1y2):
                    print("No Overlap")
                    #Now check if rooms are touching
                    if (r1x1 > r2x2 or r2x1 > r1x2):
                        print("Not touching Horizontally")
                    else:
                        print("Touching Horizontally")
                        if (r1y1 > r2y2 or r2y1 > r1y2):
                            print("Not touching Vertically")
                        else:
                            print("Touching Vertically")
                            #Rooms touching
                            touchingRooms.append(self.rooms.index(room1))
                      
                else:
                    print("Overlap")
                    #If an overlap is found -> Check if room 1 has a child
                    room = self.rooms[i]
                    while (room.childRoom != None):
                        temp = room.childRoom
                        room = temp
                    room.childRoom = self.rooms[j]
                    if room.childRoom not in self.childRooms:
                        self.childRooms.append(self.rooms[j])
        
        #Now remove rooms that need to be removed
        for i in range(0, len(self.childRooms)):
            self.rooms.remove(self.childRooms[i])
           
        
        #Now create 2D grid
        self.grid = Grid(self.width, self.height, self.rooms, self.corridors, self.childRooms)
        #Fix touching rooms that have walls unconstructed
        print(touchingRooms)
        for roomIndex in touchingRooms:
            #Get room
            try:
                room = self.rooms[roomIndex]
                #Alter edge tiles
                #Start with Left and right tiles (Including corners
                for i in range (room.getX(), room.getX() + room.getWidth() - 1):
                    if i == room.getX():
                        self.grid.grid[i][room.getY()] = 6
                        self.grid.grid[i][room.getY() + room.getHeight() - 1] = 7
                    elif i == (room.getX() + room.getWidth() - 1):
                        self.grid.grid[i][room.getY()] = 8
                        self.grid.grid[i][room.getY() + room.getHeight() - 1] = 9
                    else:
                        self.grid.grid[i][room.getY()] = 2
                        self.grid.grid[i][room.getY() + room.getHeight() - 1] = 3
                
                #Now do Top and Bottom Tiles
                for i in range (room.getY(), room.getY() + room.getHeight() - 1):
                    if i == room.getY():
                        self.grid.grid[room.getX()][i] = 6
                        self.grid.grid[room.getX() + room.getWidth() - 1][i] = 8
                    elif i == (room.getY() + room.getHeight() - 1):
                        self.grid.grid[room.getX()][i] = 7
                        self.grid.grid[room.getX() + room.getWidth() - 1][i] = 9
                    else:
                        self.grid.grid[room.getX()][i] = 5
                        self.grid.grid[room.getX() + room.getWidth() - 1][i] = 4
            except:
                print("Error: Room removed")
                continue
        #Now create Image 
        self.createImage(self.rooms, self.tileset)
        
#Main method to create dungeon from parameters given through system arguments 
#In -> Size, Shape, CorridorAlgorithm, Dungeon Seed, Population Seed, DungeonTheme, Party Size, Party Avg Level, PopulationDensity, Tileset
#Out -> List of encounters (generated via dungeonPopulation.py), Dungeon Seed, Population Seed, Party Size, Party average level
def main(Size, Shape, CorridorAlgorithm, DunSeed, PopSeed, Theme, PartySize, PartyLevel, PopDensity, Tileset):

    #If seed is not given (0) then create new random seed
    chosenSeed = None
    if DunSeed == None:
        DunSeed = 0
    if int(DunSeed) == 0:
        chosenSeed = random.randint(1, 99999999)
        random.seed(chosenSeed)
        np.random.seed(chosenSeed)
    else:
        random.seed(int(DunSeed))
        np.random.seed(int(DunSeed))
        chosenSeed = DunSeed
    print("Seed: {0}".format(chosenSeed))
    #Generate Dungeon
    dungeon = Dungeon(Size, Shape, CorridorAlgorithm, Tileset)
    
    
    #Now handle population
    #Set/determine population seed
    if int(PopSeed) == 0:
        #Reset current random
        random.seed()
        PopSeed = random.randint(1, 9999)
        random.seed(PopSeed)
    else:
        random.seed(int(PopSeed))
    #print("Population Seed: {0}".format(PopSeed))
    #Now populate dungeon with enemies -> By calling dungeonPopulation.populateDungeon()
    encounters, partySize, partyLevel = populateDungeon(dungeon.getRooms(), PopSeed, Theme, int(PartySize), int(PartyLevel), PopDensity)
    
    return encounters, chosenSeed, PopSeed, partySize, partyLevel
    
    
        

 
 
 #if __name__ == "__main__":
    #main()   