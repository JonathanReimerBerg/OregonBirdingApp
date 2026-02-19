import pandas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

exclusions = ['Black Swan']

def cleanCSV(loc):       #mostly just removing columns we don't need, and then writing to new CSV file 
    data = pandas.read_csv('ProjectFiles/MyEBirdData.csv', low_memory=False)
    data.drop(columns = ['Scientific Name', 'Taxonomic Order', 'Distance Traveled (km)', 'Area Covered (ha)',
                     'Breeding Code', 'Observation Details', 'Checklist Comments', 'ML Catalog Numbers',
                     'Location ID', 'Latitude', 'Longitude', 'Time', 'Protocol', 'Duration (Min)',
                     'All Obs Reported', 'Number of Observers'], inplace = True)
    data.drop(data[data['State/Province'] != 'US-OR'].index, inplace = True)
    if loc != "Oregon":
        data.drop(data[data.County != loc].index, inplace = True)
    data.reset_index(drop = True, inplace = True)
    data.columns = [c.replace(' ', '_') for c in data.columns]
    data.to_csv('ProjectFiles/CSVs/' + loc + 'CleanedData.csv', encoding = 'utf-8', index = False)
    return(data)

def cleanList(lyst):
    newList = []
    for i in lyst:
        newList.append(i)
    return(newList)

def removeOtherTaxa(data):  #remove all non countable taxa, coultn't get all of these in one line
    data = data[~data.Common_Name.str.contains(" x ")]  
    data = data[~data.Common_Name.str.contains(" sp.")]   
    data = data[~data.Common_Name.str.contains("/")]
    data = data[~data.Common_Name.str.contains("Domestic")]
    data['Common_Name'] = data['Common_Name'].str.replace(r'\s+\([^()]*\)$', '', regex=True) #remove stuff in parenthesis
    for i in exclusions:
        data = data[~data.Common_Name.str.contains(i)]
    return(data)



def hotspotList(loc):  #will return the name of each location birds have been reported from
    data = pandas.read_csv('ProjectFiles/CSVs/' + loc + 'CleanedData.csv')
    hotspots = data['Location'].unique()
    hotspots.sort()
    return(cleanList(hotspots))

def scatterplot(species, loc): #create a scatterplot of all the reports of a species by time of year and count
    data = pandas.read_csv('ProjectFiles/CSVs/' + loc + 'CleanedData.csv')
    data.drop(data[data.Common_Name != species].index, inplace = True)  #remove everything but the target sp.

    data['Date'] = pandas.to_datetime(data['Date'])           
    data['Date'] = data['Date'].apply(lambda x: x.replace(year = 2024)) #make everything the same year (one with leap day)
    for i in data.index:
        if data.loc[i, "Count"] == 'X':    #need integer values only
            data.drop(i, inplace = True) 
    data['Count'] = data['Count'].apply(pandas.to_numeric) 
    
    plt.figure()
    plt.scatter(data['Date'], data['Count'])
    #plt.gcf().autofmt_xdate()      #different visual option
    
    date_format = mdates.DateFormatter('%b, %d')    #format the x-axis to show day/month instead of year
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.grid()

    fig = plt.gcf()   #formatting
    fig.set_size_inches(13, 7.5)
    plt.xlim([datetime.date(2024, 1, 1), datetime.date(2024, 12, 31)])    #make jan 1 with 0 count flush with the origin
    plt.ylim([0, data['Count'].max()*1.15])    #make a top margin
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.title(str(species) + ' in ' + loc)

    plt.show()

def simpleList(loc, year = None, asof = False):
    data = pandas.read_csv('ProjectFiles/CSVs/' + loc + 'CleanedData.csv')
    data = removeOtherTaxa(data)

    if year:
        if asof:
            data['Date'] = pandas.to_datetime(data['Date'])
            data = data[data['Date'].dt.year <= year]
        else:
            data = data[data.Date.str.contains(str(year))]

    data = data.drop_duplicates('Common_Name', keep='first')  #after sorting, keep the first occurence of each species
    return data['Common_Name']


def yearlist(loc, year = None, hotspot = None, last = False, sortByDate = True):   #print a list of species for a given year, can sort by first seen or last
    data = pandas.read_csv('ProjectFiles/CSVs/' + loc + 'CleanedData.csv')
    data = removeOtherTaxa(data)
    if year and year != 'Life':
        data = data[data.Date.str.contains(str(year))]  #include only species in given year
    if hotspot:
        data = data[data['Location'] == str(hotspot)]   #include only species from a given hotspot

    if sortByDate:
        data = data.sort_values('Date', kind = 'mergesort')

    if last:            #removing duplicates keeps the first occurence, so by flipping we can get the latest seen date instead
        data = data.reindex(index=data.index[::-1])
    data = data.drop_duplicates('Common_Name', keep='first')  #after sorting, keep the first occurence of each species

    firsts = [data['Common_Name'].values.tolist(), data['Date'].values.tolist(), data['Location'].values.tolist()]  #get all the data we want into a list to easily print  
    return(firsts)

def compareLists(county, year, hotspot):   #given two locations/times, find the differences in each list to each other
    list1 = yearlist(county[0], year[0], hotspot[0])
    list2 = yearlist(county[1], year[1], hotspot[1])
    loc1notloc2 = []
    loc2notloc1 = []
    for i in range(0, len(list1[0])):   #iterate through list 1, looking for birds not in list 2
        if list1[0][i] not in list2[0]:
            loc1notloc2.append([list1[0][i], list1[1][i], list1[2][i]])    #store differences
    for i in range(0, len(list2[0])):    #vice versa
        if list2[0][i] not in list1[0]:
            loc2notloc1.append([list2[0][i], list2[1][i], list2[2][i]])

    return([loc1notloc2, loc2notloc1])

