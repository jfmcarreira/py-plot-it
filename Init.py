#!/usr/bin/python3

import os, sys
from MiscFct import *

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
DefaultLinePlotCfg = []
DefaultPointsPlotCfg = []
DefaultSkipPlotCfg = []

XValueDefault = 0
YValueDefault = 0
YValueValueExtraDefault = -1
BuildAxisValuesAuto = False
XValueDefaultLabel = ""
YValueDefaultLabel = ""

GenerateBarPlotDefault = 0
GnuplotTerminalDefault = "eps"

ConfigFileName = "cfgData.py"

############################################################################################
# Read configuration
############################################################################################
############################################################################################
# Configuration list class
############################################################################################
class ConfigurationList:
  def __init__(self):
    self.title = []
    self.configs = []
    self.details = []
    self.name = []
    self.tab = -1
    self.label = []
    self.values_tab = -1
    self.use_for_plot = 0
    self.selectAll = 0
    self.selectionArray = []
    self.sort = 0
    self.showLabels = 1
    self.numColumns = 5


if os.path.exists("cfgData.py"):
  exec(open("cfgData.py").read())
elif os.path.exists("../cfgData.py"):
  exec(open("../cfgData.py").read())
else:
  print("No cfg file!")
  exit()


############################################################################################
# Read data file
############################################################################################
ResultsTableHeader = readResultsHeader(ResultsFileDefault)
ResultsTable = readResults(ResultsFileDefault)
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
    if currConfig.tab == -1:
      currConfig.tab = findColumn( ResultsTableHeader, currConfig.label ) + 1
      assert( currConfig.tab >= 0)
    currConfig.details = resultsGetDetails( ResultsTable, currConfig.tab)
    currConfig.details = translateMappings( ConfigMapping, currConfig.details )
    if currConfig.sort == 1:
      currConfig.details.sort(key=itemgetter(0))
    for j in range( len( currConfig.details ) ):
      currConfig.configs.append( currConfig.details[j][0] )
      currConfig.name.append( currConfig.details[j][1] )
    Configs.append( currConfig )

if BuildAxisValuesAuto == True:
  AxisValues = []
  AxisValuesRaw = []
  for col in range( 1,  len( ResultsTableHeader ) + 1 ):
    label = ResultsTableHeader[col - 1]
    if not XValueDefaultLabel == "":
      if XValueDefaultLabel == label:
        XValueDefault = col
    if not YValueDefaultLabel == "":
      if YValueDefaultLabel == label:
        YValueDefault = col
    # Check if it exists in configs
    for j in range( len( Configs ) ):
      if Configs[j].tab == col:
        label = Configs[j].title
    AxisValues.append( tuple( [col, findMap( ConfigMapping, label )] ) )
    AxisValuesRaw.append( tuple( [col, label ] ) )

else:
  for i in  XValues:
    AxisValues.append( i )
  for i in YValues:
    AxisValues.append( i )
  for i in range( len( AxisValues ) ):
    if AxisValues[i][0] == '-':
      l = list( AxisValues[i] )
      l[0] = AxisValues[i-1][0] + 1
      AxisValues[i] = tuple( l )
