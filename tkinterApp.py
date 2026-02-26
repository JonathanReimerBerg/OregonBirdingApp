import tkinter as tk
from tkinter import ttk

import ProjectFiles.sql_methods as sm
import ProjectFiles.panda_methods as pm
import ProjectFiles.DB_writer as dw

import os

All_Locations = ['Oregon', 'Baker', 'Benton', 'Clackamas', 'Clatsop', 'Columbia', 'Coos', 'Crook', 'Curry', 'Deschutes', 'Douglas',
                    'Gilliam', 'Grant', 'Harney', 'Hood River', 'Jackson', 'Jefferson', 'Josephine', 'Klamath', 'Lake', 'Lane', 'Lincoln',
                    'Linn', 'Malheur', 'Marion', 'Morrow', 'Multnomah', 'Polk', 'Sherman', 'Tillamook', 'Umatilla', 'Union', 'Wallowa', 
                    'Wasco', 'Washington', 'Wheeler', 'Yamhill'] #all Oregon counties and the state itself

#Create the opening window 
root = tk.Tk()
root.geometry('1200x800')
root.title("Oregon Birding App")
root.configure(bg='#9eb5a1')


def setupLoc(loc, new = False):  #adds location to the list of databases/csv's
    if new:         #create directory if this is the first location
        os.mkdir('ProjectFiles/DBs')
        os.mkdir('ProjectFiles/CSVs')
    dw.initializeDB(loc)
    pm.cleanCSV(loc)
    return

def checkIfNew():       #checks if a location has been initialized
    if not os.path.isfile('ProjectFiles/DBs/OregonDatabase.db'):
        setupLoc('Oregon', True)


def getInput(hotspot, year, species):
    selectInput = inputWindow(root, hotspot, year, species)
    input = selectInput.retrieve()
    selectInput.destroy()
    return input

def callFunc(func):     #handles where to go from main window button presses
    if func in ["CompareLists"]:
        loc1 = getInput(True, True, False)
        loc2 = getInput(True, True, False)
        outputWindow(root, func, [loc1[0], loc2[0]], [loc1[1], loc2[1]], [loc1[2], loc2[2]])
    elif func in ["Lifelist", "Highcounts"]:
        loc = getInput(True, True, False)
        outputWindow(root, func, loc[0], loc[1], loc[2])
    elif func in ["Updatedata", "CompareAll", "ListingResults"]:     #some funcs don't require user inputs
        outputWindow(root, func)
    elif func in ["SpeciesSummary"]:
        loc = getInput(False, False, True)
        outputWindow(root, func, loc[0], loc[1], loc[2], loc[3])



