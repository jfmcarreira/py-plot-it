#!/usr/bin/python3

from AbstractGenerator import *

class PlotGenerator(AbstractGenerator):
  def __init__(self, Configs, Results, PltConfig, Template):
    AbstractGenerator.__init__(self, Configs, Results, PltConfig)
    self.Template = Template

  ###
  ### Plot functions
  ###
  def dumpAxisLabels(self, axisName):
    if axisName == "x":
      selectedAxis = self.PltConfig.selectXValues
    elif axisName == "y":
      selectedAxis = self.PltConfig.selectYValues
    else:
      return

    Label = []
    for i in range( len( AxisValues )):
      if AxisValues[i][0] == selectedAxis:
        Label = AxisValues[i][1]
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
    self.keyPosition = 0
    if not self.PltConfig.legendPosition == 0:
      keyPosition = self.PltConfig.legendPosition[self.PltConfig.legendPositionIdx].lower();
      gnuplotKeyConfiguration += "set key " + keyPosition
      if "left" in keyPosition:
        gnuplotKeyConfiguration += " Left reverse" # swap label and markers
        self.keyPosition = 0
      else:
        gnuplotKeyConfiguration += " Right" # swap label and markers
        self.keyPosition = 1
    else:
      gnuplotKeyConfiguration += "set key off"
    self.OutputScript.write( gnuplotKeyConfiguration + "\n" )

    self.dumpAxisLimits( "x", self.PltConfig.plotXLim )
    self.dumpAxisLimits( "y", self.PltConfig.plotYLim )

    self.plotFileNameList = []
    self.plotCommand = ""

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

  def loop(self, file_idx, plot_idx, plotResults, extraResults):

    if plot_idx == 0:
      self.plotData = []
      self.plotCommand = "plot"

    if not plotResults:
      return

    extraLegendInfo = ""
    if self.PltConfig.measureBDRate:
      extraLegendInfo = formatNumber( extraResults[prrBD] )
    extraLegendInfo += " | "
    extraLegendInfo = extraLegendInfo[:-3]

    if not extraLegendInfo == "":
      if self.keyPosition == 0:
        self.currentLegend = "(" + extraLegendInfo + ") " + self.currentLegend
      else:
        self.currentLegend = self.currentLegend + " (" + extraLegendInfo + ")"

    if not self.PltConfig.showBars:
      plotResults = sorted(plotResults, key=lambda line: float(line[1]))
    # Init gnuplot data point and command

    for line in plotResults:
      self.plotData.append( line )
    self.plotData.append( ["e"] )

    if self.PltConfig.showBars:
      self.plotCommand += " '-' using " + str(prY+1) + ":xtic(" + str(prLabel+1) + ") ls " + str( plot_idx + 100 )
      #self.plotCommand += " ti col"
    else:
      self.plotCommand += " '-' using " + str(prX+1) + ":" + str(prY+1) + " w lp ls " + str( plot_idx + 1 )
    self.plotCommand += " title '" + self.currentLegend + "',"

    #if last:
      #self.plotFileNameList.append( self.currentFileName ) # keep a list of files to convert
      #if self.selectedGnuplotTerminal == "eps":
        #self.currentFileName += ".eps"
      #elif self.selectedGnuplotTerminal == "pdf":
        #self.currentFileName += ".pdf"

      #self.OutputScript.write( "set output '"  + self.currentFileName + "'\n" )

      #if self.PltConfig.showTitle:
        #self.OutputScript.write( "set title '" + processLabel( self.currentTitle ) + "'\n" )
      #else:
        #self.OutputScript.write( "unset title'\n" )

      #self.OutputScript.write( self.plotCommand[:-1] + "\n" )
      #for line in self.plotData:
        #for item in line:
          #self.OutputScript.write( "%s " % (item) )
        #self.OutputScript.write( "\n")
      #self.OutputScript.write( "\n")

  def last(self):
    self.plotFileNameList.append( self.currentFileName ) # keep a list of files to convert
    if self.selectedGnuplotTerminal == "eps":
      self.currentFileName += ".eps"
    elif self.selectedGnuplotTerminal == "pdf":
      self.currentFileName += ".pdf"

    self.OutputScript.write( "set output '"  + self.currentFileName + "'\n" )

    if self.PltConfig.showTitle:
      self.OutputScript.write( "set title '" + processLabel( self.currentTitle ) + "'\n" )
    else:
      self.OutputScript.write( "unset title'\n" )

    if not self.plotCommand == "plot":
      self.OutputScript.write( self.plotCommand[:-1] + "\n" )
      for line in self.plotData:
        for item in line:
          self.OutputScript.write( "%s " % (item) )
        self.OutputScript.write( "\n")
      self.OutputScript.write( "\n")

# kate: indent-mode python; space-indent on; indent-width 2; tab-indents off; tab-width 2; replace-tabs on;
