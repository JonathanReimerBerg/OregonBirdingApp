import sqlite3

All_Counties = ['Baker', 'Benton', 'Clackamas', 'Clatsop', 'Columbia', 'Coos', 'Crook', 'Curry', 'Deschutes', 'Douglas',
                    'Gilliam', 'Grant', 'Harney', 'Hood River', 'Jackson', 'Jefferson', 'Josephine', 'Klamath', 'Lake', 'Lane', 'Lincoln',
                    'Linn', 'Malheur', 'Marion', 'Morrow', 'Multnomah', 'Polk', 'Sherman', 'Tillamook', 'Umatilla', 'Union', 'Wallowa', 
                    'Wasco', 'Washington', 'Wheeler', 'Yamhill']

def runCommand(command, fetchone = False, fetchall = False):
    connection = sqlite3.connect('ProjectFiles/MainDatabase.db')
    crsr = connection.cursor()
    try:
        crsr.execute(command)
    except:
        print(command)
    result = crsr.fetchall()
    connection.commit()
    connection.close
    return(result)

def hotspotsRank(loc, year):
    masterList = []
    if year == 'Life':
        yearval = "Total_Species"
    else:
        yearval = "in" + str(year)
    for county in All_Counties:
        if county == loc or loc == 'Oregon':     #when 'Oregon' is selected, we do all counties
            columns = []
            for column in [i[1] for i in runCommand("PRAGMA table_info('" + county + "')")]:   #gets all column names and then writes them to new variable
                columns.append(column)
            if yearval in columns:        
                hotspots = runCommand("SELECT Hotspot, Hotspot_ID, " + yearval + " From [" + county + "]")
            else:                   # if column doesn't exist, we know each value is zero and don't need to retrive it and get an error
                hotspots = runCommand("SELECT Hotspot, Hotspot_ID From [" + county + "]")
                hotspots = [tup + (0,) for tup in hotspots]
            for hotspot in hotspots:
                masterList.append(hotspot)
    return(masterList)



