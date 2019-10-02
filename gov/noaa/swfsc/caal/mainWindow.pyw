'''
Created on Jan 14, 2017

@author: yyzz
'''

import os
import platform
import sys
import subprocess
#import posixpath
import shutil 
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
#from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from math import *


#import gov.noaa.swfsc.caal.plotCanvas
#import gov.noaa.swfsc.caal.qrc_resources
import qrc_resources
#from gov.noaa.swfsc.caal.plotCanvas import PlotCanvas
from matplotlib.colors import Colormap


__version__ = "1.0.0"


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

#         self.imageLabel = QLabel()
#         self.imageLabel.setMinimumSize(200, 200)
#         self.imageLabel.setAlignment(Qt.AlignCenter)
#         self.imageLabel.setContextMenuPolicy(Qt.ActionsContextMenu)
#         self.setCentralWidget(self.imageLabel)
        self.filename = None
        self.printer = None
        self.ageProportionMatrix = []
        self.fishLengthMatrix = []

        self.sizeLabel = QLabel()
        self.sizeLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage("Ready", 10000)

        
        fileDataOpenAction = self.createAction("&Open Data File...", self.fileDataOpen,
                "Ctrl+D", "fileopen",
                "Open an existing input data file")
        filePinOpenAction = self.createAction("&Open Pin File...", self.filePinOpen,
                "Ctrl+P", "fileopen",
                "Open an existing Pin file")
        
        filePrintAction = self.createAction("&Print", self.filePrint,
                QKeySequence.Print, "fileprint", "Print the image")
        fileQuitAction = self.createAction("&Quit", self.close,
                "Ctrl+Q", "filequit", "Close the application")
        
      
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenuActions = (fileDataOpenAction, filePinOpenAction,
                None, filePrintAction,
                fileQuitAction)
        self.fileMenu.aboutToShow.connect(self.updateFileMenu)
        
        
        viewReportAction = self.createAction("&View Report", self.viewReport,
                "", "", "View Report")
        viewLogAction = self.createAction("&View Echo Input File", self.viewEchoInputFile,
                "", "", "View Log File")

        viewMenu = self.menuBar().addMenu("&View")
        self.addActions(viewMenu, (viewReportAction,viewLogAction))
        
        runAction = self.createAction("&Run CAAL Basic Model", self.runCAAL,
                "Ctrl+R", "", "Run CAAL Basic Model")
        

        runMenu = self.menuBar().addMenu("&Run")
        self.addActions(runMenu, (runAction,None))
        
        
        runAction = self.createAction("&Select Program For Viewing Output Files", self.selectProgram,
                "", "", "Select Program For Viewing Output Files")
        

        runMenu = self.menuBar().addMenu("&Options")
        self.addActions(runMenu, (runAction,None))
        
        inputDataAction = self.createAction("&Input Data", self.inputData,
                "", "", "Input Data")
        modelResultAction = self.createAction("&Model Result", self.modelResult,
                "", "", "Model Result")
        
        viewMenu = self.menuBar().addMenu("&Window")
        self.addActions(viewMenu, (inputDataAction,modelResultAction))
        
        helpAboutAction = self.createAction("&About CAAL",self.helpAbout)
        helpUsingAction = self.createAction("&Using CAAL", self.helpUsing,)
        helpTechManualAction = self.createAction("&Technical Manual",self.helpTechManual)
        helpUserManualAction = self.createAction("&User's Manual",self.helpUserManual)
        helpMenu = self.menuBar().addMenu("&Help")
        self.addActions(helpMenu, (helpAboutAction, helpUsingAction,helpTechManualAction,helpUserManualAction))
        
        self.stackedWidget = QStackedWidget()
        
        self.inputDataTabWidget = QTabWidget()
        
        gridLayout1 = QGridLayout()
        inputDataFileLabel = QLabel("Input Data File:")
        self.inputDataFileEdit = QLineEdit()
        self.inputDataFileEdit.setReadOnly(True)
        self.inputDataFileEdit.setStyleSheet("background-color:#c1c5cc")
        inputDataFileLabel.setBuddy(self.inputDataFileEdit)
        
        gridLayout1.addWidget(inputDataFileLabel, 0, 0)
        gridLayout1.addWidget(self.inputDataFileEdit, 0, 1, 1, 5)
       
        
        self.modelOptions = []
        modelButtonLayout = QHBoxLayout()

        self.modelButtonGroup = QButtonGroup()
        modelButtonText = ""
        for i in range(4): 
            if i == 0:
                modelButtonText = "von bertlanffy"
            elif i == 1:
                modelButtonText = "Gompertz"
            elif i == 2:
                modelButtonText = "Inverse logistic"
            elif i == 3:
                modelButtonText = "Richards"
            button = QRadioButton(modelButtonText)     # make a button
            modelButtonLayout.addWidget(button)           # add to layout
            self.modelButtonGroup.addButton(button,i)       # add to QButtonGroup
            self.modelOptions.append(button)
        


        growthModelOptionLabel = QLabel("Growth Model Option:")    
        gridLayout1.addWidget(growthModelOptionLabel,1,0)
        gridLayout1.addLayout(modelButtonLayout,1,1,1,5)
        
        self.firstLowerBoundLabel = QLabel("Linf Lower Bound:")
        self.firstLowerBoundEdit = QLineEdit()
        self.firstLowerBoundEdit.setReadOnly(True)
        self.firstLowerBoundEdit.setStyleSheet("background-color:#c1c5cc")
        self.firstLowerBoundLabel.setBuddy(self.firstLowerBoundEdit)
        gridLayout1.addWidget(self.firstLowerBoundLabel,2,0)
        gridLayout1.addWidget(self.firstLowerBoundEdit,2,1)
        
        self.firstUpperBoundLabel = QLabel("Linf Upper Bound:")
        self.firstUpperBoundEdit = QLineEdit()
        self.firstUpperBoundEdit.setReadOnly(True)
        self.firstUpperBoundEdit.setStyleSheet("background-color:#c1c5cc")
        self.firstUpperBoundLabel.setBuddy(self.firstUpperBoundEdit)
        gridLayout1.addWidget(self.firstUpperBoundLabel,2,2)
        gridLayout1.addWidget(self.firstUpperBoundEdit,2,3)
        
        self.firstPhaseLabel = QLabel("Linf Phase:")
        self.firstPhaseEdit = QLineEdit()
        self.firstPhaseEdit.setReadOnly(True)
        self.firstPhaseEdit.setStyleSheet("background-color:#c1c5cc")
        self.firstPhaseLabel.setBuddy(self.firstPhaseEdit)
        gridLayout1.addWidget(self.firstPhaseLabel,2,4)
        gridLayout1.addWidget(self.firstPhaseEdit,2,5)
        
        self.secondLowerBoundLabel = QLabel("K Lower Bound:")
        self.secondLowerBoundEdit = QLineEdit()
        self.secondLowerBoundEdit.setReadOnly(True)
        self.secondLowerBoundEdit.setStyleSheet("background-color:#c1c5cc")
        self.secondLowerBoundLabel.setBuddy(self.secondLowerBoundEdit)
        gridLayout1.addWidget(self.secondLowerBoundLabel,3,0)
        gridLayout1.addWidget(self.secondLowerBoundEdit,3,1)
        
        self.secondUpperBoundLabel = QLabel("K Upper Bound:")
        self.secondUpperBoundEdit = QLineEdit()
        self.secondUpperBoundEdit.setReadOnly(True)
        self.secondUpperBoundEdit.setStyleSheet("background-color:#c1c5cc")
        self.secondUpperBoundLabel.setBuddy(self.secondUpperBoundEdit)
        gridLayout1.addWidget(self.secondUpperBoundLabel,3,2)
        gridLayout1.addWidget(self.secondUpperBoundEdit,3,3)
        
        self.secondPhaseLabel = QLabel("K Phase:")
        self.secondPhaseEdit = QLineEdit()
        self.secondPhaseEdit.setReadOnly(True)
        self.secondPhaseEdit.setStyleSheet("background-color:#c1c5cc")
        self.secondPhaseLabel.setBuddy(self.secondPhaseEdit)
        gridLayout1.addWidget(self.secondPhaseLabel,3,4)
        gridLayout1.addWidget(self.secondPhaseEdit,3,5)
        
        
        self.thirdLowerBoundLabel = QLabel("t0 Lower Bound:")
        self.thirdLowerBoundEdit = QLineEdit()
        self.thirdLowerBoundEdit.setReadOnly(True)
        self.thirdLowerBoundEdit.setStyleSheet("background-color:#c1c5cc")
        self.thirdLowerBoundLabel.setBuddy(self.thirdLowerBoundEdit)
        gridLayout1.addWidget(self.thirdLowerBoundLabel,4,0)
        gridLayout1.addWidget(self.thirdLowerBoundEdit,4,1)
        
        self.thirdUpperBoundLabel = QLabel("t0 Upper Bound:")
        self.thirdUpperBoundEdit = QLineEdit()
        self.thirdUpperBoundEdit.setReadOnly(True)
        self.thirdUpperBoundEdit.setStyleSheet("background-color:#c1c5cc")
        self.thirdUpperBoundLabel.setBuddy(self.thirdUpperBoundEdit)
        gridLayout1.addWidget(self.thirdUpperBoundLabel,4,2)
        gridLayout1.addWidget(self.thirdUpperBoundEdit,4,3)
        
        self.thirdPhaseLabel = QLabel("t0 Phase:")
        self.thirdPhaseEdit = QLineEdit()
        self.thirdPhaseEdit.setReadOnly(True)
        self.thirdPhaseEdit.setStyleSheet("background-color:#c1c5cc")
        self.thirdPhaseLabel.setBuddy(self.thirdPhaseEdit)
        gridLayout1.addWidget(self.thirdPhaseLabel,4,4)
        gridLayout1.addWidget(self.thirdPhaseEdit,4,5)
        
        self.fourthLowerBoundLabel = QLabel("p Lower Bound:")
        self.fourthLowerBoundEdit = QLineEdit()
        self.fourthLowerBoundEdit.setReadOnly(True)
        self.fourthLowerBoundEdit.setStyleSheet("background-color:#c1c5cc")
        self.fourthLowerBoundLabel.setBuddy(self.fourthLowerBoundEdit)
        gridLayout1.addWidget(self.fourthLowerBoundLabel,5,0)
        gridLayout1.addWidget(self.fourthLowerBoundEdit,5,1)
        
        self.fourthUpperBoundLabel = QLabel("p Upper Bound:")
        self.fourthUpperBoundEdit = QLineEdit()
        self.fourthUpperBoundEdit.setReadOnly(True)
        self.fourthUpperBoundEdit.setStyleSheet("background-color:#c1c5cc")
        self.fourthUpperBoundLabel.setBuddy(self.fourthUpperBoundEdit)
        gridLayout1.addWidget(self.fourthUpperBoundLabel,5,2)
        gridLayout1.addWidget(self.fourthUpperBoundEdit,5,3)
        
        self.fourthPhaseLabel = QLabel("p Phase:")
        self.fourthPhaseEdit = QLineEdit()
        self.fourthPhaseEdit.setReadOnly(True)
        self.fourthPhaseEdit.setStyleSheet("background-color:#c1c5cc")
        self.thirdPhaseLabel.setBuddy(self.fourthPhaseEdit)
        gridLayout1.addWidget(self.fourthPhaseLabel,5,4)
        gridLayout1.addWidget(self.fourthPhaseEdit,5,5)
        
        self.fourthLowerBoundLabel.hide()
        self.fourthLowerBoundEdit.hide()
        self.fourthUpperBoundLabel.hide()
        self.fourthUpperBoundEdit.hide()
        self.fourthPhaseLabel.hide()
        self.fourthPhaseEdit.hide()
        
        self.varianceOptions = []
        varianceButtonLayout = QHBoxLayout()

        self.varianceButtonGroup = QButtonGroup()
        varianceButtonText = ""
        for i in range(3): 
            if i == 0:
                varianceButtonText = "estimate const cv"
            elif i == 1:
                varianceButtonText = "estimate const sd"
            elif i == 2:
                varianceButtonText = "cv1 cv2 at age1 age2"
            
            button = QRadioButton(varianceButtonText)     # make a button
            varianceButtonLayout.addWidget(button)           # add to layout
            self.varianceButtonGroup.addButton(button,i)       # add to QButtonGroup
            self.varianceOptions.append(button)
        


        estimateVarianceOptionLabel = QLabel("Estimate Variance Option:")    
        gridLayout1.addWidget(estimateVarianceOptionLabel,6,0)
        gridLayout1.addLayout(varianceButtonLayout,6,1,1,5)
        
        self.varianceLowerBoundLabel = QLabel("CV Lower Bound:")
        self.varianceLowerBoundEdit = QLineEdit()
        self.varianceLowerBoundEdit.setReadOnly(True)
        self.varianceLowerBoundEdit.setStyleSheet("background-color:#c1c5cc")
        self.varianceLowerBoundLabel.setBuddy(self.varianceLowerBoundEdit)
        gridLayout1.addWidget(self.varianceLowerBoundLabel,7,0)
        gridLayout1.addWidget(self.varianceLowerBoundEdit,7,1)
        
        self.varianceUpperBoundLabel = QLabel("CV Upper Bound:")
        self.varianceUpperBoundEdit = QLineEdit()
        self.varianceUpperBoundEdit.setReadOnly(True)
        self.varianceUpperBoundEdit.setStyleSheet("background-color:#c1c5cc")
        self.varianceUpperBoundLabel.setBuddy(self.varianceUpperBoundEdit)
        gridLayout1.addWidget(self.varianceUpperBoundLabel,7,2)
        gridLayout1.addWidget(self.varianceUpperBoundEdit,7,3)
        
        self.variancePhaseLabel = QLabel("CV Phase:")
        self.variancePhaseEdit = QLineEdit()
        self.variancePhaseEdit.setReadOnly(True)
        self.variancePhaseEdit.setStyleSheet("background-color:#c1c5cc")
        self.variancePhaseLabel.setBuddy(self.variancePhaseEdit)
        gridLayout1.addWidget(self.variancePhaseLabel,7,4)
        gridLayout1.addWidget(self.variancePhaseEdit,7,5)
        
        
        self.varianceLowerBoundLabel2 = QLabel("CV2 Lower Bound:")
        self.varianceLowerBoundEdit2 = QLineEdit()
        self.varianceLowerBoundEdit2.setReadOnly(True)
        self.varianceLowerBoundEdit2.setStyleSheet("background-color:#c1c5cc")
        self.varianceLowerBoundLabel2.setBuddy(self.varianceLowerBoundEdit2)
        gridLayout1.addWidget(self.varianceLowerBoundLabel2,8,0)
        gridLayout1.addWidget(self.varianceLowerBoundEdit2,8,1)
        
        self.varianceUpperBoundLabel2 = QLabel("CV2 Upper Bound:")
        self.varianceUpperBoundEdit2 = QLineEdit()
        self.varianceUpperBoundEdit2.setReadOnly(True)
        self.varianceUpperBoundEdit2.setStyleSheet("background-color:#c1c5cc")
        self.varianceUpperBoundLabel2.setBuddy(self.varianceUpperBoundEdit2)
        gridLayout1.addWidget(self.varianceUpperBoundLabel2,8,2)
        gridLayout1.addWidget(self.varianceUpperBoundEdit2,8,3)
        
        self.variancePhaseLabel2 = QLabel("CV2 Phase:")
        self.variancePhaseEdit2 = QLineEdit()
        self.variancePhaseEdit2.setReadOnly(True)
        self.variancePhaseEdit2.setStyleSheet("background-color:#c1c5cc")
        self.variancePhaseLabel2.setBuddy(self.variancePhaseEdit2)
        gridLayout1.addWidget(self.variancePhaseLabel2,8,4)
        gridLayout1.addWidget(self.variancePhaseEdit2,8,5)
        
        self.varianceLowerBoundLabel2.hide()
        self.varianceLowerBoundEdit2.hide()
        self.varianceUpperBoundLabel2.hide()
        self.varianceUpperBoundEdit2.hide()
        self.variancePhaseLabel2.hide()
        self.variancePhaseEdit2.hide()
        
        
        self.firstLengthLabel = QLabel("First Length:")
        self.firstLengthEdit = QLineEdit()
        self.firstLengthEdit.setReadOnly(True)
        self.firstLengthEdit.setStyleSheet("background-color:#c1c5cc")
        self.firstLengthLabel.setBuddy(self.firstLengthEdit)
        gridLayout1.addWidget(self.firstLengthLabel,9,0)
        gridLayout1.addWidget(self.firstLengthEdit,9,1)
        
        self.lastLengthLabel = QLabel("Last Length:")
        self.lastLengthEdit = QLineEdit()
        self.lastLengthEdit.setReadOnly(True)
        self.lastLengthEdit.setStyleSheet("background-color:#c1c5cc")
        self.lastLengthLabel.setBuddy(self.lastLengthEdit)
        gridLayout1.addWidget(self.lastLengthLabel,9,2)
        gridLayout1.addWidget(self.lastLengthEdit,9,3)
        
        self.lengthIncrementLabel = QLabel("Length Increment:")
        self.lengthIncrementEdit = QLineEdit()
        self.lengthIncrementEdit.setReadOnly(True)
        self.lengthIncrementEdit.setStyleSheet("background-color:#c1c5cc")
        self.lengthIncrementLabel.setBuddy(self.lengthIncrementEdit)
        gridLayout1.addWidget(self.lengthIncrementLabel,9,4)
        gridLayout1.addWidget(self.lengthIncrementEdit,9,5)
        
        self.firstAgeLabel = QLabel("First Age:")
        self.firstAgeEdit = QLineEdit()
        self.firstAgeEdit.setReadOnly(True)
        self.firstAgeEdit.setStyleSheet("background-color:#c1c5cc")
        self.firstAgeLabel.setBuddy(self.firstAgeEdit)
        gridLayout1.addWidget(self.firstAgeLabel,10,0)
        gridLayout1.addWidget(self.firstAgeEdit,10,1)
        
        self.lastAgeLabel = QLabel("Last Age:")
        self.lastAgeEdit = QLineEdit()
        self.lastAgeEdit.setReadOnly(True)
        self.lastAgeEdit.setStyleSheet("background-color:#c1c5cc")
        self.lastAgeLabel.setBuddy(self.lastAgeEdit)
        gridLayout1.addWidget(self.lastAgeLabel,10,2)
        gridLayout1.addWidget(self.lastAgeEdit,10,3)
        
        self.ageIncrementLabel = QLabel("Age Increment:")
        self.ageIncrementEdit = QLineEdit()
        self.ageIncrementEdit.setReadOnly(True)
        self.ageIncrementEdit.setStyleSheet("background-color:#c1c5cc")
        self.ageIncrementLabel.setBuddy(self.ageIncrementEdit)
        gridLayout1.addWidget(self.ageIncrementLabel,10,4)
        gridLayout1.addWidget(self.ageIncrementEdit,10,5)
        
        
        self.firstYearLabel = QLabel("First Year:")
        self.firstYearEdit = QLineEdit()
        self.firstYearEdit.setReadOnly(True)
        self.firstYearEdit.setStyleSheet("background-color:#c1c5cc")
        self.firstYearLabel.setBuddy(self.firstYearEdit)
        gridLayout1.addWidget(self.firstYearLabel,11,0)
        gridLayout1.addWidget(self.firstYearEdit,11,1)
        
        self.lastYearLabel = QLabel("Last Year:")
        self.lastYearEdit = QLineEdit()
        self.lastYearEdit.setReadOnly(True)
        self.lastYearEdit.setStyleSheet("background-color:#c1c5cc")
        self.lastYearLabel.setBuddy(self.lastYearEdit)
        gridLayout1.addWidget(self.lastYearLabel,11,2)
        gridLayout1.addWidget(self.lastYearEdit,11,3)
        
        self.yearIncrementLabel = QLabel("Year Increment:")
        self.yearIncrementEdit = QLineEdit()
        self.yearIncrementEdit.setReadOnly(True)
        self.yearIncrementEdit.setStyleSheet("background-color:#c1c5cc")
        self.lengthIncrementLabel.setBuddy(self.yearIncrementEdit)
        gridLayout1.addWidget(self.yearIncrementLabel,11,4)
        gridLayout1.addWidget(self.yearIncrementEdit,11,5)
        
        
        self.NumberOfFleetLabel = QLabel("Numbers Of Fleet:")
        self.numberOfFleetEdit = QLineEdit()
        self.numberOfFleetEdit.setReadOnly(True)
        self.numberOfFleetEdit.setStyleSheet("background-color:#c1c5cc")
        self.NumberOfFleetLabel.setBuddy(self.numberOfFleetEdit)
        gridLayout1.addWidget(self.NumberOfFleetLabel,12,0)
        gridLayout1.addWidget(self.numberOfFleetEdit,12,1)
        
        
        
        #gridLayout2 = QGridLayout()
        
        initialConditionLabel = QLabel("Initial Conditions:")
        gridLayout1.addWidget(initialConditionLabel,13,0)
        
        initialConditionEdit = QLineEdit()
        initialConditionEdit.setReadOnly(True)
        initialConditionEdit.setStyleSheet("background-color:#c1c5cc")
        
        #gridLayout1.addWidget(initialConditionEdit,13,0)
        
        
        horizontalLine     =  QFrame()
        horizontalLine.setFrameStyle(QFrame.HLine)
        horizontalLine.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        
        gridLayout1.addWidget(horizontalLine,13,1,1,6)
        
        inputPinFileLabel = QLabel("Input Pin File:")
        self.inputPinFileEdit = QLineEdit()
        self.inputPinFileEdit.setReadOnly(True)
        self.inputPinFileEdit.setStyleSheet("background-color:#c1c5cc")
        inputPinFileLabel.setBuddy(self.inputPinFileEdit)
        gridLayout1.addWidget(inputPinFileLabel, 14, 0)
        gridLayout1.addWidget(self.inputPinFileEdit, 14 , 1, 1, 5)
        
        
        #gridLayout2.addWidget(horizontalLine,1,0,1,6)
        
