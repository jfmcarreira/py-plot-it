#!/bin/python

exec(open(os.environ['HOME'] + "/IT/RunningTests/02_RunningTestsFunctions/Python/Mappins.py").read())

###################################################################################################################
# Column Configuration
ConfigVersion = 3

NumberOfColumns = 5
Configs = [ ConfigurationList() for i in range(NumberOfColumns)]

## Base
Configs[0].title      = 'Base'
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

GenerateBarPlotDefault = 0

# EPS | PDF
GnuplotTerminalDefault = 1



###################################################################################################################
# Gnuplot template

GnuPlotTemplateDefault = """
font 'TimesNewRoman,14'

set datafile missing '-'

set grid
#set size square {1,.5}

set title center  offset character 0, -.9

set xlabel center
set ylabel center offset character 1, 0


set key box spacing 1 width 0

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

set style histogram clustered  gap 1.5
set grid y
set style data histograms
set style fill solid
set boxwidth 1

set xtics rotate by 30 offset 0,-1
set bmargin 5

"""


LatexTemplateDefault = """
\\documentclass{article}
\\usepackage{adjustbox,tabularx, colortbl, ctable, array, multirow}
\\begin{document}
adasdasdas

"""