class outputWindow(tk.Toplevel):
    def __init__(self, master, func, county = None, year = None, hotspot = None, species = None):
        super().__init__(master)
        self.geometry('1000x900')
        self.configure(bg='#9eb5a1')

        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.outputBox = tk.Text(self, bg='#9eb5a1', yscrollcommand= 'true')
        self.outputBox.pack(fill=tk.BOTH, expand=True)
        self.outputBox['yscrollcommand'] = self.scrollbar.set # Text updates scrollbar
        self.scrollbar.config(command=self.outputBox.yview)

        if func == "Lifelist":
            self.lifeList(self, county, year, hotspot)
        if func == "Highcounts":
            self.highCounts(self, county, year, hotspot)
        if func == "Updatedata":
            self.updateData(self)
        if func == "CompareLists":
            self.compareLists(self, county, year, hotspot)
        if func == "CompareAll":
            self.compareAll(self)
        if func == "SpeciesSummary":
            self.speciesSummary(self, county, year, hotspot, species)
        if func == "ListingResults":
            self.listingResults(self)

    def generateTitle(self, master, type, county, year, hotspot = None):
        if hotspot:
            title = (hotspot + ', ' + county + ' ' + str(year) + ' ' + type)
        else:
            title = (county + ' ' + str(year) + ' ' + type)
        return title


    def lifeList(self, master, county, year, hotspot):   #these functions can be consolidated once outputs are all in the same format
        self.title(self.generateTitle(self, 'List', county, year, hotspot))
        birdList = pm.yearlist(county, year, hotspot)
        output = ""
        for i in range(0, len(birdList[0])):
            output += str(i + 1) + ' '*(6 - len(str(i + 1))) + birdList[0][i] +  ' '*(30 - len(birdList[0][i])) + birdList[1][i] + '   ' + birdList[2][i][:60] + '\n'
        self.outputBox.insert(1.0, output)
        self.outputBox.config(state='disabled')

    def highCounts(self, master, county, year, hotspot):
        self.title(self.generateTitle(self, 'High Counts', county, year, hotspot))
        birdList = sm.highCounts(pm.yearlist(county, None, None, False, False)[0], year, county, hotspot)
        output = ""
        for i in birdList:
            output += str(i[0])
            output += '\n'
        self.outputBox.insert(1.0, output)
        self.outputBox.config(state='disabled')

    def updateData(self, master):
        self.outputBox.insert(1.0, 'Updating Data, this may take a while... \n Check the terminal window for updates.')
        self.update()
        for i in All_Locations:
                if not os.path.isfile('ProjectFiles/DBs/' + i + 'Database.db'):
                    setupLoc(i)
                dw.updateDB(i)
                pm.cleanCSV(i)
        self.outputBox.delete(1.0, tk.END)
        self.outputBox.insert(1.0, 'Done')

    def compareLists(self, master, county, year, hotspot):
        self.title("List Comparison")
        birdLists = pm.compareLists(county, year, hotspot)

        hotspot = ['' if item is None else (' ' + str(item)) for item in hotspot]  #just for organizing section headers in the output for spacing/ not saying 'none' 

        output = 'Birds seen in' + str(hotspot[0]) + ' ' + str(county[0]) + ', ' + str(year[0]) + ' not in' + str(hotspot[1]) + ' ' + str(county[1]) + ', ' + str(year[1]) + '\n\n'
        for i in range(0, len(birdLists[0])):
            output += str(i + 1) + ' '*(6 - len(str(i + 1))) + birdLists[0][i][0] +  ' '*(30 - len(birdLists[0][i][0])) + birdLists[0][i][1] + '   ' + birdLists[0][i][2][:60] + '\n'

        output += '\nBirds seen in ' + str(hotspot[1]) + ' ' + str(county[1]) + ', ' + str(year[1]) + ' not in ' + str(hotspot[0]) + ' ' + str(county[0]) + ', ' + str(year[0]) + '\n\n'
        for i in range(0, len(birdLists[1])):
            output += str(i + 1) + ' '*(6 - len(str(i + 1))) + birdLists[1][i][0] +  ' '*(30 - len(birdLists[1][i][0])) + birdLists[1][i][1] + '   ' + birdLists[1][i][2][:60] + '\n'

        self.outputBox.insert(1.0, output)
        self.outputBox.config(state='disabled')

    def compareAll(self, master):
        lists = pm.compareAll(All_Locations[1::])
        self.title("All counties comparison")

        output = "Birds seen in all 36 Oregon Counties: \n\n"
        for i in lists[0]:
            output += i + '\n'
        output += '\nBirds seen in all but 1 Oregon Counties: (missing county)\n\n'
        for i in lists[1]:
            output += i + '   (' + lists[1][i] + ')\n'
        output += '\nBirds seen in all but 2 Oregon Counties: (missing counties)\n\n'
        for i in lists[2]:
            output += i + '   (' + lists[2][i][0] + ', ' + lists[2][i][1] + ')\n'
        output += '\n\n\nBirds seen in only 1 Oregon County: \n\n'
        for i in lists[3]:
            if lists[3][i]:
                output += i + '\n'
                for j in lists[3][i]:
                    output += '   ' + j + '\n'
                output += '\n'

        self.outputBox.insert(1.0, output)
        self.outputBox.config(state='disabled')

    def speciesSummary(self, master, county, year, hotspot, species):
        self.title(species + " in " + self.generateTitle(self, 'List', county, year, hotspot))
        birdlist = sm.speciesData(species, county)
        output = ''
        for i in birdlist:
            output += str(i[0]) + "-" + str(i[1]) + "-" + str(i[2]) + " "*(7-(len(str(i[0])) + len(str(i[1])))) + str(i[4]) + " "*(7-len(str(i[4]))) + str(i[3]) + '\n'
        self.outputBox.insert(1.0, output)
        self.outputBox.config(state='disabled')
        pm.scatterplot(species, county)

    def listingResults(self, master):
        self.title("2025 Oregon Listing Results")
        output = pm.results_2025()
        self.outputBox.insert(1.0, output)
        self.outputBox.config(state='disabled')


