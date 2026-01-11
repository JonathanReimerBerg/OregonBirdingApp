#File used to create a DB from a downloaded CSV file from eBird.
#To update, just delete the DB and this will create a new one, I could implement
#a feature in the future to update the DB from an newer CSV file. 

import csv
import sqlite3
import re
from datetime import date

def runCommand(command, loc, fetchone = False, fetchall = False):
    connection = sqlite3.connect("ProjectFiles/DBs/" + loc + "Database.db")
    crsr = connection.cursor()
    try:
        crsr.execute(command)
    except:
        print(command)    #print the command if it doesn't work, usually a formatting issue when writing code
    result = crsr.fetchall()
    connection.commit()
    connection.close
    return(result)

def initializeDB(loc):
    command = """CREATE TABLE IF NOT EXISTS CHECKLISTS ( 
        ID varchar(64),
        Hotspot varchar(64),
        Time varchar(16),
        Month INTEGER varchar(2),
        Day INTEGER varchar(2),
        Year INTEGER varchar(4),
        Observers Integer varchar(2),
        UNIQUE(ID),
        CONSTRAINT CHECKLISTS_PK
        );"""

    runCommand(command, loc)   #create a table to store each checklists using its given ebird identifier

    command = """CREATE TABLE IF NOT EXISTS LAST_UPDATED (
        Year INTEGER, 
        Month INTEGER, 
        Day INTEGER
        );"""
    runCommand(command, loc)

    command = """INSERT INTO LAST_UPDATED (Year, Month, Day)
    SELECT 1899, 1, 1
    WHERE NOT EXISTS (SELECT 1 FROM LAST_UPDATED);"""
    runCommand(command, loc)   #if there are no values in table set default last update to Jan 1, 1899, just before the defualt life list entry for ebird


def updateDB(loc):
    lastUpdated = runCommand("SELECT Year, Month, Day from LAST_UPDATED;", loc)[0]
    lastUpdated = date(lastUpdated[0], lastUpdated[1], lastUpdated[2])
    print('\n' + loc,'last updated: ' + str(lastUpdated))
    nowUpdated = lastUpdated

    birds = runCommand("SELECT name FROM sqlite_master where type='table';", loc)  # a table for each species, using list to check dups
    birds = [item[0] for item in birds]
    lists = []  #checklists can show up multiple times in the data, so we should check dups

    with open('ProjectFiles/MyEBirdData.csv', 'r', encoding='utf') as file:
        reader = csv.reader(file)
        for row in reader:
            if ((row[6] == loc) or (loc == 'Oregon')) and (row[5] == 'US-OR'):    #database only being set up for Oregon
                ld = row[11].split('-')   #ld stands for list date, so we can update the nowUpdated to the latest checklist date added
                ld = date(int(ld[0]), int(ld[1]), int(ld[2]))
                if ld > lastUpdated:    #we only want to add new lists to the db
                    if ld > nowUpdated:
                        nowUpdated = ld
                    if row[0] not in lists:   #check if we arleady entered the checklist in 'checklists' table
                        values = '"'+row[0]+'","'+row[8]+'","'+row[12]+'''
                            ",'''+row[11][5:7]+','+row[11][8:10]+','+row[11][0:4]+','+row[18] 
                        command = '''INSERT INTO CHECKLISTS (ID, Hotspot, Time, Month, Day, Year, Observers)
                            VALUES (''' + values + ''');'''
                        runCommand(command, loc)
                        lists.append(row[0])

                    if '(' in row[1]:      #basically removes sub-taxa
                        row[1] = re.sub(r"\((.*?)\)", "", row[1])[:-1]
                    
                    if row[1] not in birds:   #if we don't have a table for that bird yet
                        command = ("CREATE TABLE if not exists '" + str(row[1].replace("'","''")) + "'" + '''(
                            Checklist varchar(10),
                            Count INTEGER varchar(5),
                            Year varchar(4));''')
                        runCommand(command, loc)
                        birds.append(row[1])
                        print(row[1], ' added')

                    if row[4] == 'X':   #integers only, defaulting to 1 bird seen
                        row[4] = str(1)

                    command = ("INSERT INTO '" + str(row[1].replace("'","''")) + "'(Checklist, Count, Year) VALUES" + '''
                        ("''' + str(row[0]) + '", ' + row[4] + ', "' + str(row[11][0:4]) + '");')
                    runCommand(command, loc)   #adds the report to the species table


    runCommand("UPDATE LAST_UPDATED set Year = " + str(nowUpdated.year) + ", Month = " + str(nowUpdated.month) + ", Day = " + str(nowUpdated.day) + ";", loc)

    print(loc, 'data done, now updated as of ' + str(nowUpdated), '\n')
            

#The following code fragment can create a table for each checklist, which is much less efficient
    
#command = ('CREATE TABLE if not exists ' + str(row[0]) + '''(Species varchar(64),
#                Count INTEGER varchar(5), CONSTRAINT ''' + str(row[0]) + '_PK);')
#            runCommand(command)

#            if row[4] == 'X':
#                row[4] = str(1)

#            command = ('INSERT INTO ' + str(row[0]) + '''(Species, Count) VALUES
#                ("''' + str(row[1]) + '", ' + row[4] + ');')
#            runCommand(command)
