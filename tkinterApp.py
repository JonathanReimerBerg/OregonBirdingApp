import tkinter as tk
from tkinter import ttk
import ProjectFiles.sql_methods as sm
import ProjectFiles.panda_methods as pm
import ProjectFiles.DB_writer as dw
import os

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



def displayText(text):
    print(text)

def callFunc(func):     #handles where to go from main window button presses
    if func in ["Lifelist", "Highcounts"]:
        inputWindow(root, func)
    elif func in ["Updatedata"]:     #some funcs don't require user inputs
        outputWindow(root, func)

def outputRequest(func, county, year, hotspot = None):     #calls output window after getting necessary inputs
    outputWindow(root, func, county, year, hotspot)


class outputWindow(tk.Toplevel):
    def __init__(self, master, func, county = None, year = None, hotspot = None):
        super().__init__(master)
        self.geometry('1000x900')
        self.configure(bg='#9eb5a1')
        self.counties = ['Oregon', 'Baker', 'Benton', 'Clackamas', 'Clatsop', 'Columbia', 'Coos', 'Crook', 'Curry', 'Deschutes', 'Douglas',
                    'Gilliam', 'Grant', 'Harney', 'Hood River', 'Jackson', 'Jefferson', 'Josaphine', 'Klamath', 'Lake', 'Lane', 'Lincoln',
                    'Linn', 'Malheur', 'Marion', 'Morrow', 'Multnomah', 'Polk', 'Sherman', 'Tillamook', 'Umatilla', 'Union', 'Wallawa', 
                    'Wasco', 'Washington', 'Wheeler', 'Yamhill']  #inlcuding the entire state as a location

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

    def generateTitle(self, master, type, county, year, hotspot = None):
        if hotspot:
            title = (hotspot + ', ' + county + ' ' + str(year) + ' ' + type)
        else:
            title = (county + ' ' + str(year) + ' ' + type)
        return title


    def lifeList(self, master, county, year, hotspot):   #these functions can be consolidated once outputs are all in the same format
        self.title(self.generateTitle(self, 'List', county, year, hotspot))
        if county:
            birdList = pm.yearlist(county, year, hotspot)
        else:
            birdList = pm.yearlist('Oregon', year, hotspot)
        output = ""
        for i in range(0, len(birdList[0])):
            output += str(i + 1) + ' '*(6 - len(str(i + 1))) + birdList[0][i] +  ' '*(30 - len(birdList[0][i])) + birdList[1][i] + '   ' + birdList[2][i][:60] + '\n'
        self.outputBox.insert(1.0, output)
        self.outputBox.config(state='disabled')

    def highCounts(self, master, county, year, hotspot):
        self.title(self.generateTitle(self, 'High Counts', county, year, hotspot))
        birdList = sm.highCounts(pm.yearlist(county)[0], year, county, hotspot)
        output = ""
        for i in birdList:
            output += str(i[0])
            output += '\n'
        self.outputBox.insert(1.0, output)
        self.outputBox.config(state='disabled')

    def updateData(self, master):
        self.outputBox.insert(1.0, 'Updating Data, this may take a while... \n Check the terminal window for updates.')
        self.update()
        for i in self.counties:
                if not os.path.isfile('ProjectFiles/DBs/' + i + 'Database.db'):
                    setupLoc(i)
                dw.updateDB(i)
        self.outputBox.delete(1.0, tk.END)
        self.outputBox.insert(1.0, 'Done')


