#!/usr/bin/python

############################################################################################
# Imports
############################################################################################
import os, sys
import guidata
import tempfile
import os.path
import signal
import imp
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
with open(ConfigFileName) as f:
  code = compile(f.read(), ConfigFileName, 'exec')
  exec(code)

############################################################################################
# Default values
############################################################################################

GnuplotTerminals = ["eps", "pdf"]

if not 'ConfigVersion' in globals():
  ConfigVersion = 1

if not 'ConfigMapping' in globals():
  ConfigMapping = []

if not 'GnuPlotTemplateDefault' in globals():
  GnuPlotTemplateDefault = ""
if not 'GnuPlotTemplateBarPlotDefault' in globals():
  GnuPlotTemplateBarPlotDefault = ""

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
    # aux_variables
    self.gnuplotFile = 0

  def dumpAxisLimits(self, axis, axisLimit):
    if axisLimit:
      axisLimit = axisLimit.split(',')
      if len( axisLimit ) == 3:
        self.gnuplotFile.write( "set " + axis + "tics " + axisLimit[0] + "," + axisLimit[1] + "," + axisLimit[2] + "\n" )
        self.gnuplotFile.write( "set " + axis + "range [" + axisLimit[0] + ":" + axisLimit[2] + "]\n" )
      else:
        self.gnuplotFile.write( "set " + axis + "range [" + axisLimit[0] + ":" + axisLimit[1] + "]\n" )


  def genPlot(self, ):

    # Selected terminal
    selectedGnuplotTerminal = GnuplotTerminals[self.GnuplotConfig.terminalIdx];
    UseBarPlot = self.GnuplotConfig.showBars


    if self.PltConfig.plotFile == "":
      print( "Empty title!!" )
      return

    XLabel = []
    YLabel = []
    for i in range( len( XValues )):
      if XValues[i][0] == self.PltConfig.selectXValues:
        XLabel = XValues[i][1]
        break

    for i in range( len( YValues )):
      if YValues[i][0] == self.PltConfig.selectYValues:
        YLabel = YValues[i][1]
        break

    #
    # Init variables
    #

    # General cfg variable
    aCfgChoice       = []
    # Configs for each group of plots
    fileConfig       = []
    fileConfigChoice = []
    # Configs for each plot
    plotConfig       = []
    plotConfigChoice = []

    # Bar plot specific
    barPlotLabelsCfg = []

    numberPlots = 1
    plotConditions = 0
    numberLines = 1

    for i in range( len( Configs )):
      exec("aCfgChoice.append( self.PltConfig.cfgChoice%d )" % (i) )
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
              barPlotLabelsCfg.append( label )
          skip_filtering = 1
          break

      if not skip_filtering:
        if use_for_plot == 0:
          fileConfig.append( Configs[i] )
          fileConfigChoice.append( aCfgChoice[i] )
          numberPlots *= len( aCfgChoice[i] )
        else:
          plotConditions += 1
          plotConfig.append( Configs[i] )
          plotConfigChoice.append( aCfgChoice[i] )
          if self.PltConfig.selectXValues != Configs[i].tab and self.PltConfig.selectXValues != Configs[i].values_tab:
            numberLines *= len( aCfgChoice[i] )

    if numberPlots == 0 or plotConditions == 0:
      return

    print( "Generation %d plots with %d lines!" % (numberPlots, numberLines) )
    print( "Using columns %d vs %d" % (self.PltConfig.selectXValues - 1, self.PltConfig.selectYValues - 1) )

    if UseBarPlot:
      print(barPlotLabelsCfg)

    if not ResultsTable:
      readResults( self.PltConfig.resultsFile )


    configChoiceCurrent = [ int(0) for i in range( len( Configs ) )]
    preFilteredResults = ResultsTable
    for i in range( len( Configs )):
      configList = []
      for j in aCfgChoice[i]:
        configList.append( Configs[i].configs[j] )
      preFilteredResults = filterSeveralResults( preFilteredResults, Configs[i].tab, configList )

    catIdx = 0
    plotFileNameList = []
    plotFileName = self.PltConfig.plotFile


    ## Init gnuplot script
    plotFileNameList = []
    f_gnuplot_name = self.PltConfig.plotFile + ".plt"
    f_gnuplot = self.gnuplotFile = open( f_gnuplot_name, 'w' )

    if selectedGnuplotTerminal == "eps":
      GnuPlotTerminalConfig = "set terminal postscript eps enhanced"

    if selectedGnuplotTerminal == "pdf":
      GnuPlotTerminalConfig = "set terminal pdfcairo mono"

    GnuPlotTerminalConfig += " \\"
    f_gnuplot.write( GnuPlotTerminalConfig )

    f_gnuplot.write( self.GnuplotConfig.GnuPlotTemplate )

    if UseBarPlot == True:
      f_gnuplot.write( self.GnuplotConfig.GnuPlotTemplateBarPlot )


    if XLabel and not UseBarPlot:
      f_gnuplot.write( "set xlabel '" + XLabel + "'\n" )
    if YLabel:
      f_gnuplot.write( "set ylabel '" + YLabel + "'\n" )

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

    f_gnuplot.write( gnuplotKeyConfiguration + "\n\n" )


    self.dumpAxisLimits( "x", self.GnuplotConfig.plotXLim )
    self.dumpAxisLimits( "y", self.GnuplotConfig.plotYLim )

    fileConfigChoiceCurrent = [ int(0) for i in range( len( fileConfig ) )]

    for file_idx in range( numberPlots ):

      ## Filter the result set for the different line curves of the current plot
      filteredResults = preFilteredResults;
      plotCurrentFileName = ""
      plotCurrentTitle = ""
      for i in range( len( fileConfig )):
          filteredResults = filterResults( filteredResults, fileConfig[i].tab, fileConfig[i].configs[fileConfigChoice[i][fileConfigChoiceCurrent[i]]] )
          plotCurrentFileName += fileConfig[i].configs[fileConfigChoice[i][fileConfigChoiceCurrent[i]]] + "_"
          if fileConfig[i].name[fileConfigChoice[i][fileConfigChoiceCurrent[i]]]:
            plotCurrentTitle += fileConfig[i].name[fileConfigChoice[i][fileConfigChoiceCurrent[i]]] + " - "

      plotCurrentFileName = plotCurrentFileName[:-1]
      plotCurrentTitle = plotCurrentTitle[:-3]
      plotConfigChoiceCurrent = [ int(0) for i in range( len( plotConfig ) )]

      # Init gnuplot data point and command
      plotData = []
      plotCommand = "plot"

      firstPlot = True

      ## Loop through each plot on the current file (several lines)
      for plot_idx in range( numberLines ):

        ## Filter results for the current line
        legend = ""
        currResults = filteredResults
        applyFiltering = False
        for i in range( len( plotConfig )):
          if self.PltConfig.selectXValues == plotConfig[i].tab or self.PltConfig.selectXValues == plotConfig[i].values_tab:
            applyFiltering = True
            continue
          currResults = filterResults( currResults, plotConfig[i].tab, plotConfig[i].configs[plotConfigChoice[i][plotConfigChoiceCurrent[i]]] )
          legend += plotConfig[i].name[plotConfigChoice[i][plotConfigChoiceCurrent[i]]] + " - "

        #print("Applying filtering: " + str(applyFiltering) )

        plotResults = []
        barDataIndex = 0

        if applyFiltering:
          for i in range( len( plotConfig )):
            if self.PltConfig.selectXValues != plotConfig[i].tab and self.PltConfig.selectXValues != plotConfig[i].values_tab:
              continue
            for j in plotConfigChoice[i]:
              for line in currResults:
                if line[ plotConfig[i].tab - 1 ] == plotConfig[i].configs[j]:
                  currPlotData = [ line[self.PltConfig.selectYValues - 1] ]
                  if UseBarPlot:
                    if firstPlot == True:
                      currPlotData.append( "\"" + barPlotLabelsCfg[barDataIndex] + "\"" )
                  else:
                    currPlotData.append( line[self.PltConfig.selectXValues - 1] )
                  barDataIndex += 1
                  plotResults.append( currPlotData )
        else:
          for line in currResults:
            currPlotData = [ line[self.PltConfig.selectYValues - 1] ]
            if UseBarPlot:
              if firstPlot == True:
                currPlotData.append( "\"" + barPlotLabelsCfg[barDataIndex] + "\"" )
            else:
              currPlotData.append( line[self.PltConfig.selectXValues - 1] )
            barDataIndex += 1
            plotResults.append( currPlotData )

        if legend != "":
          legend = legend[:-3]
          legend = legend.replace('_', '\_')

        ## check empty data -> trigger an exception
        if not plotResults:
          print("No data to plot! skipping...")
          continue

        plotResultsSort = plotResults
        #currResultsSort.sort( key=lambda x: x[0])
        for line in plotResultsSort:
          plotData.append( line )
        plotData.append( ["e"] )

        if UseBarPlot:
          if firstPlot == True:
            plotCommand += " '-' using 1:xtic(2)"
          else:
            plotCommand += " '-' using 1"
          plotCommand += " ls " + str( plot_idx + 100 )
          #plotCommand += " ti col"
        else:
          plotCommand += " '-' using 2:1 w lp ls " + str( plot_idx + 1 )

        plotCommand += " title '" + legend + "',"


        ## setup variables for the next line within the same plot
        ## try to increment the last config! if not possible
        ## try to increment the previous one and so one
        for i in reversed(range( len( plotConfig ))):
          if self.PltConfig.selectXValues == plotConfig[i].tab or self.PltConfig.selectXValues == plotConfig[i].values_tab:
            continue
          if plotConfigChoiceCurrent[i] ==  len( plotConfigChoice[i] ) - 1:
            plotConfigChoiceCurrent[i] = 0
          else:
            plotConfigChoiceCurrent[i] += 1
            break

      # dump title, output, plot command and data points
      if not plotCommand == "plot":
        plotFileNameList.append( plotCurrentFileName ) # keep a list of files to convert
        if selectedGnuplotTerminal == "eps":
          plotCurrentFileName += ".eps"
        if selectedGnuplotTerminal == "pdf":
          plotCurrentFileName += ".pdf"

        f_gnuplot.write( "set output '"  + plotCurrentFileName + "'\n" )

        if self.GnuplotConfig.showTitle:
          f_gnuplot.write( "set title '" + plotCurrentTitle + "'\n" )

        f_gnuplot.write( plotCommand[:-1] + "\n" )
        for line in plotData:
          for item in line:
            f_gnuplot.write( "%s " % (item) )
          f_gnuplot.write( "\n")
        f_gnuplot.write( "\n")

      ## setup variables for the next file
      ## try to increment the last config! if not possible
      ## try to increment the previous one and so one
      for i in reversed(range( len( fileConfig ))):
        if fileConfigChoiceCurrent[i] ==  len( fileConfigChoice[i] ) - 1:
          fileConfigChoiceCurrent[i] = 0
        else:
          fileConfigChoiceCurrent[i] += 1
          break

      firstPlot = False


    # close gnuplot script and plot
    f_gnuplot.close()
    os.system( "gnuplot -e \"load '" + f_gnuplot_name + "'\" ")

    # Finally convert the set of pdf files in one pdf file with multiple pages
    if selectedGnuplotTerminal == "eps" or selectedGnuplotTerminal == "pdf":
      convert_cmd = "gs -q -sPAPERSIZE=letter -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=" + plotFileName + ".pdf"
      for f in plotFileNameList:
        if selectedGnuplotTerminal == "eps":
          os.system( "ps2pdf -dEPSCrop " + f + ".eps " + f + ".pdf" )
        convert_cmd += " " + f + ".pdf"
      os.system( convert_cmd )
      for f in plotFileNameList:
        if selectedGnuplotTerminal == "eps":
          os.remove( f + ".eps" )
        os.remove( f + ".pdf" )

    if self.PltConfig.keepPlotScript == 0:
      os.remove( f_gnuplot_name )

    print("Finished!")


