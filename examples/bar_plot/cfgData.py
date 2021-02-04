#!/bin/python

###################################################################################################################
# Init

ConfigVersion = 2
Configs = [ ConfigurationList() for i in range(5)]
XValues = []
YValues = []


###################################################################################################################
# Base
Configs[0].title      = 'Base'
Configs[0].tab        = 2
Configs[0].selectAll  = 1
Configs[0].showLabels = 1
Configs[0].details    = [
                        ( 'lowdelay_P_4R_slice_1200B', 'Low-Delay' ),
                        ( 'lowdelay_P_4R_slice_single', 'Low-Delay' ),
                      ]

####################################################################################################################
## Sequence

Configs[1].title      = 'Sequence'
Configs[1].tab        = 3
Configs[1].selectAll  = 1
Configs[1].showLabels = 1
Configs[1].details    = [
                        ( 'seq_basketball_drill', 'Basketball Drill' ),
                        ( 'seq_basketball_drive', 'Basketball Drive' ),
                        ( 'seq_book_arrival_c6', 'Book Arrival' ),
                        ( 'seq_bqsquare', 'BQSquare' ),
                        ( 'seq_cactus', 'Cactus' ),
                        ( 'seq_four_people', 'Four People' ),
                        ( 'seq_kimono', 'Kimono' ),
                        ( 'seq_kendo_c3', 'Kendo', ),
                        ( 'seq_kristen_sara', 'Kristen Sara' ),
                        ( 'seq_park', 'Park Scene' ),
                        ( 'seq_people', 'People' ),
                        ( 'seq_race', 'Race Horses' ),
                        ( 'seq_tennis', 'Tennis' ),
                        ( 'seq_traffic', 'Traffic' ),
                      ]

####################################################################################################################
## Condition

Configs[2].title      = 'Condition'
Configs[2].tab        = 4
Configs[2].showLabels = 1
Configs[2].selectAll  = 1
Configs[2].details  = [
                        ( 'NoTMVP_ConcealmentFC','FC' ),
                        ( 'NoTMVP_ConcealmentMC', 'MC' ),
                        ( 'NoTMVP_ConcealmentMVE', 'MVE' ),
                        ( 'NoTMVP_ConcealmentMVESearchDeepFlow', 'DeepFlow' ),
                        ( 'NoTMVP_ConcealmentMVEBestVersion2_ConcealmentBestSizeDyn13_BestLambda01', 'ECM_13' ),
                        ( 'NoTMVP_ConcMVE_ConcResGOPLD10_ConcealmentWithDiff','MVE_ConcRes10' ),
                      ]



###################################################################################################################
# QP / Rate
Configs[3].title      = 'Rate/QP'
Configs[3].tab        = 5
Configs[3].selectAll  = 1
Configs[3].details    = [
                        ( 'rate_single',  'Fixed'  ),
                        ( 'rate_single_90pc',  '-10%'  ),
                        ( 'rate_single_80pc',  '-20%'  ),
                        ( 'rate_single_70pc',  '-30%'  ),
                        ( 'rate_single_60pc',  '-40%'  ),
                        ( 'rate_single_50pc',  '-50%'  ),
                        ( 'qp_22', 'QP=22' ),
                        ( 'qp_27', 'QP=27' ),
                        ( 'qp_32', 'QP=32' ),
                        ( 'qp_37', 'QP=37' ),
                      ]

###################################################################################################################
# PLR
Configs[4].title      = 'PacketLossRatio'
Configs[4].tab        = 7
Configs[4].selectAll  = 1
Configs[4].details    = [
                        ( '0.0',  'EF'  ),
                        ( '0.5',  '0.5%'  ),
                        ( '1.0',  '1.0%'  ),
                        ( '1.2',  '1.2%'  ),
                        ( '1.6',  '1.6%'  ),
                        ( '2.0',  '2.0%'  ),
                        ( '2.2',  '2.2%'  ),
                        ( '2.4',  '2.4%'  ),
                        ( '2.6',  '2.6%'  ),
                        ( '2.8',  '2.8%'  ),
                        ( '3.0',  '3.0%'  ),
                        ( '5.0',  '5.0%'  ),
                        ( '7.0',  '7.0%'  ),
                        ( '10.0', '10.0%' ),
                        ( '20.0', '20.0%' ),
                      ]
###################################################################################################################
# Configure results columns

XValues = [(6, "Bitrate [kbps]"), (18, "Bitrate+Overhead [kbps]"), (7, "Packet Loss Ratio [%]"), (19, "Effective Packet Loss Ratio [%]"), (3, "Sequence"), (4, "ECM")]
YValues = [(8, "PSNR [dB]"), (9, "SSIM"), (10, "AFFECTED_PSNR"), (11, "WPSNR"), (20, "FSIM"), (21, "Time [ms]")]


###################################################################################################################
# Defaults

ResultsFileDefault = "summary"
FilterNonExistent = 1

PlotFileDefault = "PlotQuality"
KeepPlotFileDefault = 1
PlotLegendDefault = 1

ConfigurationSelectAll = 1
XValueDefault = 3
YValueDefault = 21

GenerateBarPlotDefault = 1

###################################################################################################################
# Gnuplot template

# EPS | PDF
GnuplotTerminalDefault = 0

GnuPlotTemplate = """
font 'TimesNewRoman,18'

set datafile missing '-'

set grid
#set size {1,1}

set title   font 'TimesNewRoman,20' center  offset character 0, -1

set xlabel center
set ylabel center offset character 1, 0

set xtics center
set ytics center

set key spacing 1 width 0

set style line 4 lc 1 lt  1 lw 3 pt  2 ps 1
set style line 2 lc 2 lt  2 lw 3 pt  3 ps 1
set style line 3 lc 3 lt  4 lw 3 pt  4 ps 1
set style line 1 lc 4 lt  4 lw 3 pt  10 ps 1
set style line 5 lc 7 lt  3 lw 3 pt  6 ps 1
set style line 6 lc 8 lt  6 lw 3 pt  8 ps 1
set style line 7 lc 2 lt  7 lw 3 pt  8 ps 1
set style line 8 lc 3 lt  8 lw 3 pt  9 ps 1
set style line 9 lc 4 lt  9 lw 3 pt  10 ps 1

set style line 100 lc 1 lw 3
set style line 101 lc 4 lw 3
set style line 102 lc 2 lw 3
set style line 103 lc 3 lw 3

set rmargin 0.3

"""

GnuPlotTemplateBarPlot = """

set style histogram clustered  gap 1.5
set grid y
set style data histograms
set style fill solid
set boxwidth 1

set xtics rotate by 30 offset 0,-1
set bmargin 5

"""


