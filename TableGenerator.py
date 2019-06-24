#!/usr/bin/python3

from AbstractGenerator import *

def processLatexText(label):
  label = label.replace( "\\\\", "\\\\\\\\")
  label = label.replace( "%", "\%")
  return label


def formatTableNumber(value):
  return formatNumber( value )


class TableGenerator(AbstractGenerator):
  def __init__(self, Configs, Results, PltConfig, Template):
    AbstractGenerator.__init__(self, Configs, Results, PltConfig)
    self.Template = Template

  def header(self):
    self.OutputScript.write( "pdflatex -halt-on-error << _EOF\n" )
    LatexHeader = """\documentclass{article}
\\usepackage{adjustbox,tabularx, colortbl, ctable, array, multirow}
"""
    self.OutputScript.write( LatexHeader )
    self.OutputScript.write( self.Template.LatexTemplate )

    LatexHeader = "\\usepackage[active,tightpage]{preview} \n\PreviewEnvironment{tabular} \n\\begin{document} \n\pagestyle{empty} \n\\begin{table}[!t] \n\\begin{tabular}"

    # get test data for headers
    plotResults = self.getData( [ int(0) for i in range( len( self.fileConfig ) )], [ int(0) for i in range( len( self.plotConfig ) )] )

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

    LegendHeader = ""
    for cfg in self.plotConfig:
      LegendHeader += cfg.title + " - "

    if not LegendHeader == "":
      LatexHeader += "l"
      TableHeader += replaceLabelChars( LegendHeader[:-3] ) + " & "


    #print( "Generation %d plots with %d lines and %d points!" % (self.numberPlots, self.numberLines, self.numberPoints) )

    self.TableHeaderLabels = []
    for i in range ( self.numberPoints ):
      LatexHeader += "c"
      TableHeader += plotResults[i][prLabel][1:-1] + " & "
      self.TableHeaderLabels.append( plotResults[i][prLabel] )

    if self.PltConfig.measureBDRate:
      LatexHeader += "c"
      TableHeader += "BD-RATE & "

    TableHeader = TableHeader[:-3]
    LatexHeader += "}"
    TableHeader += "\\\\ \n\midrule"

    self.OutputScript.write( LatexHeader + "\n" + processLatexText( TableHeader ) + "\n" )

    if self.PltConfig.showAverage:
      self.avergeArray = [ float(0) for i in range( self.numberPoints * self.numberLines )]
      self.avergeArrayCount = [ float(0) for i in range( self.numberPoints * self.numberLines )]
    self.avergeIndex = 0

    if self.PltConfig.showExtra:
      self.avergeExtraArray = [ float(0) for i in range( self.numberPoints * self.numberLines )]

  def printAverage(self):

    self.OutputScript.write( "\multirow{" + str( self.numberLines ) + "}{*}{\\textbf{Average}}\n" )

    self.avergeIndex = 0
    ## Loop through each plot on the current file (several lines)
    currentPlotConfigChoice = [ int(0) for i in range( len( self.plotConfig ) )] # Marks which line choice are we plotting
    for plot_idx in range( self.numberLines ):

      TableLine = "& "

      ## configure legend
      self.currentLegend = ""
      for i in range( len( self.plotConfig )):
        curr_idx = self.plotConfigChoice[i][currentPlotConfigChoice[i]]
        self.currentLegend += self.plotConfig[i].name[curr_idx] + " - "
      self.currentLegend = processLabel(self.currentLegend[:-3])

      if not self.currentLegend == "":
        TableLine += self.currentLegend + " & "

      for i in range ( self.numberPoints ):
        TableLine += formatTableNumber( self.avergeArray[self.avergeIndex] )
        if self.PltConfig.showExtra:
          TableLine += " (" + formatTableNumber( self.avergeExtraArray[self.avergeIndex] ) + ")"
        TableLine += " & "
        self.avergeIndex += 1

      TableLine = TableLine[:-3]
      TableLine += "\\\\ \n"
      self.OutputScript.write( processLatexText( TableLine ) )

      ## LOOP
      for i in reversed(range( len( self.plotConfig ))):
        if currentPlotConfigChoice[i] ==  len( self.plotConfigChoice[i] ) - 1:
          currentPlotConfigChoice[i] = 0
        else:
          currentPlotConfigChoice[i] += 1
          break



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

    PrintLine = True
    TableLine = ""

    if plot_idx == 0 and self.showTitle:
      TableLine = "\multirow{" + str( self.numberLines ) + "}{*}{" + replaceLabelChars(self.currentTitle) + "}" + " & "
    elif self.PltConfig.showAverage or self.showTitle:
      TableLine += " & "

    if not self.currentLegend == "":
      TableLine += self.currentLegend + " & "

    resultsArray =  []
    for i in range ( self.numberPoints ):
      result = []

      for j in range ( len( plotResults ) ):
        if plotResults[j][prLabel] == self.TableHeaderLabels[i]:
          result = plotResults[i]
          break

      if not result == []:
        PrintLine = True
        TableLine += formatTableNumber( float(result[prY]) )
        if self.PltConfig.showExtra:
          TableLine += " (" + formatTableNumber( float(result[prYextra]) ) + ")"
        #TableLine += " & "
        if self.PltConfig.showAverage:
          self.avergeArray[self.avergeIndex] = ( self.avergeArray[self.avergeIndex] * self.avergeArrayCount[self.avergeIndex] + float(result[prY]) ) / (self.avergeArrayCount[self.avergeIndex] + 1)
          if self.PltConfig.showExtra:
            self.avergeExtraArray[self.avergeIndex] = ( self.avergeExtraArray[self.avergeIndex] * self.avergeArrayCount[self.avergeIndex] + float(result[prYextra]) ) / (self.avergeArrayCount[self.avergeIndex] + 1)
          self.avergeArrayCount[self.avergeIndex] += 1

      self.avergeIndex += 1
      TableLine += " & "

    if self.PltConfig.measureBDRate:
      TableLine += formatTableNumber( extraResults[prrBD] ) + " & "

    TableLine = TableLine[:-3]
    TableLine += " \\\\ \n"
    if PrintLine:
      self.OutputScript.write( processLatexText( TableLine ) )

  def last(self):
    TableLine = "\midrule \n"
    self.OutputScript.write( processLatexText( TableLine ) )


# kate: indent-mode python; space-indent on; indent-width 2; tab-indents off; tab-width 2; replace-tabs on;