class PlotConfiguration(dt.DataSet):
  ############################################################################################
  # Class Initialization
  ############################################################################################
  resultsFile = di.FileOpenItem("Results file", default = ResultsFileDefault )
  plotFile = di.StringItem("Plot file", default = PlotFileDefault ).set_pos(col=0)
  keepPlotScript = di.BoolItem("Keep plot script", default=KeepPlotFileDefault ).set_pos(col=1)

  aAvailableCfg = []
  for cfg in Configs:
    aAvailableCfg.append( cfg.title )

  #cfgChoice = []
  #for cfg in Configs:
    #if cfg.selectAll == 1:
      #currentCfgChoice = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[ i for i in range(len(cfg.configs)) ] ).vertical(3)
    #else:
      #currentCfgChoice = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[] ).vertical(3)
    #cfgChoice.append( currentCfgChoice )


  if len(Configs) > 0:
    cfg = Configs[0]
    if cfg.showLabels == 1:
      displayList = cfg.name
    else:
      displayList = cfg.configs
    if cfg.selectAll == 1:
      cfgChoice0 = di.MultipleChoiceItem( cfg.title, displayList, default=[ i for i in range(len(cfg.configs)) ] ).vertical(4)
    else:
      cfgChoice0 = di.MultipleChoiceItem( cfg.title, displayList, default=[] ).vertical(4)

  if len(Configs) > 1:
    cfg = Configs[1]
    if cfg.showLabels == 1:
      displayList = cfg.name
    else:
      displayList = cfg.configs
    if cfg.selectAll == 1:
      cfgChoice1 = di.MultipleChoiceItem( cfg.title, displayList, default=[ i for i in range(len(cfg.configs)) ] ).vertical(4)
    else:
      cfgChoice1 = di.MultipleChoiceItem( cfg.title, displayList, default=[] ).vertical(4)

  if len(Configs) > 2:
    cfg = Configs[2]
    if cfg.showLabels == 1:
      displayList = cfg.name
    else:
      displayList = cfg.configs
    if cfg.selectAll == 1:
      cfgChoice2 = di.MultipleChoiceItem( cfg.title, displayList, default=[ i for i in range(len(cfg.configs)) ] ).vertical(2)
    else:
      cfgChoice2 = di.MultipleChoiceItem( cfg.title, displayList, default=[] ).vertical(2)

  if len(Configs) > 3:
    cfg = Configs[3]
    if cfg.showLabels == 1:
      displayList = cfg.name
    else:
      displayList = cfg.configs
    if cfg.selectAll == 1:
      cfgChoice3 = di.MultipleChoiceItem( cfg.title, displayList, default=[ i for i in range(len(cfg.configs)) ] ).vertical(3).set_pos(col=0)
    else:
      cfgChoice3 = di.MultipleChoiceItem( cfg.title, displayList, default=[] ).vertical(3).set_pos(col=0)

  if len(Configs) > 4:
    cfg = Configs[4]
    if cfg.showLabels == 1:
      displayList = cfg.name
    else:
      displayList = cfg.configs
    if cfg.selectAll == 1:
      cfgChoice4 = di.MultipleChoiceItem( cfg.title, displayList, default=[ i for i in range(len(cfg.configs)) ] ).vertical(3).set_pos(col=1)
    else:
      cfgChoice4 = di.MultipleChoiceItem( cfg.title, displayList, default=[] ).vertical(3).set_pos(col=1)

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
      plts.genPlot()
    else:
      break;



# kate: indent-mode python; space-indent on; indent-width 2; tab-indents off; tab-width 2; replace-tabs on;
