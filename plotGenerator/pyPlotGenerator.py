#!/usr/bin/python3

############################################################################################
# Imports
############################################################################################
import os, sys
import guidata
import tempfile
import os.path
import signal
import imp
from operator import itemgetter
from guidata.qt.QtGui import QMainWindow, QSplitter
from guidata.dataset.qtwidgets import DataSetShowGroupBox, DataSetEditGroupBox
from guidata.dataset.datatypes import (DataSet, BeginGroup, EndGroup,
                                       BeginTabGroup, EndTabGroup)
from guidata.dataset.dataitems import (ChoiceItem, FloatItem, StringItem,
                                       DirectoryItem, FileOpenItem, MultipleChoiceItem)

from guidata.configtools import get_icon
from guidata.qthelpers import create_action, add_actions, get_std_icon
from guidata.dataset.qtwidgets import DataSetEditLayout, DataSetShowLayout
from guidata.dataset.qtitemwidgets import DataSetWidget
import guidata.dataset.datatypes as dt
import guidata.dataset.dataitems as di
from operator import itemgetter, attrgetter
signal.signal(signal.SIGINT, signal.SIG_DFL)


############################################################################################
# Configuration list class
############################################################################################
class ConfigurationList:
  def __init__(self):
    self.title = []
    self.configs = []
    self.details = []
    self.name = []
    self.tab = 0
    self.values_tab = -1
    self.use_for_plot = 0
    self.selectAll = 0
    self.sort = 0
    self.showLabels = 1


## Plot results definition
prLabel   = 0
prX       = 1
prY       = 2
prYextra  = 3

############################################################################################
# Auxiliary functions
############################################################################################
def filterResults( results, col, value):
  filtResults = []
  for line in results:
    if line[col - 1] == value:
      filtResults.append(line)
  return filtResults

def filterSeveralResults( results, col, values):
  filtResults = []
  for line in results:
    for v in values:
      if line[col - 1] == v:
        filtResults.append(line)
        break
  return filtResults

# Returns an array of [ detail, name ]
def resultsGetDetails( results, col):
  members = []
  for line in results:
    value = line[col - 1]
    if value not in members:
      members.append( value )

  outMembers = []
  for line in members:
    outMembers.append([line, line])
  return outMembers


# Find name in mappins
def findMap( mappings, config):
  name = config
  for line in mappings:
    if line[0] == config:
      name = line[1]
      return name
  return name

# Find name in mappins
def translateMappings( mappings, details):
  outDetails = []
  for line in details:
    outDetails.append( [line[0], findMap( mappings, line[0] )] )
  return outDetails

def readResults(fname):
  if os.path.isfile(fname):
    print("Reading results!!")
    for line in open(fname).readlines():
      if not line.startswith("#"):
        ResultsTable.append(line.split())

def processLabel(label):
  if label != "":
    label = label[:-3]
    label = label.replace('_', '\_')
  return label

############################################################################################
# Default values
############################################################################################
TypeDefault = 0
ConfigVersion = 1
ConfigMapping = []
LatexTemplateDefault = """

"""
GnuplotTerminals = ["eps", "pdf"]

GnuPlotTemplateDefault = """
font 'TimesNewRoman,14'

set datafile missing '-'

set grid
#set size square {1,.5}

set title center  offset character 0, -.9

set xlabel center
set ylabel center offset character 1, 0

set key spacing 1 width 0

set style line 4 lc 1 lt  1 lw 2 pt  2 ps 1
set style line 2 lc 2 lt  2 lw 2 pt  3 ps 1
set style line 3 lc 3 lt  4 lw 2 pt  4 ps 1
set style line 1 lc 4 lt  4 lw 2 pt  10 ps 1
set style line 5 lc 7 lt  3 lw 2 pt  6 ps 1
set style line 6 lc 8 lt  6 lw 2 pt  8 ps 1
set style line 7 lc 2 lt  7 lw 2 pt  8 ps 1
set style line 8 lc 3 lt  8 lw 2 pt  9 ps 1
set style line 9 lc 4 lt  9 lw 2 pt  10 ps 1

set style line 100 lc 1 lw 3
set style line 101 lc 4 lw 3
set style line 102 lc 2 lw 3
set style line 103 lc 3 lw 3

#set rmargin 1

"""

