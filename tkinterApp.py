import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import webbrowser as wb

import ProjectFiles.sql_methods as sm
import ProjectFiles.panda_methods as pm
import ProjectFiles.DB_writer as dw

import os
import shutil

All_Locations = ['Oregon', 'Baker', 'Benton', 'Clackamas', 'Clatsop', 'Columbia', 'Coos', 'Crook', 'Curry', 'Deschutes', 'Douglas',
                    'Gilliam', 'Grant', 'Harney', 'Hood River', 'Jackson', 'Jefferson', 'Josephine', 'Klamath', 'Lake', 'Lane', 'Lincoln',
                    'Linn', 'Malheur', 'Marion', 'Morrow', 'Multnomah', 'Polk', 'Sherman', 'Tillamook', 'Umatilla', 'Union', 'Wallowa', 
                    'Wasco', 'Washington', 'Wheeler', 'Yamhill'] #all Oregon counties and the state itself

#Create the opening window 
root = tk.Tk()
root.geometry('1200x800')
root.title("Oregon Birding App")
root.configure(bg='#9eb5a1')


def checkIfNew():       #checks if a location has been initialized
    if not os.path.isfile('ProjectFiles/MainDatabase.db'):
        dw.initializeDB()
    if not os.path.isdir('ProjectFiles/CSVs'):
        os.mkdir('ProjectFiles/CSVs')
        for loc in All_Locations:
            pm.cleanCSV(loc)

def popupWindow(title, message, func):
    result = messagebox.askyesno(title, message)
    if result:
        func()

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
    elif func in ["CompareAll", "ListingResults"]:     #some funcs don't require user inputs
        outputWindow(root, func)
    elif func in ["SpeciesSummary"]:
        loc = getInput(False, False, True)
        outputWindow(root, func, loc[0], loc[1], loc[2], loc[3])
    elif func in ["HotspotsRank"]:
        loc = getInput(False, True, False)
        outputWindow(root, func, loc[0], loc[1], loc[2])



