#!/usr/bin/python3

from AbstractGenerator import *

def processLatexText(label):
  label = label.replace( "\\\\", "\\\\\\\\")
  label = label.replace( "%", "\%")
  return label


def formatTableNumber(value):
  try:
    fmt = formatNumber( value )
  except:
    print("Cannot format %s" % value )
    exit(1)
  return fmt


class TableGenerator(AbstractGenerator):
  def __init__(self, Configs, Results, PltConfig, Template):
    AbstractGenerator.__init__(self, Configs, Results, PltConfig)
    self.Template = Template
    self.useMultiRow = False
    
  def header(self):

    if self.PltConfig.measureBDRate == 0:
      self.PltConfig.showOnlyBD = False

    self.OutputScript.write( "pdflatex -halt-on-error << _EOF\n" )
    LatexHeader = """\documentclass{article}
\\usepackage{adjustbox,tabularx, colortbl, ctable, array, multirow}
"""
    self.OutputScript.write( LatexHeader )
    self.OutputScript.write( self.Template.LatexTemplate )

    LatexHeader = "\\usepackage[active,tightpage]{preview} \n\PreviewEnvironment{tabular} \n\\begin{document} \n\pagestyle{empty} \n\\begin{table}[!t] \n\\begin{tabular}"

    # get test data for headers
    plotResults = self.getData( [ int(0) for i in range( len( self.fileConfig ) )], [ int(0) for i in range( len( self.plotConfig ) )] )
    self.TableHeaderLabels = []
    for i in range ( self.numberPoints ):
      self.TableHeaderLabels.append( plotResults[i][prLabel] )

    TableHeader = "\\toprule \n"

    LatexHeader += "{"

    self.showTitle = False
    TitleHeader = ""
    for i in range( len( self.fileConfig ) ):
      if len( self.fileConfigChoice[i] ) > 1:
        TitleHeader += self.fileConfig[i].title + " - "

    if not TitleHeader == "":
      LatexHeader += "l"
      TableHeader += replaceLabelChars( TitleHeader[:-3] ) + " & "
      self.showTitle = True
    elif self.PltConfig.showAverage:
      LatexHeader += "l"
      TableHeader += " & "

    if self.PltConfig.showLinesColumnwise:

      # Code based on the main abstract loop
      currentPlotConfigChoice = [ int(0) for i in range( len( self.plotConfig ) )]
      for plot_idx in range( self.numberLines ):
        currentLegend = ""
        for i in range( len( self.plotConfig )):
          curr_idx = self.plotConfigChoice[i][currentPlotConfigChoice[i]]
          currentLegend += self.plotConfig[i].name[curr_idx] + " - "

        if not self.PltConfig.showOnlyBD:
          for i in range ( self.numberPoints ):
            LatexHeader += "c"
            if not currentLegend == "":
              TableHeader += processLabel(currentLegend[:-3]) + " - "
            TableHeader += processLabel(plotResults[i][prLabel][1:-1]) + " & "

        if self.PltConfig.measureBDRate > 0:
          LatexHeader += "c"
          if not currentLegend == "":
              TableHeader += processLabel(currentLegend[:-3]) + " - "
          if self.PltConfig.measureBDRate == 1:
            TableHeader += "BD-Rate & "
          else:
            TableHeader += "BD-Quality & "

        for i in reversed(range( len( self.plotConfig ))):
          if currentPlotConfigChoice[i] ==  len( self.plotConfigChoice[i] ) - 1:
            currentPlotConfigChoice[i] = 0
          else:
            currentPlotConfigChoice[i] += 1
            break

    else:
      LegendHeader = ""
      for cfg in self.plotConfig:
        LegendHeader += cfg.title + " - "

      if not LegendHeader == "":
        LatexHeader += "l"
        TableHeader += replaceLabelChars( LegendHeader[:-3] ) + " & "

      if not self.PltConfig.showOnlyBD:
        for i in range ( self.numberPoints ):
          LatexHeader += "c"
          TableHeader += plotResults[i][prLabel][1:-1] + " & "

      if self.PltConfig.measureBDRate > 0:
        LatexHeader += "c"
        if self.PltConfig.measureBDRate == 1:
          TableHeader += "BD-Rate & "
        else:
          TableHeader += "BD-Quality & "

    TableHeader = TableHeader[:-3]
    LatexHeader += "}"
    TableHeader += "\\\\ \n\midrule"

    self.OutputScript.write( LatexHeader + "\n" + processLatexText( TableHeader ) + "\n" )
    self.tableLine = ""

    numAveragePoints = 0;
    if not self.PltConfig.showOnlyBD:
      numAveragePoints += self.numberPoints * self.numberLines
      if self.PltConfig.showExtra:
        numAveragePoints *= 2
    if self.PltConfig.measureBDRate > 0:
      numAveragePoints += self.numberLines
    self.avergeArray = [ float(0) for i in range( numAveragePoints )]
    self.avergeArrayCount = [ float(0) for i in range( numAveragePoints )]
    self.avergeIndex = 0


  def printAverage(self):

    if self.PltConfig.showLinesColumnwise:
      TableLine = "\\textbf{Average}"
    else:
      TableLine = "\multirow{" + str( self.numberLines ) + "}{*}{\\textbf{Average}}\n"

    self.avergeIndex = 0
    ## Loop through each plot on the current file (several lines)
    currentPlotConfigChoice = [ int(0) for i in range( len( self.plotConfig ) )] # Marks which line choice are we plotting
    for plot_idx in range( self.numberLines ):

      TableLine += "& "

      ## configure legend
      if not self.PltConfig.showLinesColumnwise:
        self.currentLegend = ""
        for i in range( len( self.plotConfig )):
          curr_idx = self.plotConfigChoice[i][currentPlotConfigChoice[i]]
          self.currentLegend += self.plotConfig[i].name[curr_idx] + " - "
        self.currentLegend = processLabel(self.currentLegend[:-3])
        if not self.currentLegend == "":
          TableLine += self.currentLegend + " & "

      for i in range ( self.numberPoints ):
        if not self.PltConfig.showOnlyBD:
          TableLine += formatTableNumber( self.avergeArray[self.avergeIndex] )
          self.avergeIndex += 1
          if self.PltConfig.showExtra:
            TableLine += " (" + formatTableNumber( self.avergeExtraArray[self.avergeIndex] ) + ")"
            self.avergeIndex += 1
          TableLine += " & "

      if self.PltConfig.measureBDRate > 0:
        if plot_idx > 0:
          TableLine += formatTableNumber( self.avergeArray[self.avergeIndex] ) + " & "
        else:
          TableLine += "-- & "
        self.avergeIndex += 1

      TableLine = TableLine[:-3]
      if not self.PltConfig.showLinesColumnwise:
        TableLine += "\\\\ \n"

      ## LOOP
      for i in reversed(range( len( self.plotConfig ))):
        if currentPlotConfigChoice[i] ==  len( self.plotConfigChoice[i] ) - 1:
          currentPlotConfigChoice[i] = 0
        else:
          currentPlotConfigChoice[i] += 1
          break

    if self.PltConfig.showLinesColumnwise:
      TableLine += "\\\\ \n"
    self.OutputScript.write( processLatexText( TableLine ) )

  def footer(self):

    if self.PltConfig.showAverage:
      self.printAverage()

    TableFooter = "\\bottomrule\n\end{tabular}\n\end{table}\n\end{document}"
    self.OutputScript.write( TableFooter )
    self.OutputScript.write( "\n_EOF\n" )
    self.OutputScript.write( "mv texput.pdf ${SCRIPT_NAME%%.*}.pdf\n")
    self.OutputScript.write( "rm texput.aux texput.log \n" )


  def loop( self, file_idx, plot_idx, plotResults, extraResults):

    if plot_idx == 0:
      self.avergeIndex = 0

    PrintLine = False

    if plot_idx == 0 and self.showTitle:
      if self.PltConfig.showLinesColumnwise:
        self.tableLine = replaceLabelChars(self.currentTitle) + " & "
      else:
        if self.useMultiRow:
          self.tableLine = "\multirow{" + str( self.numberLines ) + "}{*}{" + replaceLabelChars(self.currentTitle) + "}" + " & "
        else:
          self.tableLine = replaceLabelChars(self.currentTitle) + " & "
    elif self.PltConfig.showAverage or self.showTitle:
      self.tableLine += " & "

    if not self.PltConfig.showLinesColumnwise and not self.currentLegend == "":
      self.tableLine += self.currentLegend + " & "

    resultsArray =  []
    for i in range ( self.numberPoints ):
      result = []

      for j in range ( len( plotResults ) ):
        if plotResults[j][prLabel] == self.TableHeaderLabels[i]:
          result = plotResults[i]
          break

      if not result == []:
        PrintLine = True

      if not result == [] and not self.PltConfig.showOnlyBD:
        self.tableLine += formatTableNumber( float(result[prY]) )
        if self.PltConfig.showExtra:
          self.tableLine += " (" + formatTableNumber( float(result[prYextra]) ) + ")"
        if self.PltConfig.showAverage:
          self.avergeArray[self.avergeIndex] = ( self.avergeArray[self.avergeIndex] * self.avergeArrayCount[self.avergeIndex] + float(result[prY]) ) / (self.avergeArrayCount[self.avergeIndex] + 1)
          self.avergeArrayCount[self.avergeIndex] += 1
          self.avergeIndex += 1
          if self.PltConfig.showExtra:
            self.avergeExtraArray[self.avergeIndex] = ( self.avergeExtraArray[self.avergeIndex] * self.avergeArrayCount[self.avergeIndex] + float(result[prYextra]) ) / (self.avergeArrayCount[self.avergeIndex] + 1)
            self.avergeArrayCount[self.avergeIndex] += 1
            self.avergeIndex += 1

        self.tableLine += " & "

    if self.PltConfig.measureBDRate > 0:
      if self.PltConfig.showOnlyBD and extraResults[prrBD] == "NaN":
         PrintLine = False
      self.tableLine += formatTableNumber( extraResults[prrBD] ) + " & "
      if self.PltConfig.showAverage:
        if plot_idx > 0:
          self.avergeArray[self.avergeIndex] = ( self.avergeArray[self.avergeIndex] * self.avergeArrayCount[self.avergeIndex] + float(extraResults[prrBD]) ) / (self.avergeArrayCount[self.avergeIndex] + 1)
        self.avergeArrayCount[self.avergeIndex] += 1
        self.avergeIndex += 1

    self.tableLine = self.tableLine[:-3]
    if not self.PltConfig.showLinesColumnwise:
      self.tableLine += " \\\\ \n"
      if PrintLine:
        self.OutputScript.write( processLatexText( self.tableLine ) )
      self.tableLine = ""


  def last(self):
    if self.PltConfig.showLinesColumnwise:
      self.tableLine += " \\\\ \n"
    self.tableLine += "\midrule \n"
    self.OutputScript.write( processLatexText( self.tableLine ) )


# kate: indent-mode python; space-indent on; indent-width 2; tab-indents off; tab-width 2; replace-tabs on;
