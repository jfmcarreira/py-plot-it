#!/usr/bin/python

import os, sys
import guidata
import tempfile
import os.path
import signal
import imp
from guidata.qt.QtGui import QMainWindow, QSplitter
from guidata.dataset.qtwidgets import DataSetShowGroupBox, DataSetEditGroupBox
from guidata.configtools import get_icon
from guidata.qthelpers import create_action, add_actions, get_std_icon
from guidata.dataset.qtwidgets import DataSetEditLayout, DataSetShowLayout
from guidata.dataset.qtitemwidgets import DataSetWidget
import guidata.dataset.datatypes as dt
import guidata.dataset.dataitems as di
from operator import itemgetter, attrgetter
signal.signal(signal.SIGINT, signal.SIG_DFL)

class ConfigurationList:
  def __init__(self):
    self.title = []
    self.configs = []
    self.details = []
    self.name = []
    self.tab = 0
    self.use_for_plot = 0


#
# Define variables
ResultsTable = []
ConfigFileName = "cfgData.py"


## Configure how to read the results file
def filterResults( results, col, value):
  filtResults = []
  for line in results:
    if line[col] == value:
      filtResults.append(line)
  return filtResults

def readResults(fname):
  global ResultsTable
  ResultsTable = []
  if os.path.isfile(fname):
    for line in open(fname).readlines():
      ResultsTable.append(line.split())


## Open cfgData
with open(ConfigFileName) as f:
  code = compile(f.read(), ConfigFileName, 'exec')
  exec(code)

## Optional variables from cfg
if not 'ConfigVersion' in globals():
  ConfigVersion = 1
if not 'FilterNonExistent' in globals():
  FilterNonExistent = 0
if not 'ResultsFileDefault' in globals():
  ResultsFileDefault = ""
if not 'PlotFileDefault' in globals():
  PlotFileDefault = ""
if not 'PlotLegendDefault' in globals():
  PlotLegendDefault = 0
if not 'AxisLimitDefaultX' in globals():
  AxisLimitDefaultX = ""
if not 'AxisLimitDefaultY' in globals():
  AxisLimitDefaultY = ""


if ResultsFileDefault:
  readResults( ResultsFileDefault )
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