class outputWindow(tk.Toplevel):
    def __init__(self, master, func, county = None, year = None, hotspot = None, species = None):
        super().__init__(master)
        self.geometry('1100x900')
        self.configure(bg='#9eb5a1')
        self.buttons = []

        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.outputBox = tk.Text(self, bg='#9eb5a1', yscrollcommand= 'true')
        self.outputBox.pack(fill=tk.BOTH, expand=True)
        self.outputBox['yscrollcommand'] = self.scrollbar.set 
        self.scrollbar.config(command=self.outputBox.yview)

        if func == "Lifelist":
            self.lifeList(self, county, year, hotspot)
        if func == "Highcounts":
            self.highCounts(self, county, year, hotspot)
        if func == "CompareLists":
            self.compareLists(self, county, year, hotspot)
        if func == "CompareAll":
            self.compareAll(self)
        if func == "SpeciesSummary":
            self.speciesSummary(self, county, year, hotspot, species)
        if func == "ListingResults":
            self.listingResults(self)
        if func == "HotspotsRank":
            self.hotspotRank(self, county, year)

    def generateTitle(self, master, type, county, year, hotspot = None):    #dynamically creates title for output page
        if hotspot:
            title = (hotspot + ', ' + county + ' ' + str(year) + ' ' + type)
        else:
            title = (county + ' ' + str(year) + ' ' + type)
        return title

    def linkbuttons(self, master, char_pos, submission_ids, startpoint = 0):   #creates links to checklists for each entry at a given index
        wb.register('Chrome', None, wb.BackgroundBrowser(r'C:\Program Files\Google\Chrome\Application\chrome.exe'))   #set chrome as default, may add preferences in future
        for i in range(0, len(submission_ids)):
            link_button = tk.Button(self.outputBox, text="\U0001F517", command = lambda id = submission_ids[i]: wb.get('chrome').open("ebird.org/checklist/" + str(id)), 
                                    font = ("Goergia", 7), width=1, height=1, bg = '#9eb5a1', padx = 0, pady = 0, relief="flat")
            self.buttons.append(link_button)
            self.outputBox.window_create(i + 1 + startpoint + char_pos, window = link_button)    #creates button at dynamically located spot (usually immediately after date)
        return
    
    def clearButtons(self, master):    #deletes all buttons that get replaced when the output page is reset (such as when the page is sorted)
        for i in self.buttons:
            i.destroy()
        return
    
    def sortMenu(self, master, function, inputs, options):     #creates a button with different sort options that recreates the page when one is selected
        sortMenu = tk.Menubutton(self, text = '\u21F5', bg='#9eb5a1', font = ("Georgia", 16))    #creates basic buttons
        sortMenu.place(relx = 1.0, rely = 0.0, anchor = 'ne', x = -20, y = 5)
        self.buttons.append(sortMenu)

        menu = tk.Menu(sortMenu, tearoff=0)
        sortMenu['menu'] = menu     #adds the menu to the button
        for i in options:          #adds each otpion to the menu, calling necessary functions to delete the content and add it back. getattr allows for dynamic function calling
            menu.add_command(label = i, command = lambda sort = i: [self.outputBox.config(state='normal'), self.clearButtons(self),
                                                                    self.outputBox.delete("1.0", tk.END), getattr(self, function)(self, inputs[0], inputs[1], inputs[2], sort)])
        return
    


    def lifeList(self, master, county, year, hotspot, sort = 'First Seen'):   #these functions can be consolidated once outputs are all in the same format
        self.title(self.generateTitle(self, 'List', county, year, hotspot))
        birdList = pm.dynamicList('basic', county, year, hotspot, sort)
        output = ""
        for i in range(0, len(birdList[0])):
            output += str(i + 1) + ' '*(6 - len(str(i + 1))) + birdList[0][i] +  ' '*(32 - len(birdList[0][i])) + birdList[1][i] + '     ' + birdList[2][i][:60] + '\n'
        self.outputBox.insert(1.0, output)
        self.linkbuttons(self, 0.48, birdList[3])    #places buttons at 48th character in each row
        self.sortMenu(self, 'lifeList', [county, year, hotspot], ['First Seen', 'Last Seen', 'Taxanomic'])
        self.outputBox.config(state='disabled')     #otherwise user can type in box

    def highCounts(self, master, county, year, hotspot, sort = 'Taxanomic'):
        self.title(self.generateTitle(self, 'High Counts', county, year, hotspot))
        birdList = pm.dynamicList('high counts', county, year, hotspot, sort)
        output = ""
        for i in range(0, len(birdList[0])):
            output += str(birdList[0][i]) + '  ' + ' '*(5-len(str(birdList[0][i]))) + birdList[1][i] + ' '*(31-len(birdList[1][i])) + birdList[2][i] + '     ' + birdList[3][i][:60] + '\n'
        self.outputBox.insert(1.0, output)
        self.linkbuttons(self, 0.48, birdList[4])
        self.sortMenu(self, 'highCounts', [county, year, hotspot], ['Taxanomic', 'High Count', 'Date'])
        self.outputBox.config(state='disabled')

    def compareLists(self, master, county, year, hotspot, sort = 'First Seen'):
        self.title("List Comparison")
        birdLists = pm.compareLists(county, year, hotspot, sort)

        hotspot = ['' if item is None else ('' + str(item)) for item in hotspot]  #just for organizing section headers in the output for spacing/ not saying 'none' 

        output = 'Birds seen in ' + str(hotspot[0]) + ' ' + str(county[0]) + ', ' + str(year[0]) + ' not in' + str(hotspot[1]) + ' ' + str(county[1]) + ', ' + str(year[1]) + '\n\n'
        for i in range(0, len(birdLists[0])):
            output += str(i + 1) + ' '*(6 - len(str(i + 1))) + birdLists[0][i][0] +  ' '*(30 - len(birdLists[0][i][0])) + birdLists[0][i][1] + '   ' + birdLists[0][i][2][:60] + '\n'

        output += '\nBirds seen in ' + str(hotspot[1]) + ' ' + str(county[1]) + ', ' + str(year[1]) + ' not in ' + str(hotspot[0]) + ' ' + str(county[0]) + ', ' + str(year[0]) + '\n\n'
        for i in range(0, len(birdLists[1])):
            output += str(i + 1) + ' '*(6 - len(str(i + 1))) + birdLists[1][i][0] +  ' '*(30 - len(birdLists[1][i][0])) + birdLists[1][i][1] + '   ' + birdLists[1][i][2][:60] + '\n'

        self.outputBox.insert(1.0, output)
        self.linkbuttons(self, 0.46, [tup[3] for tup in birdLists[0]], 2)
        self.linkbuttons(self, 0.46, [tup[3] for tup in birdLists[1]], 5 + len(birdLists[0]))  #two different sets since were outputting 2 lists of birds
        self.sortMenu(self, 'compareLists', [county, year, hotspot], ['First Seen', 'Last Seen', 'Taxanomic'])
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
        birdList = pm.speciesOccurence(species, county)
        output = ''
        for i in range(0, len(birdList[0])):
            output += birdList[0][i] + "      " + str(birdList[1][i]) + " "*(10-len(str(birdList[1][i]))) + birdList[2][i] + '\n'
        self.outputBox.insert(1.0, output)
        self.linkbuttons(self, 0.11, birdList[3])
        self.outputBox.config(state='disabled')
        pm.scatterplot(species, county)

    def listingResults(self, master):
        self.title("2025 Oregon Listing Results")
        output = pm.results_2025()
        self.outputBox.insert(1.0, output)
        self.outputBox.config(state='disabled')

    def hotspotRank(self, master, loc, year):
        self.title(loc + " " + year + " Hotspot Rankings")
        hotspots = sm.hotspotsRank(loc, year)
        hotspots.sort(key = lambda x: x[2], reverse = True)
        output = ''

        for i in hotspots:
            output += str(i[2]) + " "*(8-len(str(i[2]))) + i[0] + '\n'

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