def compareAll(locs):
    birdList = yearlist('Oregon')[0]

    allLocs = birdList[:]
    allButOneLocs = {}
    allButTwoLocs = {}
    onlyInLoc = {}
    eliminated = []

    for loc in locs:
        locList = yearlist(loc)[0]
        diffBirds = [bird for bird in birdList if bird not in locList]
        onlyInLoc[loc] = []
        for bird in diffBirds:
            if bird in allLocs:
                allLocs.remove(bird)
                allButOneLocs[bird] = loc
            elif bird in allButOneLocs:
                allButTwoLocs[bird] = [allButOneLocs[bird], loc]
                del allButOneLocs[bird]
            elif bird in allButTwoLocs:
                del allButTwoLocs[bird]
        for bird in locList:
            if all(bird not in sublist for sublist in onlyInLoc.values()) and (bird not in eliminated):
                onlyInLoc[loc].append(bird) 
            elif bird not in eliminated:
                for county in onlyInLoc.keys():
                    if bird in onlyInLoc[county]:
                        onlyInLoc[county].remove(bird)
                eliminated.append(bird)

    return([allLocs, allButOneLocs, allButTwoLocs, onlyInLoc])

def results_2025():
    All_Locations = ['Baker', 'Benton', 'Clackamas', 'Clatsop', 'Columbia', 'Coos', 'Crook', 'Curry', 'Deschutes', 'Douglas',
                    'Gilliam', 'Grant', 'Harney', 'Hood River', 'Jackson', 'Jefferson', 'Josephine', 'Klamath', 'Lake', 'Lane', 'Lincoln',
                    'Linn', 'Malheur', 'Marion', 'Morrow', 'Multnomah', 'Polk', 'Sherman', 'Tillamook', 'Umatilla', 'Union', 'Wallowa', 
                    'Wasco', 'Washington', 'Wheeler', 'Yamhill'] 
    Western_Half = ['Benton', 'Clackamas', 'Clatsop', 'Columbia', 'Coos', 'Curry', 'Douglas', 'Jackson', 'Josephine', 'Lane', 'Lincoln',
                    'Linn', 'Marion', 'Multnomah', 'Polk', 'Tillamook', 'Washington', 'Yamhill'] 
    Eastern_Half = ['Baker', 'Crook', 'Deschutes', 'Gilliam', 'Grant', 'Harney', 'Hood River', 'Jefferson', 'Klamath', 'Lake','Malheur', 
                'Morrow', 'Sherman', 'Umatilla', 'Union', 'Wallowa', 'Wasco', 'Wheeler'] 

    output = "Life List as of Dec 31, 2025 (threshold: 200) \n"
    output += str(len(simpleList('Oregon', 2025, True)))

    output += "\n\nYear List for 2025 (threshold: 200)\n"
    output += str(len(simpleList('Oregon', 2025, False)))

    output += "\n\nLife List for 18 Western Counties as of Dec 31, 2025 (threshold: 200)\n"
    westernLifeList = []
    for i in Western_Half:
        j = simpleList(i, 2025, True)
        for k in j:
            if k not in westernLifeList:
                westernLifeList.append(k)
    output += str(len(westernLifeList))

    output += "\n\nLife List for 18 Eastern Counties as of Dec 31, 2025 (threshold: 200)\n"
    easternLifeList = []
    for i in Eastern_Half:
        j = simpleList(i, 2025, True)
        for k in j:
            if k not in easternLifeList:
                easternLifeList.append(k)
    output += str(len(easternLifeList))

    output += "\n\nOREGON MOTORLESS BIRDING LIST: Your Oregon Motorless Life List (threshold: 100)\n(Must be calculated on own)"
    output += "\n\nYour Oregon Motorless 2025 List (threshold: 100)\n(Must be calculated on own)"
    output += "\n\nBIRDS PHOTOGRAPHED IN OREGON: Life List (threshold: 100)\n(Check eBird... functionality could be added in future)"
    output += "\n\nBIRDS RECORDED (AUDIO) IN OREGON: Life List (threshold: 50)\n(Check eBird... functionality could be added in future)"

    output += "\n\n-------------------- 2. OREGON COUNTIES LISTING -- Life Lists as of Dec 31, 2025 (threshold: 100)\n\n"
    for i in All_Locations:
        output += i + " Life List\n"
        output += str(len(simpleList(i, 2025, True))) + '\n\n'
        
    output += "-- TOTAL COUNTY TICKS (SUM OF 36 COUNTY LIFE LISTS): Life List (threshold: 2,000)\n"
    ticks  = 0
    for i in All_Locations:
        ticks += len(simpleList(i, 2025, True))
    output += str(ticks)

    output += "\n\n-- 2025 YEAR LISTS (threshold: 100)\n\n"
    for i in All_Locations:
        output += i + " 2025 List\n"
        output += str(len(simpleList(i, 2025, False))) + '\n\n'

    output += "-- TOTAL COUNTY YEAR TICKS (SUM OF 36 COUNTY 2025 YEAR LISTS): 500 or more\n"
    ticks  = 0
    for i in All_Locations:
        ticks += len(simpleList(i, 2025, False))
    output += str(ticks)

    output += "\n\nUse eBird patch/yard totals feature to calculate desired fields in sections 3"

    return output