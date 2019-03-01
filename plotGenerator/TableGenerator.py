#!/usr/bin/python3

from AbstractGenerator import *

def processLatexText(label):
  label = label.replace( "\\\\", "\\\\\\\\")
  label = label.replace( "%", "\%")
  return label

def formatTableNumber(value):
  value = float(value)
  return str("%.2f" % ( value ) )

class TableGenerator(AbstractGenerator):
  def __init__(self, PltConfig, Template):
    AbstractGenerator.__init__(self, PltConfig)
    self.Template = Template

  # BJONTEGAARD    Bjontegaard metric calculation34
  def measureBdRatefct(self, reference, processed):
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
    R1 = [float(x[1]) for x in reference]
    Q1 = [float(x[0]) for x in reference]
    R2 = [float(x[1]) for x in processed]
    Q2 = [float(x[0]) for x in processed]

    print(R1)
    print(Q1)
    print(R2)
    print(Q2)

    log_R1 = map(math.log, R1)
    log_R2 = map(math.log, R2)

    log_R1 = numpy.log(R1)
    log_R2 = numpy.log(R2)

    print(log_R1)
    print(log_R2)

    # Best cubic poly fit for graph represented by log_ratex, psrn_x.
    poly1 = numpy.polyfit(Q1, log_R1, 3)
    poly2 = numpy.polyfit(Q2, log_R2, 3)

    # Integration interval.
    min_int = max([min(Q1), min(Q2)])
    max_int = min([max(Q1), max(Q2)])

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

    return avg_diff

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
        TitleHeader += self.fileConfig[i].title + " / "

    if not TitleHeader == "":
      LatexHeader += "l"
      TableHeader += replaceLabelChars( TitleHeader ) + " & "
      self.showTitle = True
    elif self.PltConfig.showAverage:
      LatexHeader += "l"
      TableHeader += " & "

    LegendHeader = ""
    for cfg in self.plotConfig:
      LegendHeader += cfg.title + " / "

    if not LegendHeader == "":
      LatexHeader += "l"
      TableHeader += replaceLabelChars( LegendHeader ) + " & "


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
      self.currentLegend = processLabel(self.currentLegend)

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
      self.OutputScript.write( replaceLabelChars( TableLine ) )

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
    self.OutputScript.write( "mv texput.pdf " + self.PltConfig.plotFile + ".pdf\n")
    self.OutputScript.write( "rm texput.aux texput.log \n" )


  def loop( self, file_idx, plot_idx, last, plotResults):

    if plot_idx == 0:
      self.avergeIndex = 0

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
        TableLine += formatTableNumber( result[prY] )
        if self.PltConfig.showExtra:
          TableLine += " (" + formatTableNumber( result[prYextra] ) + ")"
        #TableLine += " & "
        if self.PltConfig.showAverage:
          self.avergeArray[self.avergeIndex] = ( self.avergeArray[self.avergeIndex] * self.avergeArrayCount[self.avergeIndex] + float(result[prY]) ) / (self.avergeArrayCount[self.avergeIndex] + 1)
          if self.PltConfig.showExtra:
            self.avergeExtraArray[self.avergeIndex] = ( self.avergeExtraArray[self.avergeIndex] * self.avergeArrayCount[self.avergeIndex] + float(result[prYextra]) ) / (self.avergeArrayCount[self.avergeIndex] + 1)
          self.avergeArrayCount[self.avergeIndex] += 1

        if self.PltConfig.measureBDRate:
          resultsArray.append( [ result[prY], result[prYextra] ] )

      self.avergeIndex += 1
      TableLine += " & "

    if plot_idx == 0:
      self.bdReference = resultsArray

    if self.PltConfig.measureBDRate:
      bdrate = self.measureBdRatefct(self.bdReference, resultsArray )
      TableLine += formatTableNumber( bdrate ) + " & "

    TableLine = TableLine[:-3]
    TableLine += "\\\\ \n"

    if last:
      TableLine += "\midrule \n"

    self.OutputScript.write( processLatexText( TableLine ) )


# kate: indent-mode python; space-indent on; indent-width 2; tab-indents off; tab-width 2; replace-tabs on;