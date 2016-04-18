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

ConfigFileName = "cfgData.py"


## Read configuration file and retrieve required variables
f = open(ConfigFileName)
cfgData = imp.load_source('data', '', f)
f.close()
Configs = cfgData.Configs
XValues = cfgData.XValues
YValues = cfgData.YValues
GnuPlotTemplate = cfgData.GnuPlotTemplate


## Optional variables from cfg
if hasattr(cfgData, 'ResultsFileDefault'):
  ResultsFileDefault = cfgData.ResultsFileDefault
else:
  ResultsFileDefault = ""

if hasattr(cfgData, 'PlotFileDefault'):
  PlotFileDefault = cfgData.PlotFileDefault
else:
  PlotFileDefault = ""

if hasattr(cfgData, 'PlotLegendDefault'):
  PlotLegendDefault = cfgData.PlotLegendDefault
else:
  PlotLegendDefault = 0


ResultsTable = []


def filterResults( results, col, value):
  filtResults = []
  for line in results:
    if line[col] == value:
      filtResults.append(line)
  return filtResults


def readResults(fname):
  global ResultsTable
  ResultsTable = []
  for line in open(fname).readlines():
    ResultsTable.append(line.split())


class PlotResults(dt.DataSet):

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

      try:

        ## Init gnuplot script
        dataFileNameList = []
        f_gnuplot_name = tempfile.NamedTemporaryFile( prefix="gnuplot_").name
        f_gnuplot = open( f_gnuplot_name, 'w' )
        f_gnuplot.write( GnuPlotTemplate )

        if XLabel:
          f_gnuplot.write( "set xlabel '" + XLabel + "'\n" )
        if YLabel:
          f_gnuplot.write( "set ylabel '" + YLabel + "'\n" )
        if self.legendPosition:
          f_gnuplot.write( "set key " + self.legendPosition[self.legendPositionIdx].lower() + "\n" )

        if self.showTitle:
          f_gnuplot.write( "set title '" + plotCurrentTitle + "'\n" )

        f_gnuplot.write( "set output '"  + plotCurrentFileName + ".eps'\n" )
        plot_cmd = "plot "

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
            raise NameError('There is not values plot')

          f_data_name = tempfile.NamedTemporaryFile( prefix="data_" ).name
          dataFileNameList.append( f_data_name )
          f_data = open( f_data_name, 'w' )
          currResultsSort = currResults
          for line in currResultsSort:
            f_data.write( "%s %s \n" % ( line[self.selectXValues - 1], line[self.selectYValues - 1] ) )
          f_data.close()

          # Please replace the next two line with sort within python
          os.system( "sort -n " + f_data_name + " > " + f_data_name + "_sorted" )
          os.system( "mv " + f_data_name + "_sorted " + f_data_name )

          plot_cmd += "'" + f_data_name + "' using 1:2 title '" + legend + "' w lp ls " + str( plot_idx + 1 ) + ","


          ## setup variables for the next line within the same plot
          ## try to increment the last config! if not possible
          ## try to increment the previous one and so one
          for i in reversed(range( len( plotConfig ))):
            if plotConfigChoiceCurrent[i] ==  len( plotConfigChoice[i] ) - 1:
              plotConfigChoiceCurrent[i] = 0
            else:
              plotConfigChoiceCurrent[i] += 1
              break

        ## Close gnuplot script and run system cmd
        plot_cmd = plot_cmd[:-1]
        f_gnuplot.write( plot_cmd )
        f_gnuplot.close()
        ## Plot and convert
        os.system( "gnuplot -e \"load '" + f_gnuplot_name + "'\" ")
        if os.path.isfile( plotCurrentFileName + ".eps" ):
          os.system( "ps2pdf -dEPSCrop " + plotCurrentFileName + ".eps " + plotCurrentFileName + ".pdf" )
          os.remove( plotCurrentFileName + ".eps" )
          plotFileNameList.append( plotCurrentFileName + ".pdf" )


      ## If an exception is trigger clean up the files and carry on
      except NameError as err:
        print(err)

      ## Clean up files
      os.remove( f_gnuplot_name )
      for f in dataFileNameList:
        os.remove( f )

      ## setup variables for the next file
      for i in reversed(range( len( fileConfig ))):
        if fileConfigChoiceCurrent[i] ==  len( fileConfigChoice[i] ) - 1:
          fileConfigChoiceCurrent[i] = 0
        else:
          fileConfigChoiceCurrent[i] += 1
          break


    ## Finally convert the set of pdf files in one pdf file with multiple pages
    convert_cmd = "gs -q -sPAPERSIZE=letter -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=" + plotFileName + ".pdf"
    for f in plotFileNameList:
      convert_cmd += " " + f
    os.system( convert_cmd )
    for f in plotFileNameList:
      os.remove( f )

  #
  # Class definition
  #
  resultsFile = di.FileOpenItem("Results file", default = ResultsFileDefault )
  plotFile = di.StringItem("Plot file", default = PlotFileDefault )

  aAvailableCfg = []
  for cfg in Configs:
    aAvailableCfg.append( cfg.title )

  if len(Configs) > 0:
    cfg = Configs[0]
    cfgChoice0 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[0] ).vertical(2)

  if len(Configs) > 1:
    cfg = Configs[1]
    cfgChoice1 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[0, 1] ).vertical(2)

  if len(Configs) > 2:
    cfg = Configs[2]
    cfgChoice2 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[0, 2] ).vertical(2)

  if len(Configs) > 3:
    cfg = Configs[3]
    cfgChoice3 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[] ).vertical(2)

  selectPlotCfg = di.MultipleChoiceItem( "Plot Categories", aAvailableCfg, default=[1, 2] )

  legendPosition =["Top Left", "Top Right", "Bottom Left", "Bottom Right"]
  _bgFig = dt.BeginGroup("Figure definition").set_pos(col=0, colspan=3)
  legendPositionIdx = di.ChoiceItem( "Legend Position", legendPosition, default=PlotLegendDefault-1 )
  showTitle = di.BoolItem("Display plot title")
  _egFig = dt.EndGroup("Figure definition")

  _bgAx = dt.BeginGroup("Axis definition").set_pos(col=3, colspan=3)
  selectXValues = di.ChoiceItem("X values", XValues)
  selectYValues = di.ChoiceItem("Y values", YValues)
  _egAx = dt.EndGroup("Axis definition")


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




