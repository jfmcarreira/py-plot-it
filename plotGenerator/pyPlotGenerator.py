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
    self.values_tab = -1
    self.use_for_plot = 0
    self.selectAll = 0


ConfigFileName = "cfgData.py"

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
if not 'KeepPlotFileDefault' in globals():
  KeepPlotFileDefault = 0
if not 'PlotLegendDefault' in globals():
  PlotLegendDefault = 0
if not 'AxisLimitDefaultX' in globals():
  AxisLimitDefaultX = ""
if not 'AxisLimitDefaultY' in globals():
  AxisLimitDefaultY = ""



## Configure how to read the results file
def filterResults( results, col, value):
  filtResults = []
  for line in results:
    if line[col - 1] == value:
      filtResults.append(line)
  return filtResults

## Configure how to read the results file
def filterSeveralResults( results, col, values):
  filtResults = []
  for line in results:
    for v in values:
      if line[col - 1] == v:
        filtResults.append(line)
        break
  return filtResults

def readResults(fname):
  if os.path.isfile(fname):
    print("Reading results!!")
    for line in open(fname).readlines():
      ResultsTable.append(line.split())

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
      skip_filtering = 0
      for j in self.selectPlotCfg:
        if Configs[i].title == self.aAvailableCfg[j]:
          use_for_plot = 1
          break

      for j in self.skipFilteringPlotCfg:
        if Configs[i].title == self.aAvailableCfg[j]:
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
          if self.selectXValues != Configs[i].tab and self.selectXValues != Configs[i].values_tab:
            numberLines *= len( aCfgChoice[i] )

    if numberPlots == 0 or plotConditions == 0:
      return

    print( "Generation %d plots with %d lines!" % (numberPlots, numberLines) )
    print( "Using columns %d vs %d" % (self.selectXValues - 1, self.selectYValues - 1) )

    if not ResultsTable:
      readResults( self.resultsFile )


    configChoiceCurrent = [ int(0) for i in range( len( Configs ) )]
    preFilteredResults = ResultsTable
    for i in range( len( Configs )):
      configList = []
      for j in aCfgChoice[i]:
        configList.append( Configs[i].configs[j] )
      preFilteredResults = filterSeveralResults( preFilteredResults, Configs[i].tab, configList )

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
          if fileConfig[i].name[fileConfigChoice[i][fileConfigChoiceCurrent[i]]]:
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
        applyFiltering = False
        for i in range( len( plotConfig )):
          if self.selectXValues == plotConfig[i].tab or self.selectXValues == plotConfig[i].values_tab:
            applyFiltering = True
            continue
          currResults = filterResults( currResults, plotConfig[i].tab, plotConfig[i].configs[plotConfigChoice[i][plotConfigChoiceCurrent[i]]] )
          legend += plotConfig[i].name[plotConfigChoice[i][plotConfigChoiceCurrent[i]]] + " - "


        plotResults = []
        if applyFiltering:
          for i in range( len( plotConfig )):
            if self.selectXValues != plotConfig[i].tab and self.selectXValues != plotConfig[i].values_tab:
              continue
            for j in plotConfigChoice[i]:
              for line in currResults:
                if line[ plotConfig[i].tab - 1 ] == plotConfig[i].configs[j]:
                  if self.showBars:
                    plotResults.append( [ "\"" + plotConfig[i].name[j] + "\"", line[self.selectYValues - 1] ] )
                  else:
                    plotResults.append( [ line[self.selectXValues - 1], line[self.selectYValues - 1] ] )
        else:
          for line in currResults:
            plotResults.append( [ line[self.selectXValues - 1], line[self.selectYValues - 1] ] )


        if legend != "":
          legend = legend[:-3]

        ## check empty data -> trigger an exception
        if not plotResults:
          print("No data to plot! skipping...")
          continue

        plotResultsSort = plotResults
        #currResultsSort.sort( key=lambda x: x[0])
        for line in plotResultsSort:
          plotData.append( line )
        plotData.append( ["e"] )


        if self.showBars:
          plotCommand += " '-' using 2:xtic(1)  w boxes ls " + str( plot_idx + 100 + 1 ) + ","
        else:
          plotCommand += " '-' using 1:2 title '" + legend + "' w lp ls " + str( plot_idx + 1 ) + ","


        ## setup variables for the next line within the same plot
        ## try to increment the last config! if not possible
        ## try to increment the previous one and so one
        for i in reversed(range( len( plotConfig ))):
          if self.selectXValues == plotConfig[i].tab or self.selectXValues == plotConfig[i].values_tab:
            continue
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


  ############################################################################################
  # Class definition
  ############################################################################################

  resultsFile = di.FileOpenItem("Results file", default = ResultsFileDefault )
  plotFile = di.StringItem("Plot file", default = PlotFileDefault ).set_pos(col=0)
  keepPlotScript = di.BoolItem("Keep plot script", default=KeepPlotFileDefault ).set_pos(col=1)

  aAvailableCfg = []
  for cfg in Configs:
    aAvailableCfg.append( cfg.title )

  if len(Configs) > 0:
    cfg = Configs[0]
    if cfg.selectAll == 1:
      cfgChoice0 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[ i for i in range(len(cfg.configs)) ] ).vertical(3)
    else:
      cfgChoice0 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[] ).vertical(3)

  if len(Configs) > 1:
    cfg = Configs[1]
    if cfg.selectAll == 1:
      cfgChoice1 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[ i for i in range(len(cfg.configs)) ] ).vertical(3)
    else:
      cfgChoice1 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[] ).vertical(3)

  if len(Configs) > 2:
    cfg = Configs[2]
    if cfg.selectAll == 1:
      cfgChoice2 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[ i for i in range(len(cfg.configs)) ] ).vertical(3)
    else:
      cfgChoice2 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[] ).vertical(3)

  if len(Configs) > 3:
    cfg = Configs[3]
    if cfg.selectAll == 1:
      cfgChoice3 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[ i for i in range(len(cfg.configs)) ] ).vertical(3)
    else:
      cfgChoice3 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[] ).vertical(3)

  selectPlotCfg = di.MultipleChoiceItem( "Plot Categories", aAvailableCfg, default=[2] )
  skipFilteringPlotCfg = di.MultipleChoiceItem( "Skip Categories", aAvailableCfg, default=[0] )

  legendPosition =["Off", "Top Left", "Top Right", "Bottom Left", "Bottom Right"]
  _bgFig = dt.BeginGroup("Figure definition").set_pos(col=0)
  legendPositionIdx = di.ChoiceItem( "Legend Position", legendPosition, default=PlotLegendDefault )
  showTitle = di.BoolItem("Display plot title", default=True )
  showBars = di.BoolItem("Generate bar plot", default=False )
  _egFig = dt.EndGroup("Figure definition")
  _bgAx = dt.BeginGroup("Axis definition").set_pos(col=1)
  selectXValues = di.ChoiceItem("X values", XValues).set_pos(col=0)
  selectYValues = di.ChoiceItem("Y values", YValues).set_pos(col=1)
  plotXLim = di.StringItem("X axis Limits", default=AxisLimitDefaultX ).set_pos(col=0)
  plotYLim = di.StringItem("Y axis Limits", default=AxisLimitDefaultY ).set_pos(col=1)
  _egAx = dt.EndGroup("Axis definition")

  # aux_variables
  gnuplotFile = 0



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




# kate: indent-mode python; space-indent on; indent-width 2; tab-indents off; tab-width 2; replace-tabs on;
