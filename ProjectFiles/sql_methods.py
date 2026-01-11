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

def speciesData(species, loc):  #print each occurence of a species, accompanies the scatterplot  
    print(loc)
    dates = []
    
    command = "select Month, Day, CHECKLISTS.Year, Hotspot, Count from CHECKLISTS RIGHT JOIN [" + species + "] on CHECKLISTS.ID = ["
    command += species + "].Checklist;"
    dates = runCommand(command, loc)

    print('\n')
    dates =  sorted(dates, key=lambda tup: (tup[0], tup[1])) #sort by date
    for i in dates:
        print(i[0], i[1], i[2], i[3], i[4])
    print('\n')

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

def highCounts(birdlist, year, loc, hotspot = None):
    fullList = []
    if year == 'Life':
        year = 'IS NOT NULL'
    else:
        year = '= ' + str(year)
    if hotspot:
        hotspot = ' and Hotspot = "' + str(hotspot) + '"'
    else:
        hotspot = ''
    
    for i in range(0, len(birdlist)):
        command = 'SELECT Checklist, MAX(count) from "' + str(birdlist[i]) + '" ' 
        command += "LEFT JOIN CHECKLISTS ON [" + birdlist[i] + "].Checklist = CHECKLISTS.ID "
        command += "where [" + birdlist[i] + "].year " + year + hotspot 
        highCount = runCommand(command, loc)
        if highCount[0][0]:
            countDate = runCommand("SELECT Month, Day, CHECKLISTS.Year, Hotspot from CHECKLISTS where ID = '" + highCount[0][0] + "';", loc)
            fullList.append([str(highCount[0][1]) + '  ' + ' '*(5-len(str(highCount[0][1]))) + str(birdlist[i]) + ' '*(31-len(birdlist[i])) +
                             str(countDate[0][0]) + '-' + str(countDate[0][1]) + '-' + str(countDate[0][2]) + ' '*(8-len(str(countDate[0][0]))-len(str(countDate[0][1]))) + str(countDate[0][3])])
    return(fullList)



