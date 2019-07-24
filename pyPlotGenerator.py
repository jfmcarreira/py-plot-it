#!/usr/bin/python3

############################################################################################
# Imports
############################################################################################
import guidata
from guidata.qt.QtGui import QApplication, QMainWindow, QSplitter
from guidata.dataset.qtwidgets import DataSetShowGroupBox, DataSetEditGroupBox
from guidata.dataset.datatypes import DataSet, BeginGroup, EndGroup, BeginTabGroup, EndTabGroup
from guidata.dataset.dataitems import ChoiceItem, FloatItem, StringItem, DirectoryItem, FileOpenItem, MultipleChoiceItem
from guidata.configtools import get_icon
from guidata.qthelpers import create_action, add_actions, get_std_icon
from guidata.dataset.qtwidgets import DataSetEditLayout, DataSetShowLayout
from guidata.dataset.qtitemwidgets import DataSetWidget
import guidata.dataset.datatypes as dt
import guidata.dataset.dataitems as di
from PyQt5.QtWidgets import QApplication, QLabel

from AbstractGenerator import *
from PlotGenerator import PlotGenerator
from TableGenerator import TableGenerator



class PlotConfiguration(dt.DataSet):

  def updateOutputType(self, item, value):
    print("\nitem: ", item, "\nvalue:", value)


  ############################################################################################
  # Class Initialization
  ############################################################################################
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
    if cfg.selectAll == 1:
      defaults=[ i for i in range(len(cfg.configs)) ]
    exec("cfgChoice%d = di.MultipleChoiceItem( cfg.title, displayList, defaults ).vertical(%d)" % (i, cfg.numColumns) )
    exec("cfgChoiceList.append( cfgChoice%d )" % (i) )

  _bdCatG = dt.BeginGroup("Categories").set_pos(col=0)
  linesPlotCfg = di.MultipleChoiceItem( "Lines", aAvailableCfg, default=[] ).vertical(2).set_pos(col=0)
  pointsPlotCfg = di.MultipleChoiceItem( "Points", aAvailableCfg, default=[] ).vertical(2).set_pos(col=1)
  skipFilterCfg = di.MultipleChoiceItem( "Skip", aAvailableCfg, default=[] ).vertical(2).set_pos(col=2)
  _eCatG = dt.EndGroup("Categories")

  _bgOut = dt.BeginGroup("Output definition").set_pos(col=1)
  plotFile = di.StringItem("Output", default = PlotFileDefault )
  selectedOutput = di.ChoiceItem("Output type", [ (0, "Figure"), (1, "Table") ], default=TypeDefault).set_pos(col=0)#.set_prop("display", callback=updateOutputType)
  keepPlotScript = di.BoolItem("Keep bash script", default=KeepPlotFileDefault ).set_pos(col=1)
  selectXValues = di.ChoiceItem("X values", AxisValues, default=XValueDefault)
  selectYValues = di.ChoiceItem("Y values", AxisValues, default=YValueDefault)
  measureBDRate = di.ChoiceItem("Bjontegaard", ["Disabled", "BD-Rate", "BD-Quality"], default=0)
  #measureBDRate = di.BoolItem("Measure BD-Rate", default=False )
  _egOut = dt.EndGroup("Output definition")


  _bgTabG0 = BeginTabGroup("Tab1").set_pos(col=2)
  _bgFig = dt.BeginGroup("Figure options").set_prop("display", callback=updateOutputType)
  legendPosition =["Off", "Top Left", "Top Right", "Bottom Left", "Bottom Right"]
  terminalIdx = di.ChoiceItem( "Gnuplot terminal", GnuplotTerminals, default=GnuplotTerminalDefault )
  legendPositionIdx = di.ChoiceItem( "Legend Position", legendPosition, default=PlotLegendDefault )
  #_bgAx = dt.BeginGroup("Axis definition")
  plotXLim = di.StringItem("X axis Limits", default=AxisLimitDefaultX ).set_pos(col=0)
  plotYLim = di.StringItem("Y axis Limits", default=AxisLimitDefaultY ).set_pos(col=1)
  #_egAx = dt.EndGroup("Axis definition")
  showTitle = di.BoolItem("Display plot title", default=True ).set_pos(col=0)
  showBars = di.BoolItem("Generate bar plot", default=GenerateBarPlotDefault ).set_pos(col=1)
  _egFig = dt.EndGroup("Figure options")

  _bgTab = BeginGroup("Table options")
  showLinesColumnwise = di.BoolItem("Show lines column-wise", default=True )
  showOnlyBD = di.BoolItem("Only show Bjontegaard results", default=False )
  showAverage = di.BoolItem("Show average values", default=True )
  showExtra = di.BoolItem("Extra Result", default=False ).set_pos(col=0)
  selectExtraYValues = di.ChoiceItem("Extra values", AxisValues, default=YValueValueExtraDefault).set_pos(col=0)
  _eTab = dt.EndGroup("Table options")
  _eTabG0 = dt.EndTabGroup("Tab1")

class Templates(dt.DataSet):

  _bgM = BeginGroup("Main gnuplot code").set_pos(col=0)
  GnuPlotTemplate = di.TextItem("", GnuPlotTemplateDefault + GnuPlotTemplateExtra )
  _egM = EndGroup("Main gnuplot code")
  _bgBar = BeginGroup("Bar plot extra code").set_pos(col=1)
  GnuPlotTemplateBarPlot = di.TextItem("", GnuPlotTemplateBarPlotDefault + GnuPlotTemplateBarPlotExtra )
  _egBar = EndGroup("Bar plot extra code")
  _bgT = BeginGroup("Main latex code").set_pos(col=0)
  LatexTemplate = di.TextItem("", LatexTemplateDefault)
  _egT = EndGroup("Main latex code")


if __name__ == '__main__':

  from guidata.qt.QtGui import QApplication
  #Create QApplication
  _app = QApplication(sys.argv)

  config = PlotConfiguration("Plot Configutaion")
  templates = Templates("Templates")

  g = dt.DataSetGroup( [config, templates], title='Python Publication ready outputs' )
  while (1):
    if g.edit():

      generator = []
      if config.selectedOutput == 0:
        generator = PlotGenerator(Configs, ResultsTable, config, templates)

      elif config.selectedOutput == 1:
        generator = TableGenerator(Configs, ResultsTable, config, templates)
      else:
        continue
      generator.generateOutput()
    else:
      break;

# kate: indent-mode python; space-indent on; indent-width 2; tab-indents off; tab-width 2; replace-tabs on;
