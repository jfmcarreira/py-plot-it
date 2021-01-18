#!/bin/python

exec(open(os.environ['HOME'] + "/IT/RunningTests/02_RunningTestsFunctions/Python/Mappins.py").read())

###################################################################################################################
# Column Configuration
ConfigVersion = 3

NumberOfColumns = 5
Configs = [ ConfigurationList() for i in range(NumberOfColumns)]

## Base
Configs[0].title      = 'Base'
# Configs[ci].label      = 'BASE' # tab or label
Configs[0].tab        = 2
Configs[0].selectAll  = 1

## Sequence
Configs[1].title      = 'Sequence'
Configs[1].tab        = 3
Configs[1].selectAll  = 0
Configs[1].sort       = 1

## Condition
Configs[2].title      = 'Condition'
Configs[2].tab        = 4
Configs[2].selectAll  = 0
Configs[2].sort       = 0

## QP / Rate
Configs[3].title      = 'Rate/QP'
Configs[3].tab        = 5
Configs[3].selectAll  = 0

## PLR
Configs[4].title      = 'PacketLossRatio'
Configs[4].tab        = 7
Configs[4].selectAll  = 1
Configs[4].sort       = 0

###################################################################################################################
# Configure results columns

XValues = [(6, "Bitrate [kbps]"), (18, "Bitrate+Overhead [kbps]"), (7, "Packet Loss Ratio [%]"), (19, "Effective Packet Loss Ratio [%]"), (3, "Sequence"), (4, "ECM")]
YValues = [(8, "PSNR [dB]"), (9, "SSIM"), (10, "AFFECTED_PSNR"), (11, "WPSNR"), (20, "FSIM"), (21, "Time [ms]")]

###################################################################################################################
# Defaults

ResultsFileDefault = "summary_decoding"
FilterNonExistent = 1


PlotFileDefault = "pyPlotQuality"
KeepPlotFileDefault = 1
PlotLegendDefault = 3

ConfigurationSelectAll = 1
XValueDefault = 7
YValueDefault = 8
BuildAxisValuesAuto = 0

GenerateBarPlotDefault = 0

# EPS | PDF
GnuplotTerminalDefault = 1

# Table
DefaultShowAverage = True
DefaultShowLinesColumnwise = False
DefaultShowOnlyBD = True
TypeDefault = 0

###################################################################################################################
# Template

GnuPlotTemplateExtra = """
# Extra template
"""

GnuPlotTemplateBarPlotExtra = """
# Extra template for bar graph
"""


LatexTemplateDefault = """
% Extra latex argurment before begin document
"""