#         initialConditionEdit = QLineEdit()
#         gridLayout2.addWidget(initialConditionEdit,0,1)
        
        


        
        self.linfLabel = QLabel("Linf:")
        self.linfEdit = QLineEdit()
        self.linfEdit.setReadOnly(True)
        self.linfEdit.setStyleSheet("background-color:#c1c5cc")
        self.linfLabel.setBuddy(self.linfEdit)
        gridLayout1.addWidget(self.linfLabel,15,0)
        gridLayout1.addWidget(self.linfEdit,15,1)
        
        self.kLabel = QLabel("K:")
        self.kEdit = QLineEdit()
        self.kEdit.setReadOnly(True)
        self.kEdit.setStyleSheet("background-color:#c1c5cc")
        self.kLabel.setBuddy(self.kEdit)
        gridLayout1.addWidget(self.kLabel,15,2)
        gridLayout1.addWidget(self.kEdit,15,3)
        
        self.t0Label = QLabel("t0:")
        self.t0Edit = QLineEdit()
        self.t0Edit.setReadOnly(True)
        self.t0Edit.setStyleSheet("background-color:#c1c5cc")
        self.t0Label.setBuddy(self.t0Edit)
        gridLayout1.addWidget(self.t0Label,15,4)
        gridLayout1.addWidget(self.t0Edit,15,5)
        
        self.cvLabel = QLabel("cv:")
        self.cvEdit = QLineEdit()
        self.cvEdit.setReadOnly(True)
        self.cvEdit.setStyleSheet("background-color:#c1c5cc")
        self.cvLabel.setBuddy(self.t0Edit)
        gridLayout1.addWidget(self.cvLabel,16,0)
        gridLayout1.addWidget(self.cvEdit,16,1)
        
        
        self.pLabel = QLabel("p:")
        self.pEdit = QLineEdit()
        self.pEdit.setReadOnly(True)
        self.pEdit.setStyleSheet("background-color:#c1c5cc")
        self.pLabel.setBuddy(self.pEdit)
        gridLayout1.addWidget(self.pLabel,16,2)
        gridLayout1.addWidget(self.pEdit,16,3)
        
        self.pLabel.hide()
        self.pEdit.hide()
        
        
        
        
        
        generalDataWidget = QWidget()
        generalDataLayout = QVBoxLayout()
        generalDataLayout.setAlignment(Qt.AlignTop)
        generalDataLayout.addLayout(gridLayout1)
        #generalDataLayout.addLayout(gridLayout2)
        generalDataWidget.setLayout(generalDataLayout)
        self.inputDataTabWidget.addTab(generalDataWidget, "General Data")
        
        
        
        ageProportionWidget = QWidget()
        ageProportionLayout = QVBoxLayout()
        self.ageProportionTable = QTableWidget()
        ageProportionLayout.addWidget(self.ageProportionTable)
        ageProportionWidget.setLayout(ageProportionLayout)
        self.inputDataTabWidget.addTab(ageProportionWidget, "Age Proportion")
        
        fishLengthWidget = QWidget()
        fishLengthLayout = QVBoxLayout()
        self.fishLengthTable = QTableWidget()
        fishLengthLayout.addWidget(self.fishLengthTable)
        fishLengthWidget.setLayout(fishLengthLayout)
        self.inputDataTabWidget.addTab(fishLengthWidget, "No. Fish @ Age&Length")
        
        self.stackedWidget.addWidget(self.inputDataTabWidget)
        
        
        # a figure instance to plot on
        self.growthCurveFigure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.growthCurveCanvas = FigureCanvas(self.growthCurveFigure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.growthCurveToolbar = NavigationToolbar(self.growthCurveCanvas, self)
        
        

        # set the layout
        growthCurveLayout = QVBoxLayout()
        growthCurveLayout.addWidget(self.growthCurveToolbar)
        growthCurveLayout.addWidget(self.growthCurveCanvas)
        
        growthCurveWidget = QWidget()
        growthCurveWidget.setLayout(growthCurveLayout)
        
#         self.plotCanvas = PlotCanvas(self, width=5, height=4)
        
        self.modelResultTabWidget = QTabWidget()
        self.modelResultTabWidget.addTab(growthCurveWidget,"Result1-Growth curve")
        
        # a figure instance to plot on
        self.pHatFigure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.pHatCanvas = FigureCanvas(self.pHatFigure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.pHatToolbar = NavigationToolbar(self.pHatCanvas, self)
        
        pHatYearLabel = QLabel("Year: ")
        self.pHatYearSelect = QComboBox()
        pHatYearLabel.setBuddy(self.pHatYearSelect)
        pHatFleetLabel = QLabel("Fleet: ")
        self.pHatFleetSelect = QComboBox()
        
        pHatFleetLabel.setBuddy(self.pHatFleetSelect)
        pHatParamLayout = QHBoxLayout()
        pHatParamLayout.addWidget(pHatYearLabel)
        pHatParamLayout.addWidget(self.pHatYearSelect)
        pHatParamLayout.addWidget(pHatFleetLabel)
        pHatParamLayout.addWidget(self.pHatFleetSelect)
        

        # set the layout
        pHatLayout = QVBoxLayout()
        pHatLayout.addLayout(pHatParamLayout)
        pHatLayout.addWidget(self.pHatToolbar)
        pHatLayout.addWidget(self.pHatCanvas)
        
        pHatWidget = QWidget()
        pHatWidget.setLayout(pHatLayout)
        
        self.modelResultTabWidget.addTab(pHatWidget,"Result2-p_hat")
        
        
            # a figure instance to plot on
        self.likelihoodFigure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.likelihoodCanvas = FigureCanvas(self.likelihoodFigure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.likelihoodToolbar = NavigationToolbar(self.likelihoodCanvas, self)
        
        likelihoodYearLabel = QLabel("Year: ")
        self.likelihoodYearSelect = QComboBox()
        likelihoodYearLabel.setBuddy(self.likelihoodYearSelect)
        likelihoodFleetLabel = QLabel("Fleet: ")
        self.likelihoodFleetSelect = QComboBox()
        likelihoodFleetLabel.setBuddy(self.likelihoodFleetSelect)
        pHatParamLayout = QHBoxLayout()
        pHatParamLayout.addWidget(likelihoodYearLabel)
        pHatParamLayout.addWidget(self.likelihoodYearSelect)
        pHatParamLayout.addWidget(likelihoodFleetLabel)
        pHatParamLayout.addWidget(self.likelihoodFleetSelect)
        
        # set the layout
        likelihoodLayout = QVBoxLayout()
        likelihoodLayout.addLayout(pHatParamLayout)
        likelihoodLayout.addWidget(self.likelihoodToolbar)
        likelihoodLayout.addWidget(self.likelihoodCanvas)
        
        likehoodWidget = QWidget()
        likehoodWidget.setLayout(likelihoodLayout)
        
        self.modelResultTabWidget.addTab(likehoodWidget,"Result3_individual likelihood")
#         self.setCentralWidget(self.modelResultTabWidget)
        self.stackedWidget.addWidget(self.modelResultTabWidget)
        
        self.setCentralWidget(self.stackedWidget)
        
        

        settings = QSettings()
        self.recentFiles = []
        #self.recentFiles = settings.value("RecentFiles").toStringList()
        #self.recentFiles = settings.value("RecentFiles")
        #self.restoreGeometry(
        #        settings.value("MainWindow/Geometry").toByteArray())
        #self.restoreState(settings.value("MainWindow/State"))
        
        self.setWindowTitle("CAAL")
        self.updateFileMenu()
#         QTimer.singleShot(0, self.loadInitialFile)

    def plot(self):
        ''' plot some random stuff '''
        self.filename = "./report.dat"
        growthCurveYData = []
        stddev = []
        pHatYear = {}
        pHatFleet = {}
        likelihoodYear = {}
        likelihoodFleet = {}
        
        with open(self.filename) as file_object:
            lines = file_object.readlines()
        if not lines:
            message = "Failed to read {0}".format(self.filename)
        else:
           
            mark = ""
            for line in lines:
                content = line.rstrip()
                if content.startswith("VB_p1"):
                    mark = "VB_p1"
                    continue
                if mark == "VB_p1":
                    self.p1 = float(content)
                    mark = ""
                if content.startswith("VB_p2"):
                    mark = "VB_p2"
                    continue
                if mark == "VB_p2":
                    self.p2 = float(content)
                    mark = ""
                if content.startswith("VB_p3"):
                    mark = "VB_p3"
                    continue
                if mark == "VB_p3":
                    self.p3 = float(content)
                    mark = ""
                    continue
                if content.startswith("mean_length_at_age"):
                    mark = "mean_length_at_age"
                    continue
                if mark == "mean_length_at_age":
                    mark = ""
                    growthCurveYData = content.split()
                if content.startswith("stddev_length_at_age"):
                    mark = "stddev_length_at_age"
                    continue
                if mark == "stddev_length_at_age":
                    mark = ""
                    stddev = content.split()
                if content.startswith("estimated_p_hat"):
                    mark = "p_hat"
                    continue
                if mark == "p_hat" and not content.startswith("individual_likelihood"):
                    pHatData = content.split()
                    if pHatData[0] not in pHatYear:
                        pHatYear[pHatData[0]] = pHatData[0]
                    if pHatData[1] not in pHatFleet:
                        pHatFleet[pHatData[1]] = pHatData[1]
                
                if content.startswith("individual_likelihood"):
                    mark = "likelihood"
                    continue
                if mark == "likelihood" and not content.startswith("end_of_file"):
                    likelihoodData = content.split()
                    if likelihoodData[0] not in likelihoodYear:
                        likelihoodYear[likelihoodData[0]] = likelihoodData[0]
                    if likelihoodData[1] not in likelihoodFleet:
                        likelihoodFleet[likelihoodData[1]] = likelihoodData[1]
                
                        
                
                if content.startswith("end_of_file"):
                    break
                    
                    
                    
                    
        growthCurveXData = list(range(0,16))    
        addStdDevData = [float(x) + float(y) for x, y in zip(growthCurveYData, stddev)]  
        minusStdDevData = [float(x) - float(y) for x, y in zip(growthCurveYData, stddev)]  
#         ydata = [self.p1*(1.-exp(-self.p2*(i-self.p3))) for i in range(0,16)]
        
        # create an axis
        growthCurveAX = self.growthCurveFigure.add_subplot(111)
        growthCurveAX.set_xlabel("Age (year)", fontsize=10)
        growthCurveAX.set_ylabel("Length (cm)", fontsize=10)
        growthCurveAX.tick_params(axis='both', labelsize=10)
        growthCurveAX.set_title('Estimated Growth Curve')
        growthCurveAX.set_xticks(growthCurveXData)
        # plot data
        growthCurveAX.plot(growthCurveXData,growthCurveYData, 'kD-',growthCurveXData,addStdDevData,'k--',growthCurveXData,minusStdDevData,'k--')

        # refresh canvas
        self.growthCurveCanvas.draw()
        
        
        self.pHatYearSelect.addItems(sorted(pHatYear))
        try:
            self.pHatFleetSelect.addItems(sorted(pHatFleet))
        except Exception as e:
            print(e)
        
        
        
        self.likelihoodYearSelect.addItems(sorted(likelihoodYear))
        self.likelihoodFleetSelect.addItems(sorted(likelihoodFleet))
    
    def plotPHat(self):
        lengthBinVector = []
        pHatMatrix = []
        self.filename = "./report.dat"
        year = self.pHatYearSelect.currentText()
        fleet = self.pHatFleetSelect.currentText()
        
        if len(year) > 0  and len(fleet) > 0:
            with open(self.filename) as file_object:
                lines = file_object.readlines()
            if not lines:
                message = "Failed to read {0}".format(self.filename)
            else:
           
                mark = ""
                for line in lines:
                    content = line.rstrip()
                
                    if not content.startswith("estimated_p_hat") and mark != "p_hat":
                        continue
                    if content.startswith("estimated_p_hat"):
                        mark = "p_hat"
                        continue
                    if mark == "p_hat" and not content.startswith("individual_likelihood"):
                        pHatData = content.split()
                    
                        pHatList = pHatData[3:]
                        pHatList = list(map(float, pHatList))
                        if pHatData[0] == year and pHatData[1] == fleet:
                            lengthBinVector.append(pHatData[2])
                            pHatMatrix.append(pHatList)
                    if content.startswith(("individual_likelihood","end_of_file")):
                        mark = ""
                        break
       
            pHatXData = list(range(0,16)) 
            lengthBinVector = list(map(int,lengthBinVector))    
            
            self.pHatFigure.clear()
            pHatAX = self.pHatFigure.add_subplot(111)
            pHatAX.set_xlabel("Age (year)", fontsize=10)
            pHatAX.set_ylabel("Length Bins (cm)", fontsize=10)
            pHatAX.tick_params(axis='both', labelsize=10)
            pHatAX.set_title('p-hat')
            pHatAX.set_xticks(pHatXData)
            # plot data
            try:
                
                cax = pHatAX.pcolormesh(pHatXData,lengthBinVector, pHatMatrix,cmap='jet')
                
#                 self.pHatFigure.clear()
                
                
                
                self.pHatFigure.colorbar(cax)
                
            except Exception as e:
                print(e)

            # refresh canvas
            self.pHatCanvas.draw()
        
        
    def plotLikeliHood(self):    
        lengthBinVector1 = []
        likeliHoodMatrix = []
        self.filename = "./report.dat"
        year = self.likelihoodYearSelect.currentText()
        fleet = self.likelihoodFleetSelect.currentText()
        
        if len(year) > 0  and len(fleet) > 0:
            with open(self.filename) as file_object:
                lines = file_object.readlines()
            if not lines:
                message = "Failed to read {0}".format(self.filename)
            else:
           
                mark = ""
                for line in lines:
                    content = line.rstrip()
                
                    if not content.startswith("individual_likelihood") and mark != "likelihood":
                        continue
                    if content.startswith("individual_likelihood"):
                        mark = "likelihood"
                        continue
                    if mark == "likelihood" and not content.startswith("p_hat"):
                        liklihoodData = content.split()
                    
                        likelihoodList = liklihoodData[3:]
                        likelihoodList = list(map(float, likelihoodList))
                        if liklihoodData[0] == year and liklihoodData[1] == fleet:
                            lengthBinVector1.append(liklihoodData[2])
                            likeliHoodMatrix.append(likelihoodList)
                    if content.startswith(("p_hat","end_of_file")):
                        mark = ""
                        break
       
            likelihoodXData = list(range(0,16)) 
            lengthBinVector1 = list(map(int,lengthBinVector1))    
            
            self.likelihoodFigure.clear()
            likelihoodAX = self.likelihoodFigure.add_subplot(111)
            likelihoodAX.set_xlabel("Age (year)", fontsize=10)
            likelihoodAX.set_ylabel("Length Bins (cm)", fontsize=10)
            likelihoodAX.tick_params(axis='both', labelsize=10)
            likelihoodAX.set_title('likelihood')
            likelihoodAX.set_xticks(likelihoodXData)
            # plot data
            try:
                
                cax = likelihoodAX.pcolormesh(likelihoodXData,lengthBinVector1, likeliHoodMatrix,cmap='jet')
                
#                 self.pHatFigure.clear()
                
                
                
                self.likelihoodFigure.colorbar(cax)
                
            except Exception as e:
                print(e)

            # refresh canvas
            self.likelihoodCanvas.draw()
    
    def updateAgeProportionTable(self):
        self.ageProportionColumnList = self.ageProportionColumnList[1:3]
        for i in range(len(self.ageProportionMatrix[0])-1):
            self.ageProportionColumnList.append("Age"+str(i))
        
        
        self.ageProportionTable.clear()
        self.ageProportionTable.setRowCount(len(self.ageProportionMatrix))
        self.ageProportionTable.setColumnCount(len(self.ageProportionMatrix[0]))
        self.ageProportionTable.setHorizontalHeaderLabels(self.ageProportionColumnList)
        self.ageProportionTable.setAlternatingRowColors(True)
        self.ageProportionTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ageProportionTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.ageProportionTable.setSelectionMode(QTableWidget.SingleSelection)
        
        for i in range(len(self.ageProportionMatrix)):
            ageProportionList = self.ageProportionMatrix[i]
            for j in range(len(ageProportionList)):
                item = QTableWidgetItem(ageProportionList[j])
                self.ageProportionTable.setItem(i, j, item)
            
    def updateFishLengthTable(self):
        self.fishLengthColumnList = self.fishLengthColumnList[1:4]
        for i in range(len(self.fishLengthMatrix[0])-3):
            self.fishLengthColumnList.append("Age"+str(i))
        
        
        self.fishLengthTable.clear()
        self.fishLengthTable.setRowCount(len(self.fishLengthMatrix))
        self.fishLengthTable.setColumnCount(len(self.fishLengthMatrix[0]))
        self.fishLengthTable.setHorizontalHeaderLabels(self.fishLengthColumnList)
        self.fishLengthTable.setAlternatingRowColors(True)
        self.fishLengthTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.fishLengthTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.fishLengthTable.setSelectionMode(QTableWidget.SingleSelection)
        
        for i in range(len(self.fishLengthMatrix)):
            fishLengthList = self.fishLengthMatrix[i]
            for j in range(len(fishLengthList)):
                item = QTableWidgetItem(fishLengthList[j])
                self.fishLengthTable.setItem(i, j, item)

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/{0}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            getattr(action, signal).connect(slot)
#            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action


    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)


    def closeEvent(self, event):
        
        settings = QSettings()
        filename = (QVariant(self.filename)
                    if self.filename is not None else QVariant())
        settings.setValue("LastFile", filename)
        recentFiles = (QVariant(self.recentFiles)
                           if self.recentFiles else QVariant())
        settings.setValue("RecentFiles", recentFiles)
        settings.setValue("MainWindow/Geometry", QVariant(
                             self.saveGeometry()))
        settings.setValue("MainWindow/State", QVariant(
                            self.saveState()))
       


    def loadInitialFile(self):
        settings = QSettings()
        fname = settings.value("LastFile").toString()
        if fname and QFile.exists(fname):
            self.loadFile(fname)


    def updateStatus(self, message):
        self.statusBar().showMessage(message, 10000)

    def updateFileMenu(self):
        self.fileMenu.clear()
        self.addActions(self.fileMenu, self.fileMenuActions[:-1])
        current = (self.filename
                   if self.filename is not None else None)
        recentFiles = []
        for fname in self.recentFiles:
            if fname != current and QFile.exists(fname):
                recentFiles.append(fname)
        if recentFiles:
            self.fileMenu.addSeparator()
            for i, fname in enumerate(recentFiles):
                action = QAction(QIcon(":/icon.png"),
                        "&{0} {1}".format(i + 1, QFileInfo(
                        fname).fileName()), self)
                action.setData(QVariant(fname))
                action.triggered.connect(self.loadFile)

                self.fileMenu.addAction(action)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.fileMenuActions[-1])




    def fileDataOpen(self):
        
        fname = QFileDialog.getOpenFileName(self,
                "File Chooser - Choose Data File", "/",
                "Data File (*.dat *.txt *.rtf);;All Files (*.*)")
        
        
        if fname:
            currentDir = os.getcwd()
            filename = os.path.basename(fname[0])
            fullPath = os.path.join(currentDir,filename)
            shutil.copy(fname[0],fullPath)
            
            
            self.loadDataFile(fname)
            
    def filePinOpen(self):
        fname = QFileDialog.getOpenFileName(self,
                "File Chooser - Choose Pin File", "/",
                "Pin File (*.pin);;All Files (*.*)")
        
        if fname:
            currentDir = os.getcwd()
            filename = os.path.basename(fname[0])
            fullPath = os.path.join(currentDir,filename)
            shutil.copy(fname[0],fullPath)
            self.loadPinFile(fname)


    def loadDataFile(self, fname=None):
        fname = fname[0]
        varianceOption = 1
        growthParamIndex = 1
        varianceParamIndex = 1
        if fname:
            self.filename = None
            with open(fname) as file_object:
                lines = file_object.readlines()
            if not lines:
                message = "Failed to read {0}".format(fname)
            else:
                self.addRecentFile(fname)
#                 self.
                mark = ""
                for line in lines:
                    content = line.rstrip()
                    if content.startswith("#") and "growth model option" in content.lower():
                        mark = "growth model option"
                        continue;
                    if content.startswith("# growth parameters"):
                        mark = "growth parameters"
                        continue;
                    if content.startswith("#") and "estimate variance option" in content.lower():
                        mark = "estimate variance option"
                        continue;
                    if content.startswith("# first length"):
                        mark = "length"
                        continue;
                    if content.startswith("# first age"):
                        mark = "age"
                        continue;
                    if content.startswith("# first year"):
                        mark = "year"
                        continue;
                    if content.startswith("# age proportion"):
                        mark = "age proportion"
                        continue;
                    if content.startswith("# fish length"):
                        mark = "fish length"
                        continue;
                    if content.startswith("# numbers of fleet"):
                        mark = "number of fleet"
                        continue;

                    
                    
                    
                    if mark == "growth model option":
                        self.modelOptions[int(content) - 1].setChecked(True)
                        self.modelOption = int(content)
                        mark = ""
                    elif mark == "growth parameters" and "# estimate variance option" not in content.lower():
                        
                        paramList = content.split()
                        if self.modelOption == 1 or self.modelOption == 2:
                            if growthParamIndex == 1:
                                self.firstLowerBoundLabel.setText("Linf Lower Bound:")
                                self.firstLowerBoundEdit.setText(paramList[0])
                                self.firstUpperBoundLabel.setText("Linf Upper Bound:")
                                self.firstUpperBoundEdit.setText(paramList[1])
                                self.firstPhaseLabel.setText("Linf Phase:")
                                self.firstPhaseEdit.setText(paramList[2])
                            elif growthParamIndex == 2:
                                self.secondLowerBoundLabel.setText("K Lower Bound:")
                                self.secondLowerBoundEdit.setText(paramList[0])
                                self.secondUpperBoundLabel.setText("K Upper Bound:")
                                self.secondUpperBoundEdit.setText(paramList[1])
                                self.secondPhaseLabel.setText("K Phase:")
                                self.secondPhaseEdit.setText(paramList[2])
                            elif growthParamIndex == 3:
                                self.thirdLowerBoundLabel.setText("t0 Lower Bound:")
                                self.thirdLowerBoundEdit.setText(paramList[0])
                                self.thirdUpperBoundLabel.setText("t0 Upper Bound:")
                                self.thirdUpperBoundEdit.setText(paramList[1])
                                self.thirdPhaseLabel.setText("t0 Phase:")
                                self.thirdPhaseEdit.setText(paramList[2])
                            elif growthParamIndex == 4:
                                self.fourthLowerBoundLabel.hide()
                                self.fourthLowerBoundEdit.hide()
                                self.fourthUpperBoundLabel.hide()
                                self.fourthUpperBoundEdit.hide()
                                self.fourthPhaseLabel.hide()
                                self.fourthPhaseEdit.hide()
                        
                        
                        elif self.modelOption == 3:
                            if growthParamIndex == 1:
                                self.firstLowerBoundLabel.setText("Alpha Lower Bound:")
                                self.firstLowerBoundEdit.setText()
                                self.firstUpperBoundLabel.setText("Alpha Upper Bound:")
                                self.firstUpperBoundEdit.setText()
                                self.firstPhaseLabel.setText("Alpha Phase:")
                                self.firstPhaseEdit.setText()
                            elif  growthParamIndex == 2:                            
                                self.secondLowerBoundLabel.setText("Beta Lower Bound:")
                                self.secondLowerBoundEdit.setText()
                                self.secondUpperBoundLabel.setText("Beta Upper Bound:")
                                self.secondUpperBoundEdit.setText()
                                self.secondPhaseLabel.setText("Beta Phase:")
                                self.secondPhaseEdit.setText()
                            elif growthParamIndex == 3:
                                self.thirdLowerBoundLabel.setText("K Lower Bound:")
                                self.thirdLowerBoundEdit.setText()
                                self.thirdUpperBoundLabel.setText("K Upper Bound:")
                                self.thirdUpperBoundEdit.setText()
                                self.thirdPhaseLabel.setText("K Phase:")
                                self.thirdPhaseEdit.setText()
                            elif growthParamIndex == 4:
                                self.fourthLowerBoundLabel.hide()
                                self.fourthLowerBoundEdit.hide()
                                self.fourthUpperBoundLabel.hide()
                                self.fourthUpperBoundEdit.hide()
                                self.fourthPhaseLabel.hide()
                                self.fourthPhaseEdit.hide()
                        
                        elif self.modelOption == 4:
                            if growthParamIndex == 1:
                                self.firstLowerBoundLabel.setText("Linf Lower Bound:")
                                self.firstLowerBoundEdit.setText()
                                self.firstUpperBoundLabel.setText("Linf Upper Bound:")
                                self.firstUpperBoundEdit.setText()
                                self.firstPhaseLabel.setText("Linf Phase:")
                                self.firstPhaseEdit.setText()
                            elif growthParamIndex == 2:
                                self.secondLowerBoundLabel.setText("K Lower Bound:")
                                self.secondLowerBoundEdit.setText()
                                self.secondUpperBoundLabel.setText("K Upper Bound:")
                                self.secondUpperBoundEdit.setText()
                                self.secondPhaseLabel.setText("K Phase:")
                                self.secondPhaseEdit.setText()
                            elif growthParamIndex == 3:
                                self.thirdLowerBoundLabel.setText("t0 Lower Bound:")
                                self.thirdLowerBoundEdit.setText()
                                self.thirdUpperBoundLabel.setText("t0 Upper Bound:")
                                self.thirdUpperBoundEdit.setText()
                                self.thirdPhaseLabel.setText("t0 Phase:")
                                self.thirdPhaseEdit.setText()
                            elif growthParamIndex == 4:
                                self.fourthLowerBoundLabel.setVisible()
                                self.fourthLowerBoundEdit.setVisible()
                                self.fourthUpperBoundLabel.setVisible()
                                self.fourthUpperBoundEdit.setVisible()
                                self.fourthPhaseLabel.setVisible()
                                self.fourthPhaseEdit.setVisible()
                        growthParamIndex = growthParamIndex + 1
                            
                    elif mark == "growth parameters" and "# estimate variance option" in content.lower():    
                        mark = ""
                    elif mark == "estimate variance option":
                        if(varianceParamIndex == 1):
                            self.varianceOptions[int(content) - 1].setChecked(True)
                            varianceOption = int(content)
                        if(varianceParamIndex == 2):
                            paramList = content.split()
                            if varianceOption == 1:
                                self.varianceLowerBoundLabel.setText("CV Lower Bound:")
                                self.varianceLowerBoundEdit.setText(paramList[0])
                                self.varianceUpperBoundLabel.setText("CV Upper Bound:")
                                self.varianceUpperBoundEdit.setText(paramList[1])
                                self.variancePhaseLabel.setText("CV Phase:")
                                self.variancePhaseEdit.setText(paramList[2])
                                    
                                self.varianceLowerBoundLabel2.hide()
                                self.varianceLowerBoundEdit2.hide()
                                self.varianceUpperBoundLabel2.hide()
                                self.varianceUpperBoundEdit2.hide()
                                self.variancePhaseLabel2.hide()
                                self.variancePhaseEdit2.hide()
                            elif varianceOption == 2:
                                self.varianceLowerBoundLabel.setText("SD Lower Bound:")
                                self.varianceLowerBoundEdit.setText(paramList[0])
                                self.varianceUpperBoundLabel.setText("SD Upper Bound:")
                                self.varianceUpperBoundEdit.setText(paramList[1])
                                self.variancePhaseLabel.setText("SD Phase:")
                                self.variancePhaseEdit.setText(paramList[2])
                                    
                                self.varianceLowerBoundLabel2.hide()
                                self.varianceLowerBoundEdit2.hide()
                                self.varianceUpperBoundLabel2.hide()
                                self.varianceUpperBoundEdit2.hide()
                                self.variancePhaseLabel2.hide()
                                self.variancePhaseEdit2.hide()
                            elif varianceOption == 3:
                                self.varianceLowerBoundLabel.setText("CV1 Lower Bound:")
                                self.varianceLowerBoundEdit.setText(paramList[0])
                                self.varianceUpperBoundLabel.setText("CV1 Upper Bound:")
                                self.varianceUpperBoundEdit.setText(paramList[1])
                                self.variancePhaseLabel.setText("CV1 Phase:")
                                self.variancePhaseEdit.setText(paramList[2])
                                    
                                self.varianceLowerBoundLabel2.setVisible()
                                self.varianceLowerBoundEdit2.setVisible()
                                self.varianceUpperBoundLabel2.setVisible()
                                self.varianceUpperBoundEdit2.setVisible()
                                self.variancePhaseLabel2.setVisible()
                                self.variancePhaseEdit2.setVisible()
                        if(varianceParamIndex == 2): 
                            mark = "" 
                        varianceParamIndex = varianceParamIndex + 1
                    elif mark == "length":
                        paramList = content.split()
                        self.firstLengthEdit.setText(paramList[0])
                        self.lastLengthEdit.setText(paramList[1])
                        self.lengthIncrementEdit.setText(paramList[2])
                        mark = "" 
                    elif mark == "age":
                        paramList = content.split()
                        self.firstAgeEdit.setText(paramList[0])
                        self.lastAgeEdit.setText(paramList[1])
                        self.ageIncrementEdit.setText(paramList[2])
                        mark = "" 
                    elif mark == "year":
                        paramList = content.split()
                        self.firstYearEdit.setText(paramList[0])
                        self.lastYearEdit.setText(paramList[1])
                        self.yearIncrementEdit.setText(paramList[2])
                        mark = "" 
                    elif mark == "number of fleet":
                        self.numberOfFleetEdit.setText(content)
                        mark = ""
                        
                    elif mark =="age proportion":
                        self.ageProportionColumnList = content.split()
                        mark = "age proportion data"
                    elif mark == "age proportion data" and "# lines of caal" not in content.lower():
                        ageProportionList = content.split()
                        self.ageProportionMatrix.append(ageProportionList)
                    elif mark == "age proportion data" and "# lines of caal" in content.lower():
                        mark = ""
                    elif mark == "fish length" :
                        self.fishLengthColumnList = content.split()
                        mark = "fish length data"
                    elif mark == "fish length data" and "# end of the file" not in content.lower():
                        fishLengthList = content.split()
                        self.fishLengthMatrix.append(fishLengthList)
                    elif mark == "fish length data" and "# end of the file" in content.lower():
                        mark = ""

                self.inputDataFileEdit.setText(fname)
                
                self.filename = fname
                
                message = "Loaded {0}".format(os.path.basename(fname))
            self.updateStatus(message)
            
            self.updateAgeProportionTable()
            
            self.updateFishLengthTable()
            
            
            
    def loadPinFile(self, fname=None):
        fname = fname[0]
        if fname:
            self.filename = None
            with open(fname) as file_object:
                lines = file_object.readlines()
            if not lines:
                message = "Failed to read {0}".format(fname)
            else:
                self.addRecentFile(fname)
                mark = ""
                for line in lines:
                    content = line.rstrip()
                    if content.startswith("#p1"):
                        mark = "p1"
                        continue;
                    if content.startswith("#p2"):
                        mark = "p2"
                        continue;
                    if content.startswith("#p3"):
                        mark = "p3"
                        continue;
                    if content.startswith("#p4"):
                        mark = "p4"
                        continue;
                    if content.startswith("#cv"):
                        mark = "cv"
                        continue;
                    
                    if mark == "p1":
                        self.linfEdit.setText(content)
                        mark = ""
                    elif mark == "p2":
                        self.kEdit.setText(content)
                        mark = ""
                    elif mark == "p3":
                        self.t0Edit.setText(content)
                        mark = ""
                    elif mark == "p4":
                        self.pEdit.setText(content)
                        if self.modelOption == 4:
                            self.pEdit.setVisible()
                        else:
                            self.pEdit.hide()
                        mark = ""
                    elif mark == "cv":
                        self.cvEdit.setText(content)
                        mark = ""
                    
                self.inputPinFileEdit.setText(fname)
                
                self.filename = fname
                
                
                message = "Loaded {0}".format(os.path.basename(fname))
            self.updateStatus(message)
            
    def addRecentFile(self, fname):
        if fname is None:
            return
        if fname in self.recentFiles:
            self.recentFiles.append(fname)
            while self.recentFiles.count() > 9:
                self.recentFiles.pop(0)



    def filePrint(self):
        if self.image.isNull():
            return
        if self.printer is None:
            self.printer = QPrinter(QPrinter.HighResolution)
            self.printer.setPageSize(QPrinter.Letter)
        form = QPrintDialog(self.printer, self)
        if form.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(),
                                size.height())
            painter.drawImage(0, 0, self.image)




 
        
    def viewReport(self):
        print("View Report")
        try:
            currentDirectory = os.getcwd();
            fullPath = os.path.join(currentDirectory,"report.dat")
            #os.startfile(fullPath)
            subprocess.Popen(["notepad.exe", fullPath])
            #os.system("start "+fullPath)
        except Exception as e:
            print(e)
        
    
    def viewEchoInputFile(self):
        print("View Echo Input File")
        try:
            currentDirectory = os.getcwd();
            fullPath = os.path.join(currentDirectory,"echoinput.dat")
            subprocess.Popen(["notepad.exe", fullPath])
        except Exception as e:
            print(e)
    
    def runCAAL(self):
        print("Run CAAL")
