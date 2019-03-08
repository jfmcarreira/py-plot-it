#!/usr/bin/python3

############################################################################################
# Imports
############################################################################################
import os, sys, tempfile, imp
import os.path
from operator import itemgetter, attrgetter
import signal
import numpy
import math
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

def replaceLabelChars(label):
  label = label.replace('_', '\\_')
  return label

def processLabel(label):
  if label != "":
    #label = label[:-3]
    label = replaceLabelChars( label )
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
YValueValueExtraDefault = -1

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

        self.currentLegend = processLabel(self.currentLegend)

        plotResults = self.getData( currentFileConfigChoice, currentPlotConfigChoice )

        ## check empty data -> trigger an exception
        if not plotResults:
          print("No data to plot! skipping...")
        else:
          print( plotResults )
          self.loop( file_idx, plot_idx, plotResults)

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



# kate: indent-mode python; space-indent on; indent-width 2; tab-indents off; tab-width 2; replace-tabs on;