class inputWindow(tk.Toplevel):     #allows the user to input a location/other info with a dynamic input window
    def __init__(self, master, inchotspot, incyear, incspecies):
        super().__init__(master)
        self.geometry('300x400')
        self.title("Location Picker")
        self.configure(bg='#9eb5a1')
        self.inputVal = tk.StringVar()
        self.inchotspot = inchotspot
        self.incyear = incyear
        self.incspecies = incspecies

        #box to choose a county
        self.countyLabel = tk.Label(self, text = "Pick a county:", font = ('Georgia', 11), bg='#9eb5a1')
        self.countyLabel.place(x = 90, y = 50)

        self.countyBox = ttk.Combobox(self, values = All_Locations, width = 12)
        self.countyBox.bind('<KeyRelease>', lambda event: self.filterOptions(All_Locations, self.countyBox, event))
        self.countyBox.bind("<<ComboboxSelected>>", lambda event: self.checkEnableButton('countybox', event))
        self.countyBox.place(x = 110, y = 80)

        #checkbox to allow searching by a specific hotspot
        if self.inchotspot:
            self.incHotspotsChecked = tk.BooleanVar()
            self.enableHotspot = tk.Checkbutton(self, text = 'Search by hotspot?', font = 'georgia', bg = '#9eb5a1', selectcolor='#9eb5a1', 
                                                variable = self.incHotspotsChecked, command = lambda: self.checkEnableButton('checkbox', None))

        #box to choose a year (life by default)
        if self.incyear:
            self.years = pm.getYears('Oregon')
            self.yearLabel = tk.Label(self, text = "Pick a year:", font = ('Georgia', 11), bg='#9eb5a1')
            self.yearLabel.place(x = 90, y = 200)

            self.yearBox = ttk.Combobox(self, values = self.years, width = 12)
            self.yearBox.set('Life')
            self.yearBox.bind('<KeyRelease>', lambda event: self.filterOptions(self.years, self.yearBox, event))
            self.yearBox.place(x = 110, y = 230)

        #box to choose a species (actual box added later like hotspot entry)
        if self.incspecies:
            self.speciesLabel = tk.Label(self, text = "Pick a species:", font = ('Georgia', 11), bg='#9eb5a1')
            self.speciesLabel.place(x = 90, y = 260)

        #button to confirm selection / this button is only enabled when a valid set of options are selected
        self.select = tk.Button(self, height=1, width =7, relief = 'groove', font='georgia', bd=1, bg="#d6d6d6", 
                    text='Confirm', state = 'disabled', command = self.setInputVal)
        self.select.place(x = 210, y = 340)
        self.select.bind("<Enter>", lambda e: a.config(bg='#9e9e9d'))
        self.select.bind("<Leave>", lambda e: a.config(bg='#d6d6d6'))

    def filterOptions(self, items, box, event): #filter options in a textbox based on a users input
        inp = box.get().lower()
        if inp == '':
            box["values"] = items
        else:
            filteredOptions = []
            for item in items:
                if inp in item.lower():
                    filteredOptions.append(item)
            box["values"] = filteredOptions

    def hotspotEntry(self):   #box to choose a hotspot 
        loc = self.countyBox.get()
        hotspots = pm.hotspotList(loc)

        self.hotspotBox = ttk.Combobox(self, values = hotspots, width = 24)
        self.hotspotBox.bind('<KeyRelease>', lambda event: self.filterOptions(hotspots, self.hotspotBox, event))
        self.hotspotBox.bind("<<ComboboxSelected>>", lambda event: self.checkEnableButton('hotspotbox', event))
        self.hotspotBox.place(x = 80, y = 155)

    def speciesEntry(self):
        loc = self.countyBox.get()
        species = pm.simpleList(loc)

        self.speciesBox = ttk.Combobox(self, values = species, width = 12)
        self.speciesBox.bind('<KeyRelease>', lambda event: self.filterOptions(species, self.speciesBox, event))
        self.speciesBox.bind("<<ComboboxSelected>>", lambda event: self.checkEnableButton('speciesbox', event))
        self.speciesBox.place(x = 110, y = 290)

    def checkEnableButton(self, caller, event):  #checks if we can enable the select button
        if caller == 'countybox':
            if (not self.inchotspot) and (not self.incspecies):
                self.select["state"] = 'active'
                return
            if self.inchotspot and self.incHotspotsChecked.get():
                self.hotspotBox.destroy()
                self.enableHotspot.deselect()
            if self.inchotspot:
                self.enableHotspot.place(x = 90, y = 120)
                self.select["state"] = 'active'
            if self.incspecies:
                self.speciesEntry()
                self.select["state"] = 'disabled'

        if caller == 'checkbox':
            if self.incHotspotsChecked.get():
                self.select["state"] = 'disabled'
                self.hotspotEntry()
            else:
                self.select["state"] = 'active'
                self.hotspotBox.destroy()

        if caller in ['hotspotbox', 'speciesbox']:
            self.select["state"] = 'active'


    def setInputVal(self):   #calls the next funtion and closes the window (depending on selection, there may be different outputs)
        self.input = [self.countyBox.get()]
        if self.incyear:
            self.input.append(self.yearBox.get())
        else:
            self.input.append(None)
        if  self.inchotspot and self.incHotspotsChecked.get():
            self.input.append(self.hotspotBox.get())
        else:
            self.input.append(None)
        if self.incspecies:
            self.input.append(self.speciesBox.get())
        else:
            self.input.append(None)
        self.inputVal.set('ready')

    def retrieve(self):
        self.wait_variable(self.inputVal)
        return self.input



