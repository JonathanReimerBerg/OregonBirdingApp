import sqlite3

def runCommand(command, loc, fetchone = False, fetchall = False):
    connection = sqlite3.connect('ProjectFiles/DBs/' + loc + 'Database.db')
    crsr = connection.cursor()
    try:
        crsr.execute(command)
    except:
        print(command)
    result = crsr.fetchall()
    connection.commit()
    connection.close
    return(result)

def checkHotspotBird(species, hotspot, loc): #check if a given species has been seen at a given hotspot
    command = "select Month, Day, CHECKLISTS.Year from CHECKLISTS RIGHT JOIN [" + species
    command += "] on CHECKLISTS.ID = [" + species + "].Checklist WHERE Hotspot = '"
    command += hotspot + "' Order By CHECKLISTS.YEAR, CHECKLISTS.MONTH, CHECKLISTS.DAY  Limit 1"
    return(runCommand(command, loc)) #returns earliest date if seen, otherwise returns nothing 

def hotspotList(birdlist, hotspot, loc): #get a species list for a  given hotspot
    fullList = []
    for i in range(0, len(birdlist)):
        earliestDate = checkHotspotBird(birdlist[i], hotspot, loc)
        if earliestDate:  #if the species has been seen there, store it and the first occurence (which was returned)
            fullList.append([birdlist[i], earliestDate])
    fullList = sorted(fullList, key=lambda element: (element[1][0][2], element[1][0][0], element[1][0][1])) #sort by date
    return(fullList)



