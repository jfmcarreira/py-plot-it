#!/usr/bin/python

import os, sys
import guidata
import csv
import tempfile
import os.path
import importlib

from guidata.qt.QtGui import QMainWindow, QSplitter
from guidata.dataset.qtwidgets import DataSetShowGroupBox, DataSetEditGroupBox
from guidata.configtools import get_icon
from guidata.qthelpers import create_action, add_actions, get_std_icon
from guidata.dataset.qtwidgets import DataSetEditLayout, DataSetShowLayout
from guidata.dataset.qtitemwidgets import DataSetWidget

import guidata.dataset.datatypes as dt
import guidata.dataset.dataitems as di

from operator import itemgetter, attrgetter



from cfgData import( ResultsFile, Configs, XValues, YValues, GnuPlotTemplate )

# Global GUI params
#global ConfigurationFile
#ConfigurationFile = "cfgData.py"
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


class RandomLoss(dt.DataSet):

  def genPlot(self):
    global filtResults

    colX = self.selectXValues - 1
    colY = self.selectYValues - 1

    aCfgChoice = []
    fileConfig       = []
    fileConfigChoice = []
    plotConfig       = []
    plotConfigChoice = []

    numberPlots = 1
    plotConditions = 0
    numberLines = 1

    for i in range( len( Configs )):
      exec("aCfgChoice.append( self.cfgChoice%d )" % (i) )

      for j in self.selectPlotCfg:
        if Configs[i].title == self.aAvailableCfg[j]:
          Configs[i].use_for_plot = 1
          plotConditions += 1

      if Configs[i].use_for_plot == 0:
        fileConfig.append( Configs[i] )
        fileConfigChoice.append( aCfgChoice[i] )
        numberPlots *= len( aCfgChoice[i] )
      else:
        plotConfig.append( Configs[i] )
        plotConfigChoice.append( aCfgChoice[i] )
        numberLines *= len( aCfgChoice[i] )

    if numberPlots == 0 or plotConditions == 0:
      return

    print( "Generation %d plots with %d lines!" % (numberPlots, numberLines) )
    print( "Using columns %d vs %d" % (colX, colY) )

    readResults( self.resultsFile )

    #filterString = ""
    #for i in range( len( Configs )):
      #filterString += " " + Configs[i].configs[aCfgChoice[i][0]]
    #print( filterString )


    catIdx = 0
    plotFileNameList = []

    ## Filter the result set for the different line curves of the current plot
    filteredResults = ResultsTable;
    plotFileName = ""
    for i in range( len( fileConfig )):
        filteredResults = filterResults( filteredResults, fileConfig[i].tab, fileConfig[i].configs[fileConfigChoice[i][catIdx]] )
        plotFileName += fileConfig[i].configs[fileConfigChoice[i][catIdx]] + "_"

    plotFileName = plotFileName[:-1]
    plotFileName = "test_plot"

    plotConfigChoiceCurrentIdx = len( plotConfig ) - 1
    plotConfigChoiceCurrent = [ int(0) for i in range( len( plotConfig ) )]

    try:

      ## Init gnuplot script
      dataFileNameList = []
      f_gnuplot_name = tempfile.NamedTemporaryFile( prefix="gnuplot_").name
      f_gnuplot = open( f_gnuplot_name, 'w' )
      f_gnuplot.write( GnuPlotTemplate )
      f_gnuplot.write( "set output '"  + plotFileName + ".eps'\n" )
      plot_cmd = "plot "


      for plot_idx in range( numberLines ):

        ## Filter results for the current line
        legend = ""
        for i in range( len( plotConfig )):
          currResults = filterResults( filteredResults, plotConfig[i].tab, plotConfig[i].configs[plotConfigChoice[i][plotConfigChoiceCurrent[i]]] )
          legend += plotConfig[i].name[plotConfigChoice[i][plotConfigChoiceCurrent[i]]] + " "

        if not currResults:
          raise NameError('There is not values plot')

        legend = legend[:-1]

        f_data_name = tempfile.NamedTemporaryFile( prefix="data_" ).name
        dataFileNameList.append( f_data_name )
        f_data = open( f_data_name, 'w' )
        currResultsSort = currResults
        #currResultsSort = sorted(currResults, key=itemgetter(colX))
        for line in currResultsSort:
          #print( [ line[colX], line[colY] ] )
          f_data.write( "%s %s \n" % ( line[colX], line[colY] ) )
        f_data.close()
        os.system( "sort -n " + f_data_name + " > " + f_data_name + "_sorted" )
        os.system( "mv " + f_data_name + "_sorted " + f_data_name )

        plot_cmd += "'" + f_data_name + "' using 1:2 title '" + legend + "' w lp ls " + str( plot_idx + 1 ) + ","


        if plotConfigChoiceCurrent[plotConfigChoiceCurrentIdx] ==  len( plotConfigChoice[plotConfigChoiceCurrentIdx] ) - 1:
          plotConfigChoiceCurrent[plotConfigChoiceCurrentIdx] = 0
          plotConfigChoiceCurrentIdx -= 1
          plotConfigChoiceCurrent[plotConfigChoiceCurrentIdx] += 1
        else:
          plotConfigChoiceCurrent[plotConfigChoiceCurrentIdx] += 1


      ## Close gnuplot script
      plot_cmd = plot_cmd[:-1]
      f_gnuplot.write( plot_cmd )
      f_gnuplot.close()
      ## Plot and convert
      os.system( "gnuplot -e \"load '" + f_gnuplot_name + "'\" ")
      if os.path.isfile( plotFileName + ".eps" ):
        os.system( "ps2pdf -dEPSCrop " + plotFileName + ".eps " + plotFileName + ".pdf" )
        os.remove( plotFileName + ".eps" )
        plotFileNameList.append( plotFileName + ".pdf" )

    except NameError as err:
      print(err)

    ## Clean up files
    os.remove( f_gnuplot_name )
    for f in dataFileNameList:
      os.remove( f )


  resultsFile = di.FileOpenItem("Summary file", default = ResultsFile )

  aAvailableCfg = []
  for cfg in Configs:
    aAvailableCfg.append( cfg.title )

  if len(Configs) > 0:
    cfg = Configs[0]
    cfgChoice0 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[0] ).vertical(2)

  if len(Configs) > 1:
    cfg = Configs[1]
    cfgChoice1 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[0] ).vertical(2)

  if len(Configs) > 2:
    cfg = Configs[2]
    cfgChoice2 = di.MultipleChoiceItem( cfg.title, cfg.configs, default=[0, 1, 2] ).vertical(2)

  selectPlotCfg = di.MultipleChoiceItem( "Plot Categories", aAvailableCfg, default=[2] ).vertical(4)

  selectXValues = di.ChoiceItem("X values", XValues).set_pos(col=0, colspan=2)
  selectYValues = di.ChoiceItem("Y values", YValues).set_pos(col=1, colspan=2)


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


  plts = RandomLoss("Decoder - Randon Loss")
  #g = dt.DataSetGroup( [plts], title='Running Tests Plots' )
  while (1):
    if plts.edit():
      plts.genPlot()
    else:
      break;