def updateData():
    popup = tk.Toplevel(root)
    popup.title("Updating")
    popup.geometry("260x120")
    popup.configure(bg='#9eb5a1')
    label = tk.Label(popup, text = "     Updating...\nPlease do not close\n\nWorking on: Baker", bg = '#9eb5a1', font = ('georgia', 14))
    label.pack()
    for loc in All_Locations:
        label.config(text=f"     Updating...\nPlease do not close\n\nWorking on: " + loc)
        popup.update()
        total = pm.updateData(loc)
        dw.updateDB(loc, total)
    label.config(text=f"Completed\nYou are free to use the app")
    return

def importCSV():       #allows the user to select a file name 'MyEBirdData.csv', and gets copied into expected location in 'ProjectFiles'
    sourcePath = filedialog.askopenfilename(title = "Select an eBird CSV file", filetypes = ((f"{"MyEBirdData.csv"} file", "MyEBirdData.csv"),))
    if not sourcePath:
        return
    destinationPath = os.path.abspath(__file__)[:-13] + "ProjectFiles"

    file_name = os.path.basename(sourcePath)
    destination_path = os.path.join(destinationPath, file_name)
    shutil.copy(sourcePath, destination_path)
    messagebox.showinfo("Success", f"File successfully uploaded to: {destination_path}")   #confirmation message
    checkIfNew()


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
                    text='Hotspot \n Rankings', command= lambda: callFunc('HotspotsRank'))
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

frame_separator = tk.Frame(root, height=1, bg="black", bd=0)
frame_separator.pack(fill = 'x', pady = 130, side = "bottom")

importButton = tk.Button(root, relief = 'groove', bd = 1, text="\u2913", font = ('Georgia', 15), bg='#d6d6d6', command=lambda: importCSV())
importButton.place(x = 80, y = 690, width = 32, height = 32)
importLabel = tk.Label(root, text = "Import eBird CSV and Update", font = ('Georgia', 11), bg='#9eb5a1')
importLabel.place(x = 120, y = 690)

updateButton = tk.Button(root, relief = 'groove', bd = 1, text="\u21bb", font = ('Georgia', 15), bg='#d6d6d6', 
                    command=lambda: popupWindow("Update Data: Confirmation", "WARNING, this may take a while.", updateData))
updateButton.place(x = 80, y = 740, width = 32, height = 32)
updateLabel = tk.Label(root, text = "Update Hotspot Data", font = ('Georgia', 11), bg='#9eb5a1')
updateLabel.place(x = 120, y = 740)

quit = tk.Button(root, height=2, width=15, relief = 'groove', font = 'georgia', bd=1, bg="#c99191", 
                    text='quit', command= lambda: root.destroy())       #since all other windows are from this parent window, this button (or 'x') close all windows
quit.place(x = 950, y = 710)
quit.bind("<Enter>", lambda e: quit.config(bg='red'))
quit.bind("<Leave>", lambda e: quit.config(bg='#c99191'))

if __name__ == '__main__':
    checkIfNew()  #checks if this is the first time the program has run


root.mainloop()  #shows main window