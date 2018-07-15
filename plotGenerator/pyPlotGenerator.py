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


############################################################################################
# Read configuration
############################################################################################
ConfigFileName = "cfgData.py"
exec(open(ConfigFileName).read())

############################################################################################
# Default values
############################################################################################

GnuplotTerminals = ["eps", "pdf"]

if not 'ConfigVersion' in globals():
  ConfigVersion = 1

if not 'ConfigMapping' in globals():
  ConfigMapping = []

if not 'GnuPlotTemplateDefault' in globals():
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

if not 'GnuPlotTemplateBarPlotDefault' in globals():
  GnuPlotTemplateBarPlotDefault = """

  set style histogram clustered  gap 1.5
  set grid y
  set style data histograms
  set style fill solid
  set boxwidth 1

  set xtics rotate by 30 offset 0,-1
  set bmargin 5

  """

if not 'FilterNonExistent' in globals():
  FilterNonExistent = 0
if not 'ResultsFileDefault' in globals():
  ResultsFileDefault = ""
if not 'PlotFileDefault' in globals():
  PlotFileDefault = ""
if not 'KeepPlotFileDefault' in globals():
  KeepPlotFileDefault = 0
if not 'PlotLegendDefault' in globals():
  PlotLegendDefault = 0
if not 'AxisLimitDefaultX' in globals():
  AxisLimitDefaultX = ""
if not 'AxisLimitDefaultY' in globals():
  AxisLimitDefaultY = ""

if not 'XValueDefault' in globals():
  XValueDefault = 0
if not 'YValueDefault' in globals():
  YValueDefault = 0

if not 'GenerateBarPlotDefault' in globals():
  GenerateBarPlotDefault = 0

if not 'GnuplotTerminalDefault' in globals():
  GnuplotTerminalDefault = "eps"

