#   Author      -   Jack Manning
#   Name        -   dungeonPopulation.py
#   Description -   Python file to handle population of a given Dungeon Layout with enemies
#                   Population will be based on a given set of parameters such as party size, party level, and enemy type/theme.
#                   If parameters are missing they will be randomised or based on defaults
#
#   Notes       -   DnD Monster data is found from the JSON provided at https://gist.github.com/tkfu/9819e4ac6d529e225e9fc58b358c3479
#
#   Changelog   -   04/01/2021  -   Created dictionaries of monster types and some simple methods
#                   05/01/2021  -   Linked File to dungeonGeneration.py and creates methods to populate a given list of rooms with Encounters
#                   26/01/2021  -   Added PopulationDensity variable
#                   05/04/2021 -    Added code to sort rooms based on size, and set the difficulty of each rooms based on its size (small = easy, larger = harder)#
#                   07/04/2021  -   Removed ability to populate dungeons with some enemy types where the number of enemies are few
import json
import re
import sys
import random  

#Dictionaries of Monster Type
beasts = {}
humanoids = {}
elementals = {}
monstrosities = {}
constructs = {}
dragons = {}
fiends = {}
undead = {}
giants = {}
everything = {}

#List of appropriate CR encounters by level for a single character
easyList = [25, 50, 75, 125, 250, 300, 350, 450, 550, 600, 800, 1000, 1100, 1250, 1400, 1600, 2000, 2100, 2400, 2800]
mediumList = [50, 100, 150, 250, 500, 600, 750, 900, 1100, 1200, 1600, 2000, 2200, 2500, 2800, 3200, 3900, 4200, 4900, 5700]
hardList = [75, 150, 225, 375, 750, 900, 1100, 1400, 1600, 1900, 2400, 3000, 3400, 3800, 4300, 4800, 5900, 6300, 7300, 8500]
deadlyList = [100, 200, 400, 500, 1100, 1400, 1700, 2100, 2400, 2800, 3600, 4500, 5100, 5700, 6400, 7200, 8800, 9500, 10900, 12700]

#Encounter class to handle enemy encounters
class Encounter:
    roomIndex = None
    enemyName = None
    enemyNumber = None
    approximateXp = None
    
    
    #Constructor
    #In -> Room Index, Enemy Name, Number of enemies, XP to award
    def __init__(self, Index, Name, Number, XP):
        self.roomIndex = Index + 1
        self.enemyName = Name
        self.enemyNumber = Number
        self.approximateXp = XP
    
    #ToString
    def __str__(self):
        if self.enemyName is not "":
            return "Room: {0}\n{1} x {2}\nApproximate XP: {3}".format(self.roomIndex, self.enemyNumber, self.enemyName, self.approximateXp)
        else:
            return "Room: {0}\nNo Encounter".format(self.roomIndex)
    
    def getRoom(self):
        return self.roomIndex
        
    def getEnemy(self):
        return self.enemyName
    
    def getNumber(self):
        return self.enemyNumber
    
    def getXP(self):
        return self.approximateXp

#Method to strip brackets and XP tag from CR Text
#In -> Text of form "10 (15,000 XP)"
#Out -> Cleaned up number form "15000"
def stripText(crText):
    temp1 = re.search(r"\((.*?)\)", crText)
    temp2 = temp1[0]
    temp3 = temp2.replace('(', '')
    temp4 = temp3.replace(' XP)', '')
    temp5 = temp4.replace(',', '')
    temp6 = int(temp5)
    return temp6

