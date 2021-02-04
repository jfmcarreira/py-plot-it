#!/usr/bin/python3

############################################################################################
# Imports
############################################################################################
import os, tempfile
from operator import itemgetter, attrgetter
import signal
import numpy
import math
import operator
signal.signal(signal.SIGINT, signal.SIG_DFL)

from MiscFct import *

# This returns several defaults variables
from Init import *

## Plot results definition
prLabel   = 0
prX       = 1
prY       = 2
prYextra  = 3

prrBD     = 0


############################################################################################
# Main classes
############################################################################################
class AbstractGenerator:

  def __init__(self, Configs, Results, PltConfig):
    self.PltConfig = PltConfig
    self.OutputResults = Results
    self.Configs = Configs

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

      if not barLabel == "":
        barLabel = barLabel[:-3]

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

    if self.OutputResults == []:
      self.OutputResults = readResults( self.PltConfig.resultsFile )

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

    for i in range( len( self.Configs )):
      #exec("print( type( self.PltConfig.cfgChoice%d ) )" % (i) )
      exec("self.aCfgChoice.append( self.PltConfig.cfgChoice%d )" % (i) )
      #print( type( self.aCfgChoice[i] ) )
      use_for_plot = False
      use_for_points = False
      skip_config = False
      for j in self.PltConfig.linesPlotCfg:
        if self.Configs[i].title == self.PltConfig.aAvailableCfg[j]:
          use_for_plot = True
          break

      for j in self.PltConfig.pointsPlotCfg:
        if self.Configs[i].title == self.PltConfig.aAvailableCfg[j]:
          use_for_points = True
          break

      for j in self.PltConfig.skipFilterCfg:
        if self.Configs[i].title == self.PltConfig.aAvailableCfg[j]:
          skip_config = True
          break

      if not skip_config:
        if not use_for_points:
          if use_for_plot == 0:
            self.fileConfig.append( self.Configs[i] )
            self.fileConfigChoice.append( self.aCfgChoice[i] )
            self.numberPlots *= len( self.aCfgChoice[i] )
          else:
            #plotConditions += 1
            self.plotConfig.append( self.Configs[i] )
            self.plotConfigChoice.append( self.aCfgChoice[i] )
            self.numberLines *= len( self.aCfgChoice[i] )
          configList = []
          for j in self.aCfgChoice[i]:
            configList.append( self.Configs[i].configs[j] )
          self.OutputResults = filterSeveralResults( self.OutputResults, self.Configs[i].tab, configList )
        else:
          for label in self.Configs[i].name:
            self.barPlotLabelsCfg.append( label )
          self.pointConfig.append( self.Configs[i] )
          self.pointConfigChoice.append( self.aCfgChoice[i] )
          self.numberPoints *= len( self.aCfgChoice[i] )


    if self.numberPlots == 0 or plotConditions == 0:
      return

    print( "Generation %d plots with %d lines and %d points!" % (self.numberPlots, self.numberLines, self.numberPoints) )
    print( "Using columns %d vs %d" % (self.PltConfig.selectXValues - 1, self.PltConfig.selectYValues - 1) )


    self.OutputScript = open( self.PltConfig.plotFile + ".bash", 'w' )
    # Write bash header
    self.OutputScript.write( "#!/bin/bash\nSCRIPT_NAME=$(basename \"$0\")\n" )

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

      print( self.currentTitle )

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

        self.currentLegend = processLabel(self.currentLegend[:-3])

        plotResults = self.getData( currentFileConfigChoice, currentPlotConfigChoice )
        extraResults = []
        ## check empty data -> trigger an exception
        if not plotResults:
          print("No data to plot! skipping...")
        else:
          print( plotResults )

        if plot_idx == 0:
          self.bdReference = plotResults

        Bjontegaard = "NaN"
        if self.PltConfig.measureBDRate > 0:
          if plot_idx == 0:
            Bjontegaard = "--"
          else:
            if not plotResults == []:
              Bjontegaard = self.measureBjontegaard(self.bdReference, plotResults, self.PltConfig.measureBDRate)
        extraResults.append(Bjontegaard)

        self.loop( file_idx, plot_idx, plotResults, extraResults)

        if last:
          self.last()

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

  # BJONTEGAARD    Bjontegaard metric calculation
  def measureBjontegaard(self, reference, processed, metric):
    """
    BJONTEGAARD    Bjontegaard metric calculation
    Bjontegaard's metric allows to compute the average % saving in bitrate
    between two rate-distortion curves [1].
    R1,Q1 - RD points for curve 1
    R2,Q2 - RD points for curve 2
    adapted from code from: (c) 2010 Giuseppe Valenzise
    """
    # numpy plays games with its exported functions.
    # pylint: disable=no-member
    # pylint: disable=too-many-locals
    # pylint: disable=bad-builtin
    R1 = [float(x[prX]) for x in reference]
    Q1 = [float(x[prY]) for x in reference]
    R2 = [float(x[prX]) for x in processed]
    Q2 = [float(x[prY]) for x in processed]

    if len(R1) < 4 or len(R2) < 4 or len(Q1) < 4 or len(Q2) < 4:
      return "NaN"

    log_R1 = map(math.log, R1)
    log_R2 = map(math.log, R2)

    log_R1 = numpy.log(R1)
    log_R2 = numpy.log(R2)

    if metric == 1:

      # Best cubic poly fit for graph represented by log_ratex, psrn_x.
      poly1 = numpy.polyfit(Q1, log_R1, 3)
      poly2 = numpy.polyfit(Q2, log_R2, 3)

      # Integration interval.
      min_int = max([min(Q1), min(Q2)])
      max_int = min([max(Q1), max(Q2)])
      if max_int < min_int:
        return 0.0;

      # find integral
      p_int1 = numpy.polyint(poly1)
      p_int2 = numpy.polyint(poly2)

      # Calculate the integrated value over the interval we care about.
      int1 = numpy.polyval(p_int1, max_int) - numpy.polyval(p_int1, min_int)
      int2 = numpy.polyval(p_int2, max_int) - numpy.polyval(p_int2, min_int)

      # Calculate the average improvement.
      avg_exp_diff = (int2 - int1) / (max_int - min_int)

      # In really bad formed data the exponent can grow too large.
      # clamp it.
      if avg_exp_diff > 200:
        avg_exp_diff = 200

      # Convert to a percentage.
      avg_diff = (math.exp(avg_exp_diff) - 1) * 100

    elif metric == 2:
      poly1 = numpy.polyfit(log_R1, Q1, 3)
      poly2 = numpy.polyfit(log_R2, Q2, 3)

      min_int = max([min(log_R1), min(log_R2)])
      max_int = min([max(log_R1), max(log_R2)])

      if max_int < min_int:
        return 0.0;

      p_int1 = numpy.polyint(poly1)
      p_int2 = numpy.polyint(poly2)

      int1 = numpy.polyval(p_int1, max_int) - numpy.polyval(p_int1, min_int)
      int2 = numpy.polyval(p_int2, max_int) - numpy.polyval(p_int2, min_int)

      avg_diff = (int2 - int1) / (max_int - min_int)

    else:
      avg_diff = 0.0

    return avg_diff


# kate: indent-mode python; space-indent on; indent-width 2; tab-indents off; tab-width 2; replace-tabs on;