class inputWindow(tk.Toplevel):     #allows the user to input a location/other info with a dynamic input window
    def __init__(self, master, func):
        super().__init__(master)
        self.geometry('300x400')
        self.title("Location Picker")
        self.func = func
        self.configure(bg='#9eb5a1')
        self.counties = ['Oregon', 'Baker', 'Benton', 'Clackamas', 'Clatsop', 'Columbia', 'Coos', 'Crook', 'Curry', 'Deschutes', 'Douglas',
                    'Gilliam', 'Grant', 'Harney', 'Hood River', 'Jackson', 'Jefferson', 'Josaphine', 'Klamath', 'Lake', 'Lane', 'Lincoln',
                    'Linn', 'Malheur', 'Marion', 'Morrow', 'Multnomah', 'Polk', 'Sherman', 'Tillamook', 'Umatilla', 'Union', 'Wallawa', 
                    'Wasco', 'Washington', 'Wheeler', 'Yamhill']
        self.years = ['Life', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025', '2026']
        
        self.countyLabel = tk.Label(self, text = "Pick a county:", font = ('Georgia', 10), bg='#9eb5a1')
        self.countyLabel.place(x = 90, y = 70)

        #box to choose a county
        self.entryBox = ttk.Combobox(self, values = self.counties, width = 12)
        self.entryBox.bind('<KeyRelease>', lambda event: self.filterOptions(self.counties, self.entryBox, event))
        self.entryBox.bind("<<ComboboxSelected>>", lambda event: self.checkEnableButton('box1', event))
        self.entryBox.place(x = 110, y = 100)

        #checkbox to allow searching by a specific hotspot
        self.incHotspots = tk.BooleanVar()
        self.enableHotspot = tk.Checkbutton(self, text = 'Search by hotspot?', font = 'georgia', bg = '#9eb5a1', selectcolor='#9eb5a1', 
                                            variable = self.incHotspots, command = lambda: self.checkEnableButton('checkbox', None))

        #box to choose a year (life by default)
        self.yearBox = ttk.Combobox(self, values = self.years, width = 12)
        self.yearBox.set('Life')
        self.yearBox.bind('<KeyRelease>', lambda event: self.filterOptions(self.years, self.yearBox, event))
        self.yearBox.place(x = 110, y = 250)

        #button to confirm selection / this button is only enabled when a valid set of options are selected
        self.select = tk.Button(self, height=1, width =7, relief = 'groove', font='georgia', bd=1, bg="#d6d6d6", 
                    text='Confirm', state = 'disabled', command = self.exitWindow)
        self.select.place(x = 210, y = 340)
        self.select.bind("<Enter>", lambda e: a.config(bg='#9e9e9d'))
        self.select.bind("<Leave>", lambda e: a.config(bg='#d6d6d6'))

    def filterOptions(self, locs, box, event): #filter options in a textbox based on a users input
        inp = box.get().lower()
        if inp == '':
            box["values"] = locs
        else:
            filteredOptions = []
            for loc in locs:
                if inp in loc.lower():
                    filteredOptions.append(loc)
            box["values"] = filteredOptions

    def hotspotEntry(self):   #box to choose a hotspot 
        loc = self.entryBox.get()
        hotspots = pm.hotspotList(loc)

        self.hotspotBox = ttk.Combobox(self, values = hotspots, width = 24)
        self.hotspotBox.bind('<KeyRelease>', lambda event: self.filterOptions(hotspots, self.hotspotBox, event))
        self.hotspotBox.bind("<<ComboboxSelected>>", lambda event: self.checkEnableButton('box2', event))
        self.hotspotBox.place(x = 80, y = 175)

    def checkEnableButton(self, caller, event):  #checks if we can enable the select button
        if caller == 'box1':
            if self.incHotspots.get():
                self.hotspotBox.destroy()
                self.enableHotspot.deselect()
            self.enableHotspot.place(x = 90, y = 140)
            self.select["state"] = 'active'
        if caller == 'checkbox':
            if self.incHotspots.get():
                self.select["state"] = 'disabled'
                self.hotspotEntry()
            else:
                self.select["state"] = 'active'
                self.hotspotBox.destroy()
        if caller == 'box2':
            self.select["state"] = 'active'


    def exitWindow(self):   #calls the next funtion and closes the window (depending on selection, there may be different outputs)
        if self.incHotspots.get():
            outputRequest(self.func, self.entryBox.get(), self.yearBox.get(), self.hotspotBox.get()), self.destroy()
        else:
            outputRequest(self.func, self.entryBox.get(), self.yearBox.get()), self.destroy()




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
                    text='Species Summary', command= lambda: displayText('Summary'))
d.place(x = 690, y = 180)
d.bind("<Enter>", lambda e: d.config(bg='#9e9e9d'))
d.bind("<Leave>", lambda e: d.config(bg='#d6d6d6'))

g = tk.Button(root, height=6, width=16, relief = 'groove', font = 'georgia', bd=1, bg="#d6d6d6", 
                    text='Compare 2 Lists', command= lambda: displayText('Diff'))
g.place(x = 860, y = 180)
g.bind("<Enter>", lambda e: g.config(bg='#9e9e9d'))
g.bind("<Leave>", lambda e: g.config(bg='#d6d6d6'))

f = tk.Button(root, height=6, width=16, relief = 'groove', font = 'georgia', bd=1, bg="#d6d6d6", 
                    text='Compare All Lists', command= lambda: displayText('Diff'))
f.place(x = 180, y = 320)
f.bind("<Enter>", lambda e: f.config(bg='#9e9e9d'))
f.bind("<Leave>", lambda e: f.config(bg='#d6d6d6'))

h = tk.Button(root, height=6, width=16, relief = 'groove', font = 'georgia', bd=1, bg="#d6d6d6", 
                    text='Listing Results', command= lambda: displayText('Send to Paul Sullivan'))
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