#Method to Initialise Dictionaries of monster type from JSON Data
#In -> None
#Out -> None
def initDictionaries():
    with open ('srd_5e_monsters.json') as f:
        data = json.load(f)
        for entry in data:
            #Extract size of enemy
            temp = entry['meta']
            temp2 = re.search(r"^([\w\-]+)", temp)
            size = temp2.group(1)
        
            #Check for each type of Monster
            everything[entry['name']] = stripText(entry['Challenge']), size
            #Beasts
            if("beast" in entry['meta']):
                beasts[entry['name']] = stripText(entry['Challenge']), size
            elif("humanoid" in entry['meta']):
                humanoids[entry['name']] = stripText(entry['Challenge']), size
            elif("elemental" in entry['meta']):
                elementals[entry['name']] = stripText(entry['Challenge']), size
            elif("monstrosity" in entry['meta']):
                monstrosities[entry['name']] = stripText(entry['Challenge']), size
            elif("construct" in entry['meta']):
                constructs[entry['name']] = stripText(entry['Challenge']), size
            elif("dragon" in entry['meta']):
                dragons[entry['name']] = stripText(entry['Challenge']), size
            elif("fiend" in entry['meta']):
                fiends[entry['name']] = stripText(entry['Challenge']), size
            elif("undead" in entry['meta']):
                undead[entry['name']] = stripText(entry['Challenge']), size
                
#Method to print Dictionary data to console (for testing)
#In -> None
#Out -> None
def printDictionaries():
    print(beasts)
    print(humanoids)
    print(elementals)
    print(monstrosities)
    print(constructs)
    print(dragons)
    print(fiends)
    print(undead)
    

#Method to determine encounter difficulties
#In -> Party size, Party Average level
#Out -> Easy, Medium, Hard, Deadly XP's
def determineDifficulty(PartySize, LevelAvg):
    easyXp = PartySize * easyList[LevelAvg - 1]
    mediumXp = PartySize * mediumList[LevelAvg - 1]
    hardXp = PartySize * hardList[LevelAvg - 1]
    deadlyXp = PartySize * deadlyList[LevelAvg - 1]
    return easyXp, mediumXp, hardXp, deadlyXp

#Method to create a random encounter in the given room
#In -> RoomIndex, MonsterDictionary, Target XP, Density, RoomSize
#Out -> Encounter 
def createEncounter(Index, MonsterList, Target, Density, RoomSize):
    #Determine whether encounter is required via Density
    chance = random.randint(1,100)
    if chance <= Density:
        #Create encounter
    
        #Define upper and lower range of acceptable CR's (10% up/down)
        upperTarget = Target * 1.1
        lowerTarget = Target * 0.9
        
        #Determine which types of enemies can fit in this room
        validSizes = None
        if RoomSize < 25:
            validSizes = {"Tiny", "Small", "Medium"}
        elif RoomSize < 36:
            validSizes = {"Tiny", "Small", "Medium", "Large"}
        elif RoomSize < 64:
            validSizes = {"Tiny", "Small", "Medium", "Large", "Huge"}
        else:
            validSizes = {"Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan"}
        
        #Find a monster that can fit this room with quantity of 1-4
        #Create lists of matching monsters by number
        singleMonster = []
        twoMonsters = []
        threeMonsters = []
        fourMonsters = []
        #Loop through MonsterList and find monsters that fit CR (or multiples that fit CR, e.g 3 * 100CR monster = 300CR battle)
        #Also check that enemy is not too large to fit in room
        #Medium and below can fit in any room
        #Large requires a 5x5 room
        #Huge requires a 6x6 room
        #Gargantuan requires a 8x8 room
        for monster in MonsterList:
            #First check if monster can fit in current room
            monsterSize = MonsterList.get(monster)[1]
            if monsterSize in validSizes:
                cr = int(MonsterList.get(monster)[0])
                if cr >= lowerTarget and cr <= upperTarget:
                    singleMonster.append(monster)
                if (cr*2) >= lowerTarget and (cr*2) <= upperTarget:
                    twoMonsters.append(monster)
                if (cr*3) >= lowerTarget and (cr*3) <= upperTarget:
                    threeMonsters.append(monster)
                if (cr*4) >= lowerTarget and (cr*4) <= upperTarget:
                    fourMonsters.append(monster)
        
        #Now check which of the above lists are not empty
        selectableLists = []
        if singleMonster != []:
            selectableLists.append("single")
        if twoMonsters != []:
            selectableLists.append("double")
        if threeMonsters != []:
            selectableLists.append("triple")
        if fourMonsters != []:
            selectableLists.append("quad") 
        #Now check if there is a valid list to take a monster from
        if selectableLists != []:
            #Select a random list
            chosenList = random.choice(selectableLists)
            number = None
            enemy = None
            #Now select a random enemy from the selected list
            if chosenList == "single":
                number = 1
                enemy = random.choice(singleMonster)
            elif chosenList == "double":
                number = 2
                enemy = random.choice(twoMonsters)
            elif chosenList == "triple":
                number = 3
                enemy = random.choice(threeMonsters)
            else:
                number = 4
                enemy = random.choice(fourMonsters)
            
            #Now create encounter based on randomised enemy and number
            encounter = Encounter(Index, enemy, number, Target)
            return encounter
        else:
            encounter = Encounter(Index, "", 0, 0)
            return encounter
        
    else:
        #Return blank encounter
        encounter = Encounter(Index, "", 0, 0)
        return encounter
        
        
