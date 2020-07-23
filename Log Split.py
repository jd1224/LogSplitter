from tkinter import *
from tkinter import filedialog, messagebox
import os, csv, time, re

root = Tk()
root.title('Log Splitter')
root.geometry("715x415")
root.iconbitmap("logpic.ico")

#root.resizable(False, False)

'''
#functional section contains functions called later in the program
#
#
#
'''
#choose files one at a time
def filePicker():
    global fileList, myListBox
    try:
        #get the new filename and add it to the list
        fileName = filedialog.askopenfilename(initialdir="/", title="Choose a Log to Split", filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        #make sure the filename is not empty
        if fileName != '':
            fileList.append(fileName)
            myListBox.insert(END, fileName)
    except:
        pass
#choose a directory to get all csv files from    
def dirPicker():
    global fileList, myListBox
    try:
        dirName = filedialog.askdirectory(initialdir="/", title="Choose a Directory")
        if dirName!='':
            for name in os.listdir(dirName):
                if name[-4:] == '.csv':
                    file=dirName+"/"+name
                    fileList.append(file)
                    myListBox.insert(END, file)
    except:
        pass
        
def deleteFile():
    global fileList, myListBox
    try:
        #reverse loop from the bottom up in the list to remove one or more files
        #without disrupting the list numbers each time
        for i in reversed(myListBox.curselection()):
            del fileList[i]
            myListBox.delete(i)
    except:
        pass
#clear the list of files 
def deleteAll():
    #display a warning that all entries will be removed from the pane
    choice = messagebox.askquestion ('Delete All Entries?','Are you sure you want to remove all selected files from the choices?',icon = 'warning')
    if choice == 'yes':
        global fileList, myListBox
        fileList = []
        myListBox.delete(0,END)
        clearHeaderListBoxes()
    else:
        messagebox.showinfo('Return','Your selections will remain available.')
#remove all of the headers chosen and unchosen; clear the global chosennames
def clearHeaderListBoxes():
    global chosenNames
    headerListBox.delete(0,END)
    headerListBox2.delete(0,END)
    chosenNames=[]
#pull the headers from the file selected in the file list and set them to the chooser in the bottom
def setTemplate():
    global fieldNames
    result = myListBox.curselection()
    if len(result)>1:
        messagebox.showwarning('WARNING', 'Choose only one file as the template.\nAll files must contain the same headers.', parent=root)
    elif len(result)<1:
        messagebox.showwarning('WARNING', 'You must highlight one of the files in the list.\nAll files must contain the same headers.', parent=root)
    elif myListBox.get(result[0])[-4:] != '.csv':
        messagebox.showwarning('WARNING', 'Choose only a .csv file for the template.\nThis program only handles logs in that format.', parent=root)
    else:
        try:
            with open(fileList[result[0]],'r') as infile:
                reader = csv.DictReader(infile)
                fieldnames = reader.fieldnames
                fieldNames = fieldnames
                clearHeaderListBoxes()
                for i in fieldNames:
                    headerListBox.insert(END, i)
        except:
            print("Bad setTemplate")
            
#move a selection to the selected box
def addSelected():
    
    for i in reversed(headerListBox.curselection()):
            headerListBox2.insert(0, headerListBox.get(i))
            headerListBox.delete(i)
#move a selection to the unselected box
def removeSelected():
    
    for i in reversed(headerListBox2.curselection()):
            headerListBox.insert(END, headerListBox2.get(i))
            headerListBox2.delete(i)
#move all headers to selected
def addAllHeaders():
    for i in range(0,headerListBox.size()):
        headerListBox2.insert(END, headerListBox.get(i))
        
    headerListBox.delete(0,END)
#remove all headers from selected
def removeAllheaders():
    for i in range(0,headerListBox2.size()):
        headerListBox.insert(END, headerListBox2.get(i))
        
    headerListBox2.delete(0,END)
#set the global chosenNames with the contents of the chosen box   
def setChosenNames():
    if headerListBox2.size() < 1:
        messagebox.showwarning('WARNING', 'You must choose headers to check for in the bottom pane.', parent=root)
    else:
        global chosenNames
        chosenNames=[]
        for i in range(0,headerListBox2.size()):
            chosenNames.append(headerListBox2.get(i))

def moveUp():
    for i in headerListBox2.curselection():
        pos = i
        if pos == 0:
            return
        
        selection = headerListBox2.get(pos)
        headerListBox2.delete(pos)
        headerListBox2.insert(pos-1, selection)
        headerListBox2.select_set(pos-1)

def moveDown():
   for i in headerListBox2.curselection():
        pos = i
        if pos == headerListBox2.size():
            return
        
        selection = headerListBox2.get(pos)
        headerListBox2.delete(pos)
        headerListBox2.insert(pos+1, selection)
        headerListBox2.select_set(pos+1)
#check each file in the file list against the selected headers
#remove the files that do not contain the chosen headers
def checkHeaders():
    setChosenNames()
    global failingFiles, matchingFiles
    fieldnames=[]
    for i in range(0,myListBox.size()):
        with open(myListBox.get(i),'r') as infile:
                reader = csv.DictReader(infile)
                fieldnames = reader.fieldnames
                
        if set(chosenNames)-set(fieldnames) == set():
            matchingFiles.append(myListBox.get(i))
        else:
            failingFiles.append(myListBox.get(i))
    removeFailed()
#remove files from file list if they do not contain the correct headers    
def removeFailed():
    global failingFiles
    for i in range(myListBox.size()-1,-1,-1):
        if myListBox.get(i) in failingFiles:
            myListBox.delete(i)
    if len(failingFiles)>0:        
        messageString=''
        if len(failingFiles)<5:
            messageString+='The following files were removed because they did not contain the correct headers:\n'
            for i in failingFiles:
                messageString+=i+'\n'
        else:
            messageString+=str(len(failingFiles))+" files were removed because they did not contain the correct headers"
            messagebox.showwarning('WARNING', messageString, parent=root)
    failingFiles=[]
#select the directory to write to
#display a popup if permission is denied    
def selectOutDir():
    global saveDirectory
    outdirListBox.delete(0,END)
    dirName = filedialog.askdirectory(initialdir="/", title="Choose a Directory")
    if dirName!='':
        try:
            with open(dirName+'/manifest.txt', "w+") as outfile:
                for i in matchingFiles:
                    outfile.write(i+'\n')
                outfile.close()
            outdirListBox.insert(END,dirName+"/")
            saveDirectory=dirName+"/"
        except:
            messagebox.showwarning('WARNING', "You do not have permission to write in "+dirName, parent=root)

def checkCombined():
    origfilename="combined"
    fileext=".csv"
    filename=origfilename+fileext
    checking=True
    count=1
    while checking:
        if os.path.isfile(saveDirectory+filename):
            filename=origfilename+" ("+str(count)+")"+fileext
            count+=1
        else:
            return filename
#split the log based on the selected headers
#write the log to the chosed directory
#write to current directory if none chosen
def logSplit():
    checkHeaders()
    if saveDirectory == '':
        selectOutDir()
    else:
        if saveSeperate:
            pattern = '[^\/]+$'
            if len(chosenNames)>0:
                for i in range (0,myListBox.size()):
                    file = re.findall(pattern, myListBox.get(i))
                    outsuffix= file[0]
                    with open(myListBox.get(i),'r') as infile:
                        with open(saveDirectory+"prs-"+outsuffix, "w+", newline='') as outfile:
                            fieldnames = chosenNames
                            writer = csv.DictWriter(outfile, fieldnames)
                            reader = csv.DictReader(infile)
                            writer.writeheader()
                            for row in reader:
                                outrow={}
                                for i in chosenNames:
                                    outrow[i]=row[i]
                                writer.writerow(outrow)
                            outfile.close()
                            infile.close()
            else:
                messagebox.showwarning('WARNING', "You must choose headers to keep. ", parent=root)
        else:
            filename = checkCombined()
            if len(chosenNames)>0:
                try:
                    with open(saveDirectory+filename, "w+", newline='') as outfile:
                        fieldnames = chosenNames
                        writer = csv.DictWriter(outfile, fieldnames)
                        writer.writeheader()
                        for i in range (0,myListBox.size()):
                            with open(myListBox.get(i),'r') as infile:
                                    reader = csv.DictReader(infile)
                                    for row in reader:
                                        outrow={}
                                        for i in chosenNames:
                                            outrow[i]=row[i]
                                        writer.writerow(outrow)
                                    infile.close()
                        outfile.close()
                except PermissionError:
                    messagebox.showwarning('WARNING', "ERROR!\nMake sure you have permission to write to that directory. Ensure the file is not already opened.", parent=root)
            else:
                messagebox.showwarning('WARNING', "You must choose headers to keep. ", parent=root)
                
#setup the toggle for the global variable to save seperate 
#or to save together
def toggle(tog=[0]):
    global saveSeperate
    tog[0] = not tog[0]
    if tog[0]:
        t_btn.config(text='Save\nCombined')
        saveSeperate=False
    else:
        t_btn.config(text='Save\nSeperate')
        saveSeperate=True  

'''
#Setting up the file choosing part of the program with a file picker 
#that allows the user to select csv files.
#Also allows the user to switch to all files so they can see
#where they are in the file structure.
'''

#global variables to be used
fileList=[]  
fieldNames=[]
chosenNames=[]
matchingFiles=[]
failingFiles=[]
saveDirectory=''
saveSeperate=True

#create the choosing panel to choose the files
chooser = LabelFrame(root, text="Choose Logs to Split", padx=5, pady=5)
chooser.grid(row=0, column=0, padx=10, pady=10)
scrollOne = Scrollbar(chooser, orient=VERTICAL)

#create a listbox for the files and configure scroll bar
myListBox = Listbox(chooser, width=64, yscrollcommand=scrollOne.set ,selectmode=EXTENDED)
scrollOne.config(command=myListBox.yview)
scrollOne.pack(side=RIGHT, fill=Y)
myListBox.pack()

#Button Designations for Choosing Pane
chooserButtons = LabelFrame(root)
chooserButtons.grid(row=0, column=1)

chooseButton = Button(chooserButtons, text="Choose\nFile", command=filePicker, width=8)
chooseButton.grid(row=0,column=0)

dirButton = Button(chooserButtons, text="Choose\nDirectory", command=dirPicker, width=8)
dirButton.grid(row=1,column=0)

deleteButton = Button(chooserButtons, text="Remove\nSelected", command=deleteFile, width=8)
deleteButton.grid(row=2,column=0)

clearButton = Button(chooserButtons, text="Clear\nAll", command=deleteAll, width=8)
clearButton.grid(row=0, column=1)

templateButton = Button(chooserButtons, text="Select\nTemplate", command=setTemplate, width=8)
templateButton.grid(row=1, column=1)

CompareButton = Button(chooserButtons, text="Check\nFiles", command=checkHeaders, width=8)
CompareButton.grid(row=2, column=1)

#END OF CHOOOSING PANE

'''
#Set up the file header choosing panel
#this is where the choices for which headers to 
#use as templates comes in
#
'''
#Begin header choices panes

bottomLeft = LabelFrame(root, text="Choose Headers to Keep")

headerChooser = LabelFrame(bottomLeft)
headerChooser.grid(row=0, column=0)
scrolltwo = Scrollbar(headerChooser, orient=VERTICAL)

#create a listbox for the headers and configure scroll bar
headerListBox = Listbox(headerChooser, width=25, yscrollcommand=scrolltwo.set ,selectmode=EXTENDED)
scrolltwo.config(command=headerListBox.yview)
scrolltwo.pack(side=RIGHT, fill=Y)
headerListBox.pack()


headerChosen = LabelFrame(bottomLeft)
headerChosen.grid(row=0, column=2)
scrollThree = Scrollbar(headerChosen, orient=VERTICAL)

#create a listbox for the headers chosen and configure scroll bar
headerListBox2 = Listbox(headerChosen, width=25, yscrollcommand=scrollThree.set ,selectmode=SINGLE)
scrollThree.config(command=headerListBox2.yview)
scrollThree.pack(side=RIGHT, fill=Y)
headerListBox2.pack()



#Create header choosing buttons
headerButtons = LabelFrame(bottomLeft)
headerButtons.grid(row=0, column=1)

chooseAllHeaderButton = Button(headerButtons, text=" >>> ", command=addAllHeaders, width=8)
chooseAllHeaderButton.grid(row=0,column=0)

chooseHeaderButton = Button(headerButtons, text=" > ", command=addSelected, width=8)
chooseHeaderButton.grid(row=1,column=0)

removeHeaderButton = Button(headerButtons, text=" < ", command=removeSelected, width=8)
removeHeaderButton.grid(row=2,column=0)

removeAllHeaderButton = Button(headerButtons, text=" <<< ", command=removeAllheaders, width=8)
removeAllHeaderButton.grid(row=3,column=0)

clearAllHeaderButton = Button(headerButtons, text="Clear", command=clearHeaderListBoxes, width=8)
clearAllHeaderButton.grid(row=4,column=0)

#create move up and down buttons for headers chosen
headerMoveButtons = LabelFrame(bottomLeft)
headerMoveButtons.grid(row=0, column=3)

moveUpButton= Button(headerMoveButtons, text="^", command=moveUp)
moveUpButton.pack()

moveDownButton= Button(headerMoveButtons, text="v", command=moveDown)
moveDownButton.pack()

bottomLeft.grid(row=1, column=0)
#End header choices panes

'''
#Destination chooser and run buttons
#Bottom Right Panel
'''
bottomRight = LabelFrame(root, text="Choose Save Location", padx=10)

outdirListBox = Listbox(bottomRight, width=25, height=1,selectmode=EXTENDED)
outdirListBox.grid(row=0,column=0)

outButton = Button(bottomRight, text="Save\nLocation", command=selectOutDir, width=25)
outButton.grid(row=1, column=0)

runButton = Button(bottomRight, text="Split\nLogs", command=logSplit, width=25)
runButton.grid(row=2, column=0)

t_btn = Button(bottomRight, text="Save\nSeperate", command=toggle, width=25)
t_btn.grid(row=3, column=0)

bottomRight.grid(row=1, column=1)

root.mainloop()