#         self.inputDataFileEdit.text()
#         directory = os.path.dirname(self.inputDataFileEdit.text())
#         file_list = os.listdir(directory)
        runFileName = "caal.exe"
        runPath = os.path.join(os.getcwd(),runFileName)
#         if runFileName in file_list:
#             runPath = posixpath.join(directory,runFileName)
#         print ("OK")
        pid = subprocess.run(runPath, stdout=None, stderr=None, stdin=None, shell=True)
        
        QMessageBox.warning(self, "CAAL","CAAL Model Has Successfully Completed.",QMessageBox.Ok)
        print ("OK")
         
    def selectProgram(self):
        print("Select Program")
    
    def inputData(self):
        self.stackedWidget.setCurrentIndex(0)
#         self.inputPinFileEdit.show()
        print("Switch to input data")
    
    def modelResult(self):
        self.plot()
        self.pHatYearSelect.currentIndexChanged.connect(self.plotPHat)
        self.pHatFleetSelect.currentIndexChanged.connect(self.plotPHat)
        self.likelihoodYearSelect.currentIndexChanged.connect(self.plotLikeliHood)
        self.likelihoodFleetSelect
        self.stackedWidget.setCurrentIndex(1)
#         self.inputPinFileEdit.hide()
        print("Switch to model result")
        
    def helpAbout(self):
        QMessageBox.about(self, "About CAAL",
                """<b>CAAL</b> v {0}
                <p>All rights reserved.
                <p>This application can be used to run CAAL model.
                <p>Python {1} - Qt {2} - PyQt {3} on {4}""".format(
                __version__, platform.python_version(),
                QT_VERSION_STR, PYQT_VERSION_STR,
                platform.system()))
    
    def helpUsing(self):
        print("Help Using")
    def helpTechManual(self):
        print("Help Tech Manual")
        #file = open(":/technicalManual")
        try:
            currentDirectory = os.getcwd();
            fullPath = os.path.join(currentDirectory,"file/technicalManual.pdf")
            os.startfile(fullPath)
        except Exception as e:
            print(e)
        
    def helpUserManual(self):
        print("Help User Manual")

#     def helpHelp(self):
#         form = helpform.HelpForm("index.html", self)
#         form.show()


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("")
    app.setOrganizationDomain("qtrac.eu")
    app.setApplicationName("CAAL")
    app.setWindowIcon(QIcon(":/main.gif"))
    form = MainWindow()
    form.show()
    app.exec_()


main()

if __name__ == '__main__':
    pass