label = tk.Label(root, text = "Welcome to my Oregon Birding App! \n\n Please select an option below:", font = ('Georgia', 18), bg='#9eb5a1')
label.pack(padx=20, pady=40)


#all the main window function options, as buttons
a = tk.Button(root, height=6, width = 16, relief = 'groove', font='georgia', bd=1, bg="#d6d6d6", 
                    text='Print List', command= lambda: callFunc("Lifelist"))
a.place(x = 180, y = 180)
a.bind("<Enter>", lambda e: a.config(bg='#9e9e9d'))   #color of box changes slightly to show when user is hovering over it
a.bind("<Leave>", lambda e: a.config(bg='#d6d6d6'))

b = tk.Button(root, height=6, width=16, relief = 'groove', font = 'georgia', bd=1, bg="#d6d6d6",
                    text='High Counts', command= lambda: callFunc("Highcounts"))
b.place(x = 350, y = 180)
b.bind("<Enter>", lambda e: b.config(bg='#9e9e9d'))
b.bind("<Leave>", lambda e: b.config(bg='#d6d6d6'))

c = tk.Button(root, height=6, width=16, relief = 'groove', font = 'georgia', bd=1, bg="#d6d6d6", 
                    text='Update Data', command= lambda: callFunc('Updatedata'))
c.place(x = 520, y = 180)
c.bind("<Enter>", lambda e: c.config(bg='#9e9e9d'))
c.bind("<Leave>", lambda e: c.config(bg='#d6d6d6'))

d = tk.Button(root, height=6, width=16, relief = 'groove', font = 'georgia', bd=1, bg="#d6d6d6", 
                    text='Species Summary', command= lambda: callFunc('SpeciesSummary'))
d.place(x = 690, y = 180)
d.bind("<Enter>", lambda e: d.config(bg='#9e9e9d'))
d.bind("<Leave>", lambda e: d.config(bg='#d6d6d6'))

g = tk.Button(root, height=6, width=16, relief = 'groove', font = 'georgia', bd=1, bg="#d6d6d6", 
                    text='Compare 2 Lists', command= lambda: callFunc('CompareLists'))
g.place(x = 860, y = 180)
g.bind("<Enter>", lambda e: g.config(bg='#9e9e9d'))
g.bind("<Leave>", lambda e: g.config(bg='#d6d6d6'))

f = tk.Button(root, height=6, width=16, relief = 'groove', font = 'georgia', bd=1, bg="#d6d6d6", 
                    text='Compare All \n Counties', command= lambda: callFunc('CompareAll'))
f.place(x = 180, y = 320)
f.bind("<Enter>", lambda e: f.config(bg='#9e9e9d'))
f.bind("<Leave>", lambda e: f.config(bg='#d6d6d6'))

h = tk.Button(root, height=6, width=16, relief = 'groove', font = 'georgia', bd=1, bg="#d6d6d6", 
                    text='Listing Results', command= lambda: callFunc('ListingResults'))
h.place(x = 350, y = 320)
h.bind("<Enter>", lambda e: h.config(bg='#9e9e9d'))
h.bind("<Leave>", lambda e: h.config(bg='#d6d6d6'))

quit = tk.Button(root, height=2, width=15, relief = 'groove', font = 'georgia', bd=1, bg="#c99191", 
                    text='quit', command= lambda: root.destroy())       #since all other windows are from this parent window, this button (or 'x') close all windows
quit.place(x = 950, y = 700)
quit.bind("<Enter>", lambda e: quit.config(bg='red'))
quit.bind("<Leave>", lambda e: quit.config(bg='#c99191'))

if __name__ == '__main__':
    checkIfNew()  #checks if this is the first time the program has run


root.mainloop()  #shows main window