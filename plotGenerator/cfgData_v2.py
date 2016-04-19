

###################################################################################################################
# Init

ConfigVersion = 2
Configs = [ ConfigurationList() for i in range(3)]
XValues = []
YValues = []


###################################################################################################################
# Optional variables
ResultsFileDefault = "results_example"
PlotFileDefault = "PlotFile"
#PlotLegendDefault = 4
FilterNonExistent = 1

###################################################################################################################
# Base
Configs[0].title    = 'Base'
Configs[0].tab      = 1
Configs[0].details  = [
                        ( 'lowdelay_P_4R', 'Lowdelay P' ),
                        ( 'randomaccess', 'Random Access' ),
                        ( 'lowdelay_P_4R_SingleSlice', 'Lowdelay P Single' ),
                        ( 'randomaccess_SingleSlice', 'Random Access Single' ),
                      ]

####################################################################################################################
## Sequence

Configs[1].title    = 'Sequence'
Configs[1].tab      = 2
Configs[1].details  = [
                        ( 'seq_kendo_c3', 'Kendo', ),
                        ( 'seq_book_arrival_c6', 'Book Arrival' ),
                        ( 'seq_basketball_drill', 'Basketball Drill' ),
                        ( 'seq_race', 'Race Horses' ),
                        ( 'seq_bqsquare', 'BQSquare' ),
                        ( 'seq_park', 'Park Scene' ),
                        ( 'seq_tennis', 'Tennis' ),
                        ( 'seq_kimono', 'Kimono' ),
                        ( 'seq_people', 'People' ),
                        ( 'seq_traffic', 'Traffic' ),
                      ]

####################################################################################################################
## Condition

ConfigsCond = ConfigurationList()
ConfigsConceal = ConfigurationList()

ConfigsCond.details=[
                      ( 'NoTMVP','Ref' ),
                      ( 'NoTMVP_IIR_Multi_Ref_Avg','MultiAvgW50' ),
                      ( 'NoTMVP_IIR_Multi_Ref_Avg_Weight','MultiAvgW75' ),
                      ( 'NoTMVP_ConcRedundantGOPLD10','ConcResidue10' ),
                      ( 'NoTMVP_ConcRedundantGOPLD20','ConcResidue20' ),
                      ( 'NoTMVP_ConcealEncodingGOPLD10','ConcStream10' ),
                      ( 'NoTMVP_ConcealEncodingGOPLD20','ConcStream20' ),
                    ]

Configs[2].title    = 'Condition'
Configs[2].tab      = 3
for i in range( len( ConfigsCond.details ) ):
    Configs[2].details.append( ConfigsCond.details[i]  )


###################################################################################################################
# Configure results columns

XValues = [(6, "Bitrate [kbps]"), (7, "Packet Loss Ratio [%]") ]
YValues = [(7, "PSNR [dB]") ]

#AxisLimitDefaultX = "0, 5, 100"
#AxisLimitDefaultY = "30, 1, 42"

###################################################################################################################
# Gnuplot template

GnuPlotTemplate = """
set terminal postscript eps enhanced font 'TimesNewRoman,16'

set grid
set size {0.75,0.75}
set title   font 'TimesNewRoman,20' offset character    0, -0.7, 0
set xlabel  font 'TimesNewRoman,18' offset character    0,  0.4, 0
set xtics   font 'TimesNewRoman,16' offset character    0,    0, 0
set ylabel  font 'TimesNewRoman,18' offset character  0.9,    0, 0
set ytics   font 'TimesNewRoman,16'
set key     font 'TimesNewRoman,16'
set key spacing 1  top right width 4

set style line 4 lc 1 lt  1 lw 3 pt  2 ps 1
set style line 2 lc 2 lt  2 lw 3 pt  3 ps 1
set style line 3 lc 3 lt  4 lw 3 pt  4 ps 1
set style line 1 lc 4 lt  4 lw 3 pt  10 ps 1
set style line 5 lc 7 lt  3 lw 3 pt  6 ps 1
set style line 6 lc 8 lt  6 lw 3 pt  8 ps 1
set style line 7 lc 2 lt  7 lw 3 pt  8 ps 1
set style line 8 lc 3 lt  8 lw 3 pt  9 ps 1
set style line 9 lc 4 lt  9 lw 3 pt  10 ps 1

"""