GnuPlotTemplateBarPlotDefault = """
set style histogram clustered  gap 2
set grid y
set style data histograms
set style fill solid
set boxwidth 1

set xtics rotate by 45 right
set bmargin 5

"""

GnuPlotTemplateExtra = """
# Extra template
"""

GnuPlotTemplateBarPlotExtra = """
# Extra template
"""

FilterNonExistent = 0
ResultsFileDefault = ""
PlotFileDefault = ""
KeepPlotFileDefault = 0
PlotLegendDefault = 0
AxisLimitDefaultX = ""
AxisLimitDefaultY = ""

XValues = []
YValues = []
AxisValues = []

XValueDefault = 0
YValueDefault = 0

GenerateBarPlotDefault = 0
GnuplotTerminalDefault = "eps"

############################################################################################
# Read configuration
############################################################################################
ConfigFileName = "cfgData.py"
exec(open(ConfigFileName).read())

for i in  XValues:
  AxisValues.append( i )
for i in YValues:
  AxisValues.append( i )

############################################################################################
# Read data file
############################################################################################
ResultsTable = []
readResults(ResultsFileDefault)
if not ResultsTable:
  FilterNonExistent = 0
if FilterNonExistent:
  print("Filtering results")

# Import configs using two methods
# either write details or configs + names
ConfigsImport = Configs
Configs = []
if ConfigVersion == 1:
  for i in range( len( ConfigsImport ) ):
    currConfig = ConfigsImport[i]
    for j in range( len( ConfigsImport[i].configs ) ):
      currConfig.details.append( [ ConfigsImport[i].configs[j], ConfigsImport[i].name[j] ] )
    Configs.append( currConfig )

elif ConfigVersion == 2:
  for i in range( len( ConfigsImport ) ):
    currConfig = ConfigsImport[i]
    for j in range( len( ConfigsImport[i].details ) ):
      if FilterNonExistent == 1:
        currResults = filterResults( ResultsTable, ConfigsImport[i].tab, ConfigsImport[i].details[j][0] )
      else:
        currResults = 1
      if currResults:
        currConfig.configs.append( ConfigsImport[i].details[j][0] )
        currConfig.name.append( ConfigsImport[i].details[j][1] )
    Configs.append( currConfig )

elif ConfigVersion == 3:
  for i in range( len( ConfigsImport ) ):
    currConfig = ConfigsImport[i]
    currConfig.details = resultsGetDetails( ResultsTable, currConfig.tab)
    currConfig.details = translateMappings( ConfigMapping, currConfig.details )

    if currConfig.sort == 1:
      currConfig.details.sort(key=itemgetter(0))

    for j in range( len( currConfig.details ) ):
      currConfig.configs.append( currConfig.details[j][0] )
      currConfig.name.append( currConfig.details[j][1] )
    Configs.append( currConfig )




