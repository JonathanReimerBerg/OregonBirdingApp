#File used to create a DB from a downloaded CSV file from eBird.

import csv
import sqlite3
import re
from datetime import date
import pandas

All_Counties = ['Baker', 'Benton', 'Clackamas', 'Clatsop', 'Columbia', 'Coos', 'Crook', 'Curry', 'Deschutes', 'Douglas',
                    'Gilliam', 'Grant', 'Harney', 'Hood River', 'Jackson', 'Jefferson', 'Josephine', 'Klamath', 'Lake', 'Lane', 'Lincoln',
                    'Linn', 'Malheur', 'Marion', 'Morrow', 'Multnomah', 'Polk', 'Sherman', 'Tillamook', 'Umatilla', 'Union', 'Wallowa', 
                    'Wasco', 'Washington', 'Wheeler', 'Yamhill'] 
exclusions = ['Black Swan']

def runCommand(command, fetchone = False):
    connection = sqlite3.connect("ProjectFiles/AppData/MainDatabase.db")
    crsr = connection.cursor()
    try:
        crsr.execute(command)
    except:
        print(command)    #print the command if it doesn't work, usually a formatting issue when writing code
    if fetchone:
        result = crsr.fetchone()
    else:
        result = crsr.fetchall()
    connection.commit()
    connection.close
    return(result)

def runCommands(commands):     #run several commands at once without having to start/close connection each time. Doesn't currently allow retrieving data
    connection = sqlite3.connect("ProjectFiles/AppData/MainDatabase.db")
    crsr = connection.cursor()
    for command in commands:
        try:
            crsr.execute(command)
        except:
            print(command)    #print the command if it doesn't work, usually a formatting issue when writing code
    connection.commit()
    connection.close
    return

def generateID(loc):
    highestID = runCommand("SELECT MAX(Hotspot_ID) FROM [" + loc + "];", True)[0]
    if not highestID:
        id = int(str(All_Counties.index(loc) + 1) + "000000")
    else:
        id = highestID + 1
    return id


def removeOtherTaxa(data):  #remove all non countable taxa, coultn't get all of these in one line
    data = data[~data.Common_Name.str.contains(" x ")]  
    data = data[~data.Common_Name.str.contains(" sp.")]   
    data = data[~data.Common_Name.str.contains("/")]
    data = data[~data.Common_Name.str.contains("Domestic")]
    data['Common_Name'] = data['Common_Name'].str.replace(r'\s+\([^()]*\)$', '', regex=True) #remove stuff in parenthesis
    for i in exclusions:
        data = data[~data.Common_Name.str.contains(i)]
    return(data)

def hotspotListCount(data, hotspot, year = None):
    data = data[data['Location'] == str(hotspot)]   #include only species from a given hotspot
    if year:
        data = data[data['Date'].str[:4] == year]
    data = data.drop_duplicates('Common_Name', keep='first')  #after sorting, keep the first occurence of each species
    return len(data)

def getYears(loc):       #gets all year columns associated with a location table
    columns = runCommand("SELECT name FROM PRAGMA_TABLE_INFO('" + loc + "');")
    years = []
    for i in columns:
        if i[0].startswith('in'):       # ie in2025 column name
            years.append(i[0][2:])
    return(years)

def updateYears(loc, dbyears, actualyears):    #create (if necessary) the year total columns 
    for i in actualyears:
        if i not in dbyears:
            runCommand("ALTER TABLE '" + loc + "' ADD COLUMN in" + str(i) + " INTEGER(6) NOT NULL DEFAULT 0;")
    return

def getHotspots(loc):
    hotspots = runCommand("SELECT hotspot FROM ('" + loc + "');")
    cleanedHotspots = []
    for hotspot in hotspots:
        cleanedHotspots.append(hotspot[0])
    return cleanedHotspots


def initializeDB():
    command = """CREATE TABLE IF NOT EXISTS OREGON ( 
        County varchar(64),
        County_ID INTEGER(3),
        Updated varchar(10),
        SpeciesTotal INTEGER(5)
        CONSTRAINT OREGON_PK
        );"""
    runCommand(command)   #create a table to store each count and county ID (static)

    for i in  range (0, len(All_Counties)):
        command = "INSERT INTO OREGON (County, County_ID, Updated) Values ('" + All_Counties[i] + "', " + str(i + 100) + ", '1900-01-01');"
        runCommand(command)
        
    for i in All_Counties:
        command = "CREATE TABLE IF NOT EXISTS [" + i  +"] ("
        command += """Hotspot varchar(128), 
            Hotspot_ID INTEGER(8),
            Latitude FLOAT,
            Longitude FLOAT, 
            Total_Species INTEGER(5),
            PRIMARY KEY (Hotspot_ID));
            """
        runCommand(command)


def updateDB(loc, total):
    if loc == 'Oregon':
        return
    
    lastUpdated = runCommand("SELECT Updated from OREGON WHERE County = '" + loc + "';")
    print('\n' + loc,'last updated: ' + str(lastUpdated)[3:13])

    data = pandas.read_csv('ProjectFiles/AppData/CSVs/' + loc + 'CleanedData.csv')
    data = removeOtherTaxa(data)

    nowUpdated = (data.sort_values('Date', kind = 'mergesort', ascending = False))['Date'].iloc[0]
    print(loc, 'now updated as of ' + str(nowUpdated), '\n')
    runCommand("UPDATE OREGON set Updated = '" + str(nowUpdated) + "', SpeciesTotal = " + str(total) + " WHERE County = '" + str(loc) + "';")

    years = data['Date'].str[:4].unique()
    updateYears(loc, getYears(loc), years)

    locs = data.drop_duplicates('Location')
    hotspots = getHotspots(loc)
    for row in locs.itertuples():
        totalSpecies = hotspotListCount(data, row.Location)
        if row.Location in hotspots:
            runCommand("UPDATE [" + loc + "] set Total_Species = " + str(totalSpecies) + ' WHERE Hotspot = "' + row.Location + '";')
        else:
            id = generateID(loc)
            command = "INSERT INTO [" + loc + "] (Hotspot, Hotspot_ID, Latitude, Longitude, Total_Species) "
            command += 'Values ("' + row.Location + '", ' + str(id) + ", '" + str(row.Latitude) + "', '" +  str(row.Longitude) + "', " + str(totalSpecies) + ");"
            runCommand(command)
    commands = []
    hotspots = getHotspots(loc)  #run this again because hotspots were updated 
    for hotspot in hotspots:
        for year in years:
            commands.append("UPDATE [" + loc + "] SET in" + str(year) + " = " + str(hotspotListCount(data, hotspot, year)) + ' WHERE Hotspot = "' + hotspot + '";')
    runCommands(commands)
    return

