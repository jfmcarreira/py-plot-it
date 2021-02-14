#!/usr/bin/python3

############################################################################################
# Imports
############################################################################################
from PyQt5.QtWidgets import QApplication

from guidata.dataset.datatypes import DataSet, BeginGroup, EndGroup, BeginTabGroup, EndTabGroup, DataSetGroup
from guidata.dataset.dataitems import ChoiceItem, BoolItem, TextItem, FloatItem, StringItem, DirectoryItem, FileOpenItem, MultipleChoiceItem

from AbstractGenerator import *
from PlotGenerator import PlotGenerator
from TableGenerator import TableGenerator



class PlotConfiguration(DataSet):

  def updateOutputType(self, item, value):
    print("\nitem: ", item, "\nvalue:", value)

  def applyDefaults(self, fname):

    for i in range(len(Configs)):
      cfg = Configs[i]
      #print( self.cfgChoiceList[i][0] )
      #self.PltConfig.cfgChoice%d
      if not cfg.selectionArray == []:
        exec("self.cfgChoice%d = cfg.selectionArray" % (i) )

    XValueDefault = 0
    YValueDefault = 0
    for col in range( len( AxisValuesRaw ) ):
      label = AxisValuesRaw[col][1]
      if not XValueDefaultLabel == "":
        if XValueDefaultLabel == label:
          XValueDefault = AxisValuesRaw[col][0]
      if not YValueDefaultLabel == "":
        if YValueDefaultLabel == label:
          YValueDefault = AxisValuesRaw[col][0]


    self.linesPlotCfg = DefaultLinePlotCfg
    self.pointsPlotCfg = DefaultPointsPlotCfg
    self.skipFilterCfg = DefaultSkipPlotCfg

    self.selectXValues = XValueDefault
    self.selectYValues = YValueDefault

    self.measureBDRate = DefaultMeasureBDRate

    self.plotFile = ''.join( getFilename( fname ).split("_")[1:] )

  #def __init__(self, name):
    #dt.DataSet.__init__(self)
  ############################################################################################
  # Class Initialization
  ############################################################################################
  print("Create GUI options")
  aAvailableCfg = []
  for cfg in Configs:
    aAvailableCfg.append( cfg.title )

  cfgChoiceList = []
  for i in range(len(Configs)):
    cfg = Configs[i]
    defaults = []
    if cfg.showLabels == 1:
      displayList = cfg.name
    else:
      displayList = cfg.configs
    if not cfg.selectionArray == []:
      defaults = cfg.selectionArray
    elif cfg.selectAll == 1:
      defaults = [ i for i in range(len(cfg.configs)) ]
    exec("cfgChoice%d = MultipleChoiceItem( cfg.title, displayList, defaults ).vertical(%d)" % (i, cfg.numColumns) )
    exec("cfgChoiceList.append( cfgChoice%d )" % (i) )

  _bdCatG = BeginGroup("Categories").set_pos(col=0)
  linesPlotCfg = MultipleChoiceItem( "Lines", aAvailableCfg, default=DefaultLinePlotCfg ).vertical(2).set_pos(col=0)
  pointsPlotCfg = MultipleChoiceItem( "Points", aAvailableCfg, default=DefaultPointsPlotCfg ).vertical(2).set_pos(col=1)
  skipFilterCfg = MultipleChoiceItem( "Skip", aAvailableCfg, default=DefaultSkipPlotCfg ).vertical(2).set_pos(col=2)
  _eCatG = EndGroup("Categories")

  _bgOut = BeginGroup("Output definition").set_pos(col=1)
  plotFile = StringItem("Output", default = PlotFileDefault )
  selectedOutput = ChoiceItem("Output type", [ (0, "Figure"), (1, "Table") ], default=TypeDefault).set_pos(col=0)#.set_prop("display", callback=updateOutputType)
  keepPlotScript = BoolItem("Keep bash script", default=KeepPlotFileDefault ).set_pos(col=1)
  selectXValues = ChoiceItem("X values", AxisValues, default=XValueDefault)
  selectYValues = ChoiceItem("Y values", AxisValues, default=YValueDefault)
  measureBDRate = ChoiceItem("Bjontegaard", ["Disabled", "BD-Rate", "BD-Quality"], default=DefaultMeasureBDRate)
  #measureBDRate = di.BoolItem("Measure BD-Rate", default=False )
  _egOut = EndGroup("Output definition")


  _bgTabG0 = BeginTabGroup("Tab1").set_pos(col=2)
  _bgFig = BeginGroup("Figure options").set_prop("display", callback=updateOutputType)
  legendPosition = ["Off", "Top Left", "Top Right", "Bottom Left", "Bottom Right"]
  if PlotLegendPosition:
    for i in range( len(legendPosition) ):
          if PlotLegendPosition == legendPosition[i]:
                PlotLegendDefault = i

  terminalIdx = ChoiceItem( "Gnuplot terminal", GnuplotTerminals, default=GnuplotTerminalDefault )
  legendPositionIdx = ChoiceItem( "Legend Position", legendPosition, default=PlotLegendDefault )
  #_bgAx = BeginGroup("Axis definition")
  plotXLim = StringItem("X axis Limits", default=AxisLimitDefaultX ).set_pos(col=0)
  plotYLim = StringItem("Y axis Limits", default=AxisLimitDefaultY ).set_pos(col=1)
  #_egAx = EndGroup("Axis definition")
  showTitle = BoolItem("Display plot title", default=True ).set_pos(col=0)
  showLines = BoolItem("Use Lines and Points", default=True ).set_pos(col=0)
  showBars = BoolItem("Generate bar plot", default=GenerateBarPlotDefault ).set_pos(col=1)
  _egFig = EndGroup("Figure options")

  _bgTab = BeginGroup("Table options")
  showLinesColumnwise = BoolItem("Show lines column-wise", default=DefaultShowLinesColumnwise )
  showOnlyBD = BoolItem("Only show Bjontegaard results", default=DefaultShowOnlyBD )
  showAverage = BoolItem("Show average values", default=DefaultShowAverage )
  showExtra = BoolItem("Extra Result", default=False ).set_pos(col=0)
  selectExtraYValues = ChoiceItem("Extra values", AxisValues, default=YValueValueExtraDefault).set_pos(col=0)
  _eTab = EndGroup("Table options")
  _eTabG0 = EndTabGroup("Tab1")