############################################################################################
# Main classes
############################################################################################
class AbstractGenerator:

  def __init__(self, PltConfig):
    self.PltConfig = PltConfig

  def getData(self, currentFileConfigChoice, currentPlotConfigChoice):

    plotResults = []
    barDataIndex = 0

    ## Filter the result set for the different line curves of the current plot
    filteredResults = self.OutputResults
    for i in range( len( self.fileConfig )):
      curr_idx = self.fileConfigChoice[i][currentFileConfigChoice[i]]
      filteredResults = filterResults( filteredResults, self.fileConfig[i].tab, self.fileConfig[i].configs[curr_idx] )

    applyFiltering = False
    for i in range( len( self.plotConfig )):
      curr_idx = self.plotConfigChoice[i][currentPlotConfigChoice[i]]
      if self.PltConfig.selectXValues == self.plotConfig[i].tab or self.PltConfig.selectXValues == self.plotConfig[i].values_tab:
        applyFiltering = True
        continue
      filteredResults = filterResults( filteredResults, self.plotConfig[i].tab, self.plotConfig[i].configs[curr_idx] )

    currentPointConfigChoice = [ int(0) for i in range( len( self.pointConfig ) )]
    for point_idx in range( self.numberPoints ):
      curr_point = filteredResults
      barLabel = ""
      for i in range( len( self.pointConfig )):
        curr_idx = self.pointConfigChoice[i][currentPointConfigChoice[i]]
        curr_point = filterResults( curr_point, self.pointConfig[i].tab, self.pointConfig[i].configs[curr_idx] )
        barLabel += self.pointConfig[i].name[curr_idx] + " - "

      if not curr_point == []:
        curr_point = curr_point[0] # Discard remaining results
        # TODO: Add average

        currPlotData = []
        currPlotData.append( "\"" + processLabel(barLabel) + "\"" )
        currPlotData.append( curr_point[self.PltConfig.selectXValues - 1] )
        currPlotData.append( curr_point[self.PltConfig.selectYValues - 1] )
        if self.PltConfig.showExtra:
          currPlotData.append( curr_point[self.PltConfig.selectExtraYValues - 1] )


        for i in reversed(range( len( self.pointConfig ))):
          if currentPointConfigChoice[i] ==  len( self.pointConfigChoice[i] ) - 1:
            currentPointConfigChoice[i] = 0
          else:
            currentPointConfigChoice[i] += 1
            break

        plotResults.append( currPlotData )

    return plotResults


  def generateOutput(self):

    if self.PltConfig.plotFile == "":
      print( "Empty output!!" )
      return

    if not ResultsTable:
      readResults( self.PltConfig.resultsFile )

    self.OutputResults = ResultsTable

    # General cfg variable
    self.aCfgChoice       = []
    # Configs for each group of plots
    self.fileConfig       = []
    self.fileConfigChoice = []
    # Configs for each plot
    self.plotConfig       = []
    self.plotConfigChoice = []
    # Configs for each point
    self.pointConfig       = []
    self.pointConfigChoice = []

    # Bar plot specific
    self.barPlotLabelsCfg = []

    plotConditions = 1
    self.numberPlots = 1
    self.numberLines = 1
    self.numberPoints = 1

    for i in range( len( Configs )):
      exec("self.aCfgChoice.append( self.PltConfig.cfgChoice%d )" % (i) )
      use_for_plot = False
      use_for_points = False
      for j in self.PltConfig.linesPlotCfg:
        if Configs[i].title == self.PltConfig.aAvailableCfg[j]:
          use_for_plot = True
          break

      for j in self.PltConfig.pointsPlotCfg:
        if Configs[i].title == self.PltConfig.aAvailableCfg[j]:
          use_for_points = True
          break

      if not use_for_points:
        if use_for_plot == 0:
          self.fileConfig.append( Configs[i] )
          self.fileConfigChoice.append( self.aCfgChoice[i] )
          self.numberPlots *= len( self.aCfgChoice[i] )
        else:
          #plotConditions += 1
          self.plotConfig.append( Configs[i] )
          self.plotConfigChoice.append( self.aCfgChoice[i] )
          self.numberLines *= len( self.aCfgChoice[i] )
        configList = []
        for j in self.aCfgChoice[i]:
          configList.append( Configs[i].configs[j] )
        self.OutputResults = filterSeveralResults( self.OutputResults, Configs[i].tab, configList )
      else:
        for label in Configs[i].name:
          self.barPlotLabelsCfg.append( label )
        self.pointConfig.append( Configs[i] )
        self.pointConfigChoice.append( self.aCfgChoice[i] )
        self.numberPoints *= len( self.aCfgChoice[i] )


    if self.numberPlots == 0 or plotConditions == 0:
      return

    print( "Generation %d plots with %d lines and %d points!" % (self.numberPlots, self.numberLines, self.numberPoints) )
    print( "Using columns %d vs %d" % (self.PltConfig.selectXValues - 1, self.PltConfig.selectYValues - 1) )


    self.OutputScript = open( self.PltConfig.plotFile + ".bash", 'w' )
    # Write bash header
    self.OutputScript.write( "#!/bin/bash\n" )

    self.header()

    # Marks which file choice are we plotting
    currentFileConfigChoice = [ int(0) for i in range( len( self.fileConfig ) )]

    # Loops through all files
    for file_idx in range( self.numberPlots ):

      last = False

      ## Configure title and file name
      self.currentFileName = ""
      self.currentTitle = ""
      for i in range( len( self.fileConfig )):
        curr_idx = self.fileConfigChoice[i][currentFileConfigChoice[i]]
        self.currentFileName += self.fileConfig[i].configs[curr_idx] + "_"
        if len(self.fileConfigChoice[i]) > 1:
          if self.fileConfig[i].name[curr_idx]:
            self.currentTitle += self.fileConfig[i].name[curr_idx] + " - "

      self.currentFileName = self.currentFileName[:-1]
      self.currentTitle = self.currentTitle[:-3]

      # Marks which line choice are we plotting
      currentPlotConfigChoice = [ int(0) for i in range( len( self.plotConfig ) )]

      ## Loop through each plot on the current file (several lines)
      for plot_idx in range( self.numberLines ):

        if plot_idx == self.numberLines - 1:
          last = True

        ## configure legend
        self.currentLegend = ""
        for i in range( len( self.plotConfig )):
          curr_idx = self.plotConfigChoice[i][currentPlotConfigChoice[i]]
          self.currentLegend += self.plotConfig[i].name[curr_idx] + " - "

        self.currentLegend = processLabel(self.currentLegend)

        plotResults = self.getData( currentFileConfigChoice, currentPlotConfigChoice )

        ## check empty data -> trigger an exception
        if not plotResults:
          print("No data to plot! skipping...")
          continue

        print( plotResults )
        self.loop( file_idx, plot_idx, last, plotResults)

        ## setup variables for the next line within the same plot
        ## try to increment the last config! if not possible
        ## try to increment the previous one and so one
        for i in reversed(range( len( self.plotConfig ))):
          if currentPlotConfigChoice[i] ==  len( self.plotConfigChoice[i] ) - 1:
            currentPlotConfigChoice[i] = 0
          else:
            currentPlotConfigChoice[i] += 1
            break

      ## setup variables for the next file
      ## try to increment the last config! if not possible
      ## try to increment the previous one and so one
      for i in reversed(range( len( self.fileConfig ))):
        if currentFileConfigChoice[i] ==  len( self.fileConfigChoice[i] ) - 1:
          currentFileConfigChoice[i] = 0
        else:
          currentFileConfigChoice[i] += 1
          break

    self.footer()

    # close gnuplot bash script and plot
    self.OutputScript.close()
    #os.system( "bash " + self.PltConfig.plotFile + ".bash" )
    os.system( "bash " + self.PltConfig.plotFile + ".bash > /dev/null" )

    if self.PltConfig.keepPlotScript == 0:
      os.remove( self.OutputScript_name )

    print("Finished!")


def processLatexText(label):
  label = label.replace( "\\\\", "\\\\\\\\")
  label = label.replace( "%", "\%")
  return label

def formatTableNumber(value):
  value = float(value)
  return str("%.2f" % ( value ) )

class TableGenerator(AbstractGenerator):
  def __init__(self, PltConfig, Template):
    AbstractGenerator.__init__(self, PltConfig)
    self.Template = Template

  def header(self):
    self.OutputScript.write( "pdflatex -halt-on-error << _EOF\n" )
    LatexHeader = """\documentclass{article}
\\usepackage{adjustbox,tabularx, colortbl, ctable, array, multirow}
"""
    self.OutputScript.write( LatexHeader )
    self.OutputScript.write( self.Template.LatexTemplate )

    LatexHeader = "\\usepackage[active,tightpage]{preview} \n\PreviewEnvironment{tabular} \n\\begin{document} \n\pagestyle{empty} \n\\begin{table}[!t] \n\\begin{tabular}"

    # get test data for headers
    plotResults = self.getData( [ int(0) for i in range( len( self.fileConfig ) )], [ int(0) for i in range( len( self.plotConfig ) )] )

    TableHeader = "\\toprule \n"

    LatexHeader += "{"

    self.showTitle = False
    TitleHeader = ""
    for i in range( len( self.fileConfig ) ):
      if len( self.fileConfigChoice[i] ) > 1:
        TitleHeader += self.fileConfig[i].title + " / "

    if not TitleHeader == "":
      LatexHeader += "l"
      TableHeader += processLabel( TitleHeader ) + " & "
      self.showTitle = True
    elif self.PltConfig.showAverage:
      LatexHeader += "l"
      TableHeader += " & "

    LegendHeader = ""
    for cfg in self.plotConfig:
      LegendHeader += cfg.title + " / "

    if not LegendHeader == "":
      LatexHeader += "l"
      TableHeader += processLabel( LegendHeader ) + " & "


    #print( "Generation %d plots with %d lines and %d points!" % (self.numberPlots, self.numberLines, self.numberPoints) )

    self.TableHeaderLabels = []
    for i in range ( self.numberPoints ):
      LatexHeader += "c"
      TableHeader += plotResults[i][prLabel][1:-1] + " & "
      self.TableHeaderLabels.append( plotResults[i][prLabel] )

    TableHeader = TableHeader[:-3]
    LatexHeader += "}"
    TableHeader += "\\\\ \n\midrule"

    self.OutputScript.write( LatexHeader + "\n" + processLatexText( TableHeader ) + "\n" )

    if self.PltConfig.showAverage:
      self.avergeArray = [ float(0) for i in range( self.numberPoints * self.numberLines )]
      self.avergeArrayCount = [ float(0) for i in range( self.numberPoints * self.numberLines )]
    self.avergeIndex = 0

    if self.PltConfig.showExtra:
      self.avergeExtraArray = [ float(0) for i in range( self.numberPoints * self.numberLines )]

  def printAverage(self):

    self.OutputScript.write( "\multirow{" + str( self.numberLines ) + "}{*}{\\textbf{Average}}\n" )

    self.avergeIndex = 0
    ## Loop through each plot on the current file (several lines)
    currentPlotConfigChoice = [ int(0) for i in range( len( self.plotConfig ) )] # Marks which line choice are we plotting
    for plot_idx in range( self.numberLines ):

      TableLine = "& "

      ## configure legend
      self.currentLegend = ""
      for i in range( len( self.plotConfig )):
        curr_idx = self.plotConfigChoice[i][currentPlotConfigChoice[i]]
        self.currentLegend += self.plotConfig[i].name[curr_idx] + " - "
      self.currentLegend = processLabel(self.currentLegend)

      if not self.currentLegend == "":
        TableLine += self.currentLegend + " & "

      for i in range ( self.numberPoints ):
        TableLine += formatTableNumber( self.avergeArray[self.avergeIndex] )
        if self.PltConfig.showExtra:
          TableLine += " (" + formatTableNumber( self.avergeExtraArray[self.avergeIndex] ) + ")"
        TableLine += " & "
        self.avergeIndex += 1

      TableLine = TableLine[:-3]
      TableLine += "\\\\ \n"
      self.OutputScript.write( processLatexText( TableLine ) )

      ## LOOP
      for i in reversed(range( len( self.plotConfig ))):
        if currentPlotConfigChoice[i] ==  len( self.plotConfigChoice[i] ) - 1:
          currentPlotConfigChoice[i] = 0
        else:
          currentPlotConfigChoice[i] += 1
          break



  def footer(self):

    if self.PltConfig.showAverage:
      self.printAverage()

    TableFooter = "\\bottomrule\n\end{tabular}\n\end{table}\n\end{document}"
    self.OutputScript.write( TableFooter )
    self.OutputScript.write( "\n_EOF\n" )
    self.OutputScript.write( "mv texput.pdf " + self.PltConfig.plotFile + ".pdf\n")
    self.OutputScript.write( "rm texput.aux texput.log \n" )


  def loop( self, file_idx, plot_idx, last, plotResults):

    if plot_idx == 0:
      self.avergeIndex = 0

    TableLine = ""

    if plot_idx == 0 and self.showTitle:
      TableLine = "\multirow{" + str( self.numberLines ) + "}{*}{" + self.currentTitle + "}" + " & "
    elif self.PltConfig.showAverage or self.showTitle:
      TableLine += " & "

    if not self.currentLegend == "":
      TableLine += self.currentLegend + " & "

    for i in range ( self.numberPoints ):
      result = []

      for j in range ( len( plotResults ) ):
        if plotResults[j][prLabel] == self.TableHeaderLabels[i]:
          result = plotResults[i]
          break

      if not result == []:
        TableLine += formatTableNumber( result[prY] )
        if self.PltConfig.showExtra:
          TableLine += " (" + formatTableNumber( result[prYextra] ) + ")"
        TableLine += " & "
        if self.PltConfig.showAverage:
          self.avergeArray[self.avergeIndex] = ( self.avergeArray[self.avergeIndex] * self.avergeArrayCount[self.avergeIndex] + float(result[prY]) ) / (self.avergeArrayCount[self.avergeIndex] + 1)
          if self.PltConfig.showExtra:
            self.avergeExtraArray[self.avergeIndex] = ( self.avergeExtraArray[self.avergeIndex] * self.avergeArrayCount[self.avergeIndex] + float(result[prYextra]) ) / (self.avergeArrayCount[self.avergeIndex] + 1)
          self.avergeArrayCount[self.avergeIndex] += 1

      self.avergeIndex += 1

    TableLine = TableLine[:-3]
    TableLine += "\\\\ \n"

    if last:
      TableLine += "\midrule \n"

    self.OutputScript.write( processLatexText( TableLine ) )

class PlotGenerator(AbstractGenerator):
  def __init__(self, PltConfig, Template):
    AbstractGenerator.__init__(self, PltConfig)
    self.Template = Template

  ###
  ### Plot functions
  ###
  def dumpAxisLabels(self, axisName):
    if axisName == "x":
      axis_values = AxisValues
    elif axisName == "y":
      axis_values = AxisValues
    else:
      return

    Label = []
    for i in range( len( axis_values )):
      if axis_values[i][0] == self.PltConfig.selectXValues:
        Label = axis_values[i][1]
        break

    if Label and not self.PltConfig.showBars:
      self.OutputScript.write( "set " + axisName + "label '" + Label + "'\n" )

  def dumpAxisLimits(self, axis, axisLimit):
    if axisLimit:
      axisLimit = axisLimit.split(',')
      if len( axisLimit ) == 3:
        self.OutputScript.write( "set " + axis + "tics " + axisLimit[0] + "," + axisLimit[1] + "," + axisLimit[2] + "\n" )
        self.OutputScript.write( "set " + axis + "range [" + axisLimit[0] + ":" + axisLimit[2] + "]\n" )
      else:
        self.OutputScript.write( "set " + axis + "range [" + axisLimit[0] + ":" + axisLimit[1] + "]\n" )

  def header(self):
    # Selected terminal
    self.selectedGnuplotTerminal = GnuplotTerminals[self.PltConfig.terminalIdx];

    if self.PltConfig.showBars:
      print(self.barPlotLabelsCfg)

    # Start gnuplot configuration
    self.OutputScript.write( "gnuplot << _EOF\n" )

    if self.selectedGnuplotTerminal == "eps":
      GnuPlotTerminalConfig = "set terminal postscript eps enhanced"
    elif self.selectedGnuplotTerminal == "pdf":
      GnuPlotTerminalConfig = "set terminal pdfcairo mono"
    else:
      return

    GnuPlotTerminalConfig += " \\"
    self.OutputScript.write( GnuPlotTerminalConfig )
    self.OutputScript.write( self.Template.GnuPlotTemplate )
    if self.PltConfig.showBars == True:
      self.OutputScript.write( self.Template.GnuPlotTemplateBarPlot )

    self.dumpAxisLabels("x")
    self.dumpAxisLabels("y")

    # Legend configuration
    gnuplotKeyConfiguration = ""
    if not self.PltConfig.legendPosition == 0:
      keyPosition = self.PltConfig.legendPosition[self.PltConfig.legendPositionIdx].lower();
      gnuplotKeyConfiguration += "set key " + keyPosition
      if "left" in keyPosition:
        gnuplotKeyConfiguration += " Left reverse" # swap label and markers
      else:
        gnuplotKeyConfiguration += " Right" # swap label and markers
    else:
      gnuplotKeyConfiguration += "set key off"
    self.OutputScript.write( gnuplotKeyConfiguration + "\n" )

    self.dumpAxisLimits( "x", self.PltConfig.plotXLim )
    self.dumpAxisLimits( "y", self.PltConfig.plotYLim )

    self.plotFileNameList = []

  def footer(self):

    self.OutputScript.write( "_EOF\n" )
    # Finally convert the set of pdf files in one pdf file with multiple pages
    if self.selectedGnuplotTerminal == "eps" or self.selectedGnuplotTerminal == "pdf":
      self.OutputScript.write( "CONV_FILENAMES=\"" )
      for f in self.plotFileNameList:
        self.OutputScript.write( f + ".pdf " )
      self.OutputScript.write( "\"\n" )
      convert_cmd = "gs -q -sPAPERSIZE=letter -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=" +  self.PltConfig.plotFile + ".pdf"

      if self.selectedGnuplotTerminal == "eps":
        self.OutputScript.write( "for f in $CONV_FILENAMES; do\n" )
        self.OutputScript.write( "ps2pdf -dEPSCrop ${f%.*}.eps ${f}\n" )
        self.OutputScript.write( "rm ${f%.*}.eps\n" )
        self.OutputScript.write( "done \n" )

      self.OutputScript.write( convert_cmd + " $CONV_FILENAMES \n")
      self.OutputScript.write( "rm ${CONV_FILENAMES} \n" )

  def loop(self, file_idx, plot_idx, last, plotResults):

    if not self.PltConfig.showBars:
      plotResults = sorted(plotResults, key=lambda line: float(line[1]))
    # Init gnuplot data point and command
    if plot_idx == 0:
      self.plotData = []
      self.plotCommand = "plot"

    for line in plotResults:
      self.plotData.append( line )
    self.plotData.append( ["e"] )

    if self.PltConfig.showBars:
      self.plotCommand += " '-' using " + str(prY+1) + ":xtic(" + str(prLabel+1) + ") ls " + str( plot_idx + 100 )
      #self.plotCommand += " ti col"
    else:
      self.plotCommand += " '-' using " + str(prX+1) + ":" + str(prY+1) + " w lp ls " + str( plot_idx + 1 )
    self.plotCommand += " title '" + self.currentLegend + "',"

    if last:
      self.plotFileNameList.append( self.currentFileName ) # keep a list of files to convert
      if self.selectedGnuplotTerminal == "eps":
        self.currentFileName += ".eps"
      elif self.selectedGnuplotTerminal == "pdf":
        self.currentFileName += ".pdf"

      self.OutputScript.write( "set output '"  + self.currentFileName + "'\n" )

      if self.PltConfig.showTitle:
        self.OutputScript.write( "set title '" + self.currentTitle + "'\n" )
      else:
        self.OutputScript.write( "unset title'\n" )

      self.OutputScript.write( self.plotCommand[:-1] + "\n" )
      for line in self.plotData:
        for item in line:
          self.OutputScript.write( "%s " % (item) )
        self.OutputScript.write( "\n")
      self.OutputScript.write( "\n")



class PlotConfiguration(dt.DataSet):
  ############################################################################################
  # Class Initialization
  ############################################################################################
  resultsFile = ResultsFileDefault
  resultsFile = di.FileOpenItem("Results file", default = ResultsFileDefault ).set_pos(col=0)
  selectedOutput = di.ChoiceItem("Output type", [ (0, "Figure"), (1, "Table") ], default=TypeDefault).set_pos(col=1)
  plotFile = di.StringItem("Output", default = PlotFileDefault ).set_pos(col=0)
  keepPlotScript = di.BoolItem("Keep bash script", default=KeepPlotFileDefault ).set_pos(col=1)

  aAvailableCfg = []
  for cfg in Configs:
    aAvailableCfg.append( cfg.title )

  cfgChoiceList = []
  for i in range(len(Configs)):
    cfg = Configs[i]
    defaults = []
    if cfg.showLabels == 1:
      displayList = cfg.name
    else:
      displayList = cfg.configs
    if cfg.selectAll == 1:
      defaults=[ i for i in range(len(cfg.configs)) ]
    exec("cfgChoice%d = di.MultipleChoiceItem( cfg.title, displayList, defaults ).vertical(6)" % (i) )
    exec("cfgChoiceList.append( cfgChoice%d )" % (i) )

  _bdCatG = dt.BeginGroup("Categories").set_pos(col=0)
  linesPlotCfg = di.MultipleChoiceItem( "Lines", aAvailableCfg, default=[] ).vertical().set_pos(col=0)
  pointsPlotCfg = di.MultipleChoiceItem( "Points", aAvailableCfg, default=[] ).vertical().set_pos(col=1)
  skipFilterCfg = di.MultipleChoiceItem( "Skip", aAvailableCfg, default=[] ).vertical().set_pos(col=2)
  _eCatG = dt.EndGroup("Categories")
  _bgTabG0 = dt.BeginTabGroup("Tab1").set_pos(col=1)

  _bgOut = dt.BeginGroup("Output definition")
  selectXValues = di.ChoiceItem("X values", AxisValues, default=XValueDefault)
  selectYValues = di.ChoiceItem("Y values", AxisValues, default=YValueDefault)
  _egOut = dt.EndGroup("Output definition")

  _bgFig = dt.BeginGroup("Figure definition")
  legendPosition =["Off", "Top Left", "Top Right", "Bottom Left", "Bottom Right"]
  terminalIdx = di.ChoiceItem( "Gnuplot terminal", GnuplotTerminals, default=GnuplotTerminalDefault )
  legendPositionIdx = di.ChoiceItem( "Legend Position", legendPosition, default=PlotLegendDefault )
  #_bgAx = dt.BeginGroup("Axis definition")
  plotXLim = di.StringItem("X axis Limits", default=AxisLimitDefaultX )
  plotYLim = di.StringItem("Y axis Limits", default=AxisLimitDefaultY )
  #_egAx = dt.EndGroup("Axis definition")
  showTitle = di.BoolItem("Display plot title", default=True ).set_pos(col=0)
  showBars = di.BoolItem("Generate bar plot", default=GenerateBarPlotDefault ).set_pos(col=1)
  _egFig = dt.EndGroup("Figure definition")

  _bgTab = dt.BeginGroup("Table definition")
  showAverage = di.BoolItem("Show average values", default=True )
  showExtra = di.BoolItem("Extra Result", default=False ).set_pos(col=0)
  selectExtraYValues = di.ChoiceItem("Extra values", AxisValues, default=-1).set_pos(col=0)
  _eTab = dt.EndGroup("Table definition")


  _eTabG0 = dt.EndTabGroup("Tab1")