g_AxisValues = [XValues, YValues]

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
# Main class
############################################################################################
class PlotGenerator:

  def __init__(self, PltConfig, GnuplotConfig):
    self.PltConfig = PltConfig
    self.GnuplotConfig = GnuplotConfig


  ###
  ### General functions
  ###
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

    if applyFiltering:
      for i in range( len( self.plotConfig )):
        if self.PltConfig.selectXValues != self.plotConfig[i].tab and self.PltConfig.selectXValues != self.plotConfig[i].values_tab:
          continue
        for j in self.plotConfigChoice[i]:
          for line in filteredResults:
            if line[ self.plotConfig[i].tab - 1 ] == self.plotConfig[i].configs[j]:
              currPlotData = [ line[self.PltConfig.selectYValues - 1] ]
              currPlotData.append( line[self.PltConfig.selectXValues - 1] )
              currPlotData.append( "\"" + self.barPlotLabelsCfg[barDataIndex] + "\"" )
              barDataIndex += 1
              plotResults.append( currPlotData )
    else:
      for line in filteredResults:
        currPlotData = [ line[self.PltConfig.selectYValues - 1] ]
        currPlotData.append( line[self.PltConfig.selectXValues - 1] )
        currPlotData.append( "\"" + self.barPlotLabelsCfg[barDataIndex] + "\"" )
        barDataIndex += 1
        plotResults.append( currPlotData )

    return plotResults


  def generateOutput(self):

    if self.PltConfig.plotFile == "":
      print( "Empty output!!" )
      return

    # General cfg variable
    self.aCfgChoice       = []
    # Configs for each group of plots
    self.fileConfig       = []
    self.fileConfigChoice = []
    # Configs for each plot
    self.plotConfig       = []
    self.plotConfigChoice = []

    # Bar plot specific
    self.barPlotLabelsCfg = []

    self.numberPlots = 1
    plotConditions = 0
    self.numberLines = 1

    for i in range( len( Configs )):
      exec("self.aCfgChoice.append( self.PltConfig.cfgChoice%d )" % (i) )
      use_for_plot = 0
      skip_filtering = 0
      for j in self.PltConfig.selectPlotCfg:
        if Configs[i].title == self.PltConfig.aAvailableCfg[j]:
          use_for_plot = 1
          break

      for j in self.PltConfig.skipFilteringPlotCfg:
        if Configs[i].title == self.PltConfig.aAvailableCfg[j]:
          if Configs[i].tab == self.PltConfig.selectXValues:
            for label in Configs[i].name:
              self.barPlotLabelsCfg.append( label )
          skip_filtering = 1
          break

      if not skip_filtering:
        if use_for_plot == 0:
          self.fileConfig.append( Configs[i] )
          self.fileConfigChoice.append( self.aCfgChoice[i] )
          self.numberPlots *= len( self.aCfgChoice[i] )
        else:
          plotConditions += 1
          self.plotConfig.append( Configs[i] )
          self.plotConfigChoice.append( self.aCfgChoice[i] )
          if self.PltConfig.selectXValues != Configs[i].tab and self.PltConfig.selectXValues != Configs[i].values_tab:
            self.numberLines *= len( self.aCfgChoice[i] )

    if self.numberPlots == 0 or plotConditions == 0:
      return

    print( "Generation %d plots with %d lines!" % (self.numberPlots, self.numberLines) )
    print( "Using columns %d vs %d" % (self.PltConfig.selectXValues - 1, self.PltConfig.selectYValues - 1) )


    if not ResultsTable:
      readResults( self.PltConfig.resultsFile )

    configChoiceCurrent = [ int(0) for i in range( len( Configs ) )]
    self.OutputResults = ResultsTable
    for i in range( len( Configs )):
      configList = []
      for j in self.aCfgChoice[i]:
        configList.append( Configs[i].configs[j] )
      self.OutputResults = filterSeveralResults( self.OutputResults, Configs[i].tab, configList )

    self.OutputScript = open( self.PltConfig.plotFile + ".bash", 'w' )
    # Write bash header
    self.OutputScript.write( "#!/bin/bash\n" )


    self.dumpPlotHeader()
    self.loopPlot()
    self.dumpPlotFooter()
    print("Finished!")


  ###
  ### Plot functions
  ###
  def dumpAxisLabels(self, axisName):
    if axisName == "x":
      axis_values = g_AxisValues[0]
    elif axisName == "y":
      axis_values = g_AxisValues[1]
    else:
      return

    Label = []
    for i in range( len( axis_values )):
      if axis_values[i][0] == self.PltConfig.selectXValues:
        Label = axis_values[i][1]
        break

    if Label and not self.GnuplotConfig.showBars:
      self.OutputScript.write( "set " + axisName + "label '" + Label + "'\n" )

  def dumpAxisLimits(self, axis, axisLimit):
    if axisLimit:
      axisLimit = axisLimit.split(',')
      if len( axisLimit ) == 3:
        self.OutputScript.write( "set " + axis + "tics " + axisLimit[0] + "," + axisLimit[1] + "," + axisLimit[2] + "\n" )
        self.OutputScript.write( "set " + axis + "range [" + axisLimit[0] + ":" + axisLimit[2] + "]\n" )
      else:
        self.OutputScript.write( "set " + axis + "range [" + axisLimit[0] + ":" + axisLimit[1] + "]\n" )

  def dumpPlotHeader(self):
    # Selected terminal
    self.selectedGnuplotTerminal = GnuplotTerminals[self.GnuplotConfig.terminalIdx];

    if self.GnuplotConfig.showBars:
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
    self.OutputScript.write( self.GnuplotConfig.GnuPlotTemplate )
    if self.GnuplotConfig.showBars == True:
      self.OutputScript.write( self.GnuplotConfig.GnuPlotTemplateBarPlot )

    self.dumpAxisLabels("x")
    self.dumpAxisLabels("y")

    # Legend configuration
    gnuplotKeyConfiguration = ""
    if not self.GnuplotConfig.legendPosition == 0:
      keyPosition = self.GnuplotConfig.legendPosition[self.GnuplotConfig.legendPositionIdx].lower();
      gnuplotKeyConfiguration += "set key " + keyPosition
      if "left" in keyPosition:
        gnuplotKeyConfiguration += " Left reverse" # swap label and markers
      else:
        gnuplotKeyConfiguration += " Right" # swap label and markers
    else:
      gnuplotKeyConfiguration += "set key off"
    self.OutputScript.write( gnuplotKeyConfiguration + "\n" )

    self.dumpAxisLimits( "x", self.GnuplotConfig.plotXLim )
    self.dumpAxisLimits( "y", self.GnuplotConfig.plotYLim )

    self.plotFileNameList = []

  def dumpPlotFooter(self):
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

    # close gnuplot bash script and plot
    self.OutputScript.close()
    os.system( "bash " + self.PltConfig.plotFile + ".bash" )

    if self.PltConfig.keepPlotScript == 0:
      os.remove( self.OutputScript_name )



  def loopPlot(self):

    # Marks which file choice are we plotting
    currentFileConfigChoice = [ int(0) for i in range( len( self.fileConfig ) )]

    # Loops through all files
    for file_idx in range( self.numberPlots ):

      ## Configure title and file name
      plotCurrentFileName = ""
      plotCurrentTitle = ""
      for i in range( len( self.fileConfig )):
        curr_idx = self.fileConfigChoice[i][currentFileConfigChoice[i]]
        plotCurrentFileName += self.fileConfig[i].configs[curr_idx] + "_"
        if self.fileConfig[i].name[curr_idx]:
          plotCurrentTitle += self.fileConfig[i].name[curr_idx] + " - "

      plotCurrentFileName = plotCurrentFileName[:-1]
      plotCurrentTitle = plotCurrentTitle[:-3]

      # Marks which line choice are we plotting
      currentPlotConfigChoice = [ int(0) for i in range( len( self.plotConfig ) )]

      # Init gnuplot data point and command
      plotData = []
      plotCommand = "plot"

      ## Loop through each plot on the current file (several lines)
      for plot_idx in range( self.numberLines ):

        ## configure legend
        legend = ""
        applyFiltering = False
        for i in range( len( self.plotConfig )):
          curr_idx = self.plotConfigChoice[i][currentPlotConfigChoice[i]]
          if self.PltConfig.selectXValues == self.plotConfig[i].tab or self.PltConfig.selectXValues == self.plotConfig[i].values_tab:
            continue
          legend += self.plotConfig[i].name[curr_idx] + " - "

        if legend != "":
          legend = legend[:-3]
          legend = legend.replace('_', '\_')

        plotResults = self.getData( currentFileConfigChoice, currentPlotConfigChoice )

        ## check empty data -> trigger an exception
        if not plotResults:
          print("No data to plot! skipping...")
          continue

        plotResultsSort = plotResults
        if not self.GnuplotConfig.showBars:
          plotResultsSort = sorted(plotResultsSort, key=lambda line: float(line[1]))
        for line in plotResultsSort:
          plotData.append( line )
        plotData.append( ["e"] )

        if self.GnuplotConfig.showBars:
          plotCommand += " '-' using 1:xtic(3) ls " + str( plot_idx + 100 )
          #plotCommand += " ti col"
        else:
          plotCommand += " '-' using 2:1 w lp ls " + str( plot_idx + 1 )
        plotCommand += " title '" + legend + "',"

        ## setup variables for the next line within the same plot
        ## try to increment the last config! if not possible
        ## try to increment the previous one and so one
        for i in reversed(range( len( self.plotConfig ))):
          if self.PltConfig.selectXValues == self.plotConfig[i].tab or self.PltConfig.selectXValues == self.plotConfig[i].values_tab:
            continue
          if currentPlotConfigChoice[i] ==  len( self.plotConfigChoice[i] ) - 1:
            currentPlotConfigChoice[i] = 0
          else:
            currentPlotConfigChoice[i] += 1
            break

      # dump title, output, plot command and data points
      if not plotCommand == "plot":
        self.plotFileNameList.append( plotCurrentFileName ) # keep a list of files to convert
        if self.selectedGnuplotTerminal == "eps":
          plotCurrentFileName += ".eps"
        if self.selectedGnuplotTerminal == "pdf":
          plotCurrentFileName += ".pdf"

        self.OutputScript.write( "set output '"  + plotCurrentFileName + "'\n" )

        if self.GnuplotConfig.showTitle:
          self.OutputScript.write( "set title '" + plotCurrentTitle + "'\n" )

        self.OutputScript.write( plotCommand[:-1] + "\n" )
        for line in plotData:
          for item in line:
            self.OutputScript.write( "%s " % (item) )
          self.OutputScript.write( "\n")
        self.OutputScript.write( "\n")

      ## setup variables for the next file
      ## try to increment the last config! if not possible
      ## try to increment the previous one and so one
      for i in reversed(range( len( self.fileConfig ))):
        if currentFileConfigChoice[i] ==  len( self.fileConfigChoice[i] ) - 1:
          currentFileConfigChoice[i] = 0
        else:
          currentFileConfigChoice[i] += 1
          break

    self.OutputScript.write( "_EOF\n" )