class Templates(DataSet):

  _bgM = BeginGroup("Main gnuplot code").set_pos(col=0)
  GnuPlotTemplate = TextItem("", GnuPlotTemplateDefault + GnuPlotTemplateExtra )
  _egM = EndGroup("Main gnuplot code")
  _bgBar = BeginGroup("Bar plot extra code").set_pos(col=1)
  GnuPlotTemplateBarPlot = TextItem("", GnuPlotTemplateBarPlotDefault + GnuPlotTemplateBarPlotExtra )
  _egBar = EndGroup("Bar plot extra code")
  _bgT = BeginGroup("Main latex code").set_pos(col=0)
  LatexTemplate = TextItem("", LatexTemplateDefault)
  _egT = EndGroup("Main latex code")

if __name__ == '__main__':

  print("Start main")
  #Create QApplication
  _app = QApplication(sys.argv)

  config = PlotConfiguration("Plot Configutaion")
  templates = Templates("Templates")

  if flagAutoGenerate:
    config.applyDefaults( sys.argv[1]  )


  g = DataSetGroup( [config, templates], title='Python Publication ready outputs' )
  while (1):

    if not flagAutoGenerate:
      if not g.edit():
        break

    generator = []
    if config.selectedOutput == 0:
      generator = PlotGenerator(Configs, ResultsTable, config, templates)
    elif config.selectedOutput == 1:
      generator = TableGenerator(Configs, ResultsTable, config, templates)
    else:
      continue
    generator.generateOutput()
    if flagAutoGenerate:
      break


# kate: indent-mode python; space-indent on; indent-width 2; tab-indents off; tab-width 2; replace-tabs on;