#Full method to populate a given dungeon grid with enemies
#In -> Dungeon Rooms, Seed, Theme, Party size, Party average level, PopulationDensity
#Out -> List of encounters, Party Size, Party average level
def populateDungeon(Rooms, Seed, Theme, PartySize, PartyAvg, PopDensity):
    encounters = []
    #Initialise Monster dictionaries
    initDictionaries()
    #Determine which dictionary to use from Theme parameter
    print(Theme)
    monsterType = Theme
    if monsterType == "beasts":
        monsterDict = beasts
    elif monsterType == "humanoids":
        monsterDict = humanoids
    elif monsterType == "elementals":
        monsterDict = elementals
    elif monsterType == "monstrosities":
        monsterDict = monstrosities
    elif monsterType == "constructs":
        monsterDict = constructs
    elif monsterType == "dragons":
        monsterDict = dragons
    elif monsterType == "fiends":
        monsterDict = fiends
    elif monsterType == "undead":
        monsterDict = undead
    else:
        monsterDict = everything
    
    #print(monsterDict)
    #Check if PartySize and PartyAvg are not given
    if PartySize == 0:
        PartySize = random.randint(3,5)
    if PartyAvg == 0:
        PartyAvg = random.randint(1, 20)
    
    #Now determine XP Thresholds (Easy, Medium, Hard, Deadly)
    difficulties = determineDifficulty(PartySize, PartyAvg)
    easyXp = difficulties[0]
    mediumXp = difficulties[1]
    hardXp = difficulties[2]
    deadlyXp = difficulties[3]
    #print("Easy: {0}\nMedium: {1}\nHard: {2}\nDeadly: {3}\n".format(easyXp, mediumXp, hardXp, deadlyXp))
    
    #Determine Population Density
    density = 0
    if PopDensity == "sparse":
        density = 33
    elif PopDensity == "dense":
        density = 90
    elif PopDensity == "full":
        density = 100
    else:
        density = 75
        
    #Create sorted list of rooms based on size (width * height)
    
    sortedRooms = Rooms.copy()
    sortedRooms.sort(key=sortFunctionSize)
    
    #Now go through each room and place encounter
    for room in sortedRooms:
    
        if room != None:
        
            #Determine difficulty of room based on position in sortedRooms list
            #Ratio:         3:4:2:1     easy:medium:hard:deadly
            targetXp = None
            
            roomInd = sortedRooms.index(room)
            totalRooms = len(sortedRooms)
            
            calculation = roomInd / totalRooms
            
            if calculation <= 0.3:
                targetXp = easyXp
            elif calculation <= 0.7:
                targetXp = mediumXp
            elif calculation <= 0.9:
                targetXp = hardXp
            else:
                targetXp = deadlyXp
            
            #Get room size
            size = room.size
            
            #Get room index
            ind = Rooms.index(room)
            #Now generate encounter for room based on MonsterDictionary and Xp target
            e = createEncounter(ind, monsterDict, targetXp, density, size)
            encounters.append(e)
    
    encounters.sort(key=sortFunctionIndex)
    for encounter in encounters:
        print(encounter)
    return encounters, PartySize, PartyAvg
    
    
def sortFunctionSize(room):
    return room.size
    
def sortFunctionIndex(encounter):
    return encounter.roomIndex