class PlotResults(dt.DataSet):

  def dumpAxisLimits(self, axis, axisLimit):
    if axisLimit:
      axisLimit = axisLimit.split(',')
      if len( axisLimit ) == 3:
        self.gnuplotFile.write( "set " + axis + "tics " + axisLimit[0] + "," + axisLimit[1] + "," + axisLimit[2] + "\n" )
        self.gnuplotFile.write( "set " + axis + "range [" + axisLimit[0] + ":" + axisLimit[2] + "]\n" )
      else:
        self.gnuplotFile.write( "set " + axis + "range [" + axisLimit[0] + ":" + axisLimit[1] + "]\n" )


  def genPlot(self):

    if self.plotFile == "":
      print( "Empty title!!" )
      return

    XLabel = []
    YLabel = []
    for i in range( len( XValues )):
      if XValues[i][0] == self.selectXValues:
        XLabel = XValues[i][1]
        break

    for i in range( len( YValues )):
      if YValues[i][0] == self.selectYValues:
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

    numberPlots = 1
    plotConditions = 0
    numberLines = 1

    for i in range( len( Configs )):
      exec("aCfgChoice.append( self.cfgChoice%d )" % (i) )
      use_for_plot = 0
      for j in self.selectPlotCfg:
        if Configs[i].title == self.aAvailableCfg[j]:
          use_for_plot = 1
          break

      if use_for_plot == 0:
        fileConfig.append( Configs[i] )
        fileConfigChoice.append( aCfgChoice[i] )
        numberPlots *= len( aCfgChoice[i] )
      else:
        plotConditions += 1
        plotConfig.append( Configs[i] )
        plotConfigChoice.append( aCfgChoice[i] )
        numberLines *= len( aCfgChoice[i] )

    if numberPlots == 0 or plotConditions == 0:
      return

    print( "Generation %d plots with %d lines!" % (numberPlots, numberLines) )
    print( "Using columns %d vs %d" % (self.selectXValues - 1, self.selectYValues - 1) )

    readResults( self.resultsFile )

    catIdx = 0
    plotFileNameList = []
    plotFileName = self.plotFile


    ## Init gnuplot script
    plotFileNameList = []
    f_gnuplot_name = self.plotFile + ".plt"
    f_gnuplot = self.gnuplotFile = open( f_gnuplot_name, 'w' )
    f_gnuplot.write( GnuPlotTemplate )

    if XLabel:
      f_gnuplot.write( "set xlabel '" + XLabel + "'\n" )
    if YLabel:
      f_gnuplot.write( "set ylabel '" + YLabel + "'\n" )
    if not self.legendPosition == 0:
      f_gnuplot.write( "set key " + self.legendPosition[self.legendPositionIdx].lower() + "\n\n" )
    else:
      f_gnuplot.write( "set key off \n" )

    self.dumpAxisLimits( "x", self.plotXLim )
    self.dumpAxisLimits( "y", self.plotYLim )

    fileConfigChoiceCurrent = [ int(0) for i in range( len( fileConfig ) )]

    for file_idx in range( numberPlots ):

      ## Filter the result set for the different line curves of the current plot
      filteredResults = ResultsTable;
      plotCurrentFileName = ""
      plotCurrentTitle = ""
      for i in range( len( fileConfig )):
          filteredResults = filterResults( filteredResults, fileConfig[i].tab, fileConfig[i].configs[fileConfigChoice[i][fileConfigChoiceCurrent[i]]] )
          plotCurrentFileName += fileConfig[i].configs[fileConfigChoice[i][fileConfigChoiceCurrent[i]]] + "_"
          plotCurrentTitle += fileConfig[i].name[fileConfigChoice[i][fileConfigChoiceCurrent[i]]] + " - "

      plotCurrentFileName = plotCurrentFileName[:-1]
      plotCurrentTitle = plotCurrentTitle[:-3]
      plotConfigChoiceCurrent = [ int(0) for i in range( len( plotConfig ) )]

      # Init gnuplot data point and command
      plotData = []
      plotCommand = "plot"

      ## Loop through each plot on the current file (several lines)
      for plot_idx in range( numberLines ):

        ## Filter results for the current line
        legend = ""
        currResults = filteredResults
        for i in range( len( plotConfig )):
          currResults = filterResults( currResults, plotConfig[i].tab, plotConfig[i].configs[plotConfigChoice[i][plotConfigChoiceCurrent[i]]] )
          legend += plotConfig[i].name[plotConfigChoice[i][plotConfigChoiceCurrent[i]]] + " - "

        legend = legend[:-3]

        ## check empty data -> trigger an exception
        if not currResults:
          print("No data to plot! skipping...")
          continue

        currResultsSort = currResults
        #currResultsSort.sort( key=lambda x: x[0])
        for line in currResultsSort:
          plotData.append( [ line[self.selectXValues - 1], line[self.selectYValues - 1] ] )


        #plot_cmd += "'" + f_data_name + "' using 1:2 title '" + legend + "' w lp ls " + str( plot_idx + 1 ) + ","
        plotCommand += " '-' using 1:2 title '" + legend + "' w lp ls " + str( plot_idx + 1 ) + ","

        plotData.append( ["e"] )

        ## setup variables for the next line within the same plot
        ## try to increment the last config! if not possible
        ## try to increment the previous one and so one
        for i in reversed(range( len( plotConfig ))):
          if plotConfigChoiceCurrent[i] ==  len( plotConfigChoice[i] ) - 1:
            plotConfigChoiceCurrent[i] = 0
          else:
            plotConfigChoiceCurrent[i] += 1
            break

      # dump title, output, plot command and data points
      if not plotCommand == "plot":
        plotFileNameList.append( plotCurrentFileName ) # keep a list of files to convert
        if self.showTitle:
          f_gnuplot.write( "set title '" + plotCurrentTitle + "'\n" )
        f_gnuplot.write( "set output '"  + plotCurrentFileName + ".eps'\n" )
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


    # close gnuplot script and plot
    f_gnuplot.close()
    os.system( "gnuplot -e \"load '" + f_gnuplot_name + "'\" ")

    # Finally convert the set of pdf files in one pdf file with multiple pages
    convert_cmd = "gs -q -sPAPERSIZE=letter -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=" + plotFileName + ".pdf"
    for f in plotFileNameList:
      os.system( "ps2pdf -dEPSCrop " + f + ".eps " + f + ".pdf" )
      convert_cmd += " " + f + ".pdf"
    os.system( convert_cmd )
    for f in plotFileNameList:
      os.remove( f + ".eps" )
      os.remove( f + ".pdf" )

    if self.keepPlotScript == 0:
      os.remove( f_gnuplot_name )

  #
  # Class definition
  #
  resultsFile = di.FileOpenItem("Results file", default = ResultsFileDefault )
  plotFile = di.StringItem("Plot file", default = PlotFileDefault ).set_pos(col=0)
  keepPlotScript = di.BoolItem("Keep plot script", default=0).set_pos(col=1)

  aAvailableCfg = []
  for cfg in Configs:
    aAvailableCfg.append( cfg.title )

  if len(Configs) > 0:
    cfg = Configs[0]
    cfgChoice0 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[ i for i in range(len(cfg.configs)) ] ).vertical(2)

  if len(Configs) > 1:
    cfg = Configs[1]
    cfgChoice1 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[ i for i in range(len(cfg.configs)) ] ).vertical(2)

  if len(Configs) > 2:
    cfg = Configs[2]
    cfgChoice2 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[ i for i in range(len(cfg.configs)) ] ).vertical(2)

  if len(Configs) > 3:
    cfg = Configs[3]
    cfgChoice3 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[ i for i in range(len(cfg.configs)) ] ).vertical(2)

  selectPlotCfg = di.MultipleChoiceItem( "Plot Categories", aAvailableCfg, default=[2] )

  legendPosition =["Top Left", "Top Right", "Bottom Left", "Bottom Right"]
  _bgFig = dt.BeginGroup("Figure definition").set_pos(col=0)
  legendPositionIdx = di.ChoiceItem( "Legend Position", legendPosition, default=PlotLegendDefault-1 )
  showTitle = di.BoolItem("Display plot title", default=True )
  _egFig = dt.EndGroup("Figure definition")
  _bgAx = dt.BeginGroup("Axis definition").set_pos(col=1)
  selectXValues = di.ChoiceItem("X values", XValues).set_pos(col=0)
  selectYValues = di.ChoiceItem("Y values", YValues).set_pos(col=1)
  plotXLim = di.StringItem("X axis Limits", default=AxisLimitDefaultX ).set_pos(col=0)
  plotYLim = di.StringItem("Y axis Limits", default=AxisLimitDefaultY ).set_pos(col=1)
  _egAx = dt.EndGroup("Axis definition")


  # aux_variables
  gnuplotFile = 0

#class Init(dt.DataSet):
  #resultsFile = di.FileOpenItem("Configuration File", default = ConfigurationFile)


if __name__ == '__main__':

  from guidata.qt.QtGui import QApplication


  # Create QApplication
  _app = guidata.qapplication()

  #init = Init()
  #while (not os.path.isfile( ConfigurationFile + ".py" )):
    #if not plts.edit():
      #exit()


  plts = PlotResults("Plot Results")
  #g = dt.DataSetGroup( [plts], title='Running Tests Plots' )
  while (1):
    if plts.edit():
      plts.genPlot()
    else:
      break;