class PlotConfiguration(dt.DataSet):
  ############################################################################################
  # Class Initialization
  ############################################################################################
  resultsFile = di.FileOpenItem("Results file", default = ResultsFileDefault )
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
    exec("cfgChoice%d = di.MultipleChoiceItem( cfg.title, displayList, defaults ).vertical(5)" % (i) )
    exec("cfgChoiceList.append( cfgChoice%d )" % (i) )

  _bgFig = dt.BeginGroup("Plotting definition").set_pos(col=0)
  selectPlotCfg = di.MultipleChoiceItem( "Plot Categories (Define which categories define the plotting lines)", aAvailableCfg, default=[2] )
  skipFilteringPlotCfg = di.MultipleChoiceItem( "Categories not filtered (Define which category will be plotted )", aAvailableCfg, default=[] )
  _egFig = dt.EndGroup("Plotting definition")

  _bgAx = dt.BeginGroup("Axis definition").set_pos(col=1)
  selectXValues = di.ChoiceItem("X values", XValues, default=XValueDefault)
  selectYValues = di.ChoiceItem("Y values", YValues, default=YValueDefault)
  _egAx = dt.EndGroup("Axis definition")


class GnuplotTemplate(dt.DataSet):

  _bgFig = dt.BeginGroup("Figure definition").set_pos(col=0)
  legendPosition =["Off", "Top Left", "Top Right", "Bottom Left", "Bottom Right"]
  terminalIdx = di.ChoiceItem( "Gnuplot terminal", GnuplotTerminals, default=GnuplotTerminalDefault )
  legendPositionIdx = di.ChoiceItem( "Legend Position", legendPosition, default=PlotLegendDefault )
  showTitle = di.BoolItem("Display plot title", default=True ).set_pos(col=0)
  showBars = di.BoolItem("Generate bar plot", default=GenerateBarPlotDefault ).set_pos(col=1)
  _egFig = dt.EndGroup("Figure definition")

  _bgAx = dt.BeginGroup("Axis definition").set_pos(col=1)
  plotXLim = di.StringItem("X axis Limits", default=AxisLimitDefaultX )
  plotYLim = di.StringItem("Y axis Limits", default=AxisLimitDefaultY )
  _egAx = dt.EndGroup("Axis definition")

  _bgM = BeginGroup("Main gnuplot code").set_pos(col=0)
  GnuPlotTemplate = di.TextItem("", GnuPlotTemplateDefault)
  _egM = EndGroup("Main gnuplot code")
  _bgBar = BeginGroup("Bar plot extra code").set_pos(col=1)
  GnuPlotTemplateBarPlot = di.TextItem("", GnuPlotTemplateBarPlotDefault)
  _egBar = EndGroup("Bar plot extra code")


if __name__ == '__main__':

  from guidata.qt.QtGui import QApplication

  # Create QApplication
  _app = guidata.qapplication()

  config = PlotConfiguration("Plot Configutaion")
  templates = GnuplotTemplate("GnuplotTemplate")
  plts = PlotGenerator(config, templates)

  g = dt.DataSetGroup( [config, templates], title='Python Gnuplot Generator' )
  while (1):
    if g.edit():
      plts.generateOutput()
    else:
      break;



# kate: indent-mode python; space-indent on; indent-width 2; tab-indents off; tab-width 2; replace-tabs on;