class Templates(dt.DataSet):

  _bgM = BeginGroup("Main gnuplot code").set_pos(col=0)
  GnuPlotTemplate = di.TextItem("", GnuPlotTemplateDefault + GnuPlotTemplateExtra )
  _egM = EndGroup("Main gnuplot code")
  _bgBar = BeginGroup("Bar plot extra code").set_pos(col=1)
  GnuPlotTemplateBarPlot = di.TextItem("", GnuPlotTemplateBarPlotDefault + GnuPlotTemplateBarPlotExtra )
  _egBar = EndGroup("Bar plot extra code")
  _bgT = BeginGroup("Main latex code").set_pos(col=0)
  LatexTemplate = di.TextItem("", LatexTemplateDefault)
  _egT = EndGroup("Main latex code")



if __name__ == '__main__':

  from guidata.qt.QtGui import QApplication

  # Create QApplication
  _app = guidata.qapplication()

  config = PlotConfiguration("Plot Configutaion")
  templates = Templates("Templates")

  g = dt.DataSetGroup( [config, templates], title='Python Publication ready outputs' )
  while (1):
    if g.edit():

      generator = []
      if config.selectedOutput == 0:
        generator = PlotGenerator(config, templates)

      elif config.selectedOutput == 1:
        generator = TableGenerator(config, templates)
      else:
        continue
      generator.generateOutput()
    else:
      break;



# kate: indent-mode python; space-indent on; indent-width 2; tab-indents off; tab-width 2; replace-tabs on;

