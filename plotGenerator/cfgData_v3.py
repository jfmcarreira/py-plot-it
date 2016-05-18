###################################################################################################################
# Init

ConfigVersion = 2
Configs = [ ConfigurationList() for i in range(3)]
XValues = []
YValues = []

ResultsFileDefault = "results_example_bars"
PlotFileDefault = "PlotQuality"
KeepPlotFileDefault = 1
PlotLegendDefault = 0
FilterNonExistent = 1



###################################################################################################################
# Base
Configs[0].title    = 'Base'
Configs[0].tab      = 2
Configs[0].details  = [
                        #( 'lowdelay_P_4R', 'Lowdelay P' ),
                        #( 'randomaccess', 'Random Access' ),
                        ( 'lowdelay_P_4R_SingleSlice', 'Lowdelay P Single' ),
                        #( 'randomaccess_SingleSlice', 'Random Access Single' ),
                      ]

####################################################################################################################
## Sequence

Configs[1].title    = 'Sequence'
Configs[1].tab      = 3
Configs[1].details  = [
                        ( 'seq_kendo_c3', 'Kendo', ),
                        ( 'seq_book_arrival_c6', 'Book Arrival' ),
                        ( 'seq_basketball_drill', 'Basketball Drill' ),
                        ( 'seq_race', 'Race Horses' ),
                        ( 'seq_bqsquare', 'BQSquare' ),
                        ( 'seq_park', 'Park Scene' ),
                        ( 'seq_tennis', 'Tennis' ),
                        ( 'seq_people', 'People' ),
                        ( 'seq_kimono', 'Kimono' ),
                        ( 'seq_traffic', 'Traffic' ),
                      ]

####################################################################################################################
## Condition

ConfigsCond = ConfigurationList()
ConfigsConceal = ConfigurationList()

ConfigsCond.details=[
                      ( 'NoTMVP','' ),
                      #( 'NoTMVP','Ref' ),
                      #( 'NoTMVP_IIR_Multi_Ref_Avg','MultiAvgW50' ),
                      #( 'NoTMVP_IIR_Multi_Ref_Avg_Weight','MultiAvgW75' ),
                      #( 'NoTMVP_ConcRedundant10','ConcRes10' ),
                      #( 'NoTMVP_ConcRedundant20','ConcRes20' ),
                      #( 'NoTMVP_ConcRedundantSaliency10','ConcResSaliency10' ),
                      #( 'NoTMVP_ConcRedundantSaliency20','ConcResSaliency20' ),
                      #( 'NoTMVP_ConcRedundantSaliency30','ConcResSaliency30' ),
                      #( 'NoTMVP_ConcRedundantGOPLD10','ConcResLD10' ),
                      #( 'NoTMVP_ConcRedundantGOPLD20','ConcResLD20' ),
                      #( 'NoTMVP_ConcRedundantGOPRA10','ConcResRA10' ),
                      #( 'NoTMVP_ConcRedundantGOPRA20','ConcResRA20' ),
                      #( 'NoTMVP_ConcealEncodingGOPLD10','ConcStream10' ),
                      #( 'NoTMVP_ConcealEncodingGOPLD20','ConcStream20' ),
                    ]

ConfigsConceal.details  = [
                            #( 'ConcealmentMVE','' ),
                            ( 'ConcealmentMC','MC' ),
                            ( 'ConcealmentMVE''MVE' ),
                            #( 'ConcealmentMVEEnhanced''MVE Enhanced' ),
                            #( 'ConcealmentMVEMulti','MVEMulti' ),
                            ( 'ConcealmentMVESearch','OptFlow Dual' ),
                            ( 'ConcealmentMVESearchDeepFlow','OptFlow Deep ' ),
                            ( 'ConcealmentMVESearchFarneback','OptFlow Farneback' ),
                            ( 'ConcealmentMVESearchSimpleFlow','OptFlow Simple' ),
                            ( 'ConcealmentMVEBestFrame','Opt Frame' ),
                            ( 'ConcealmentMVEBestCtu','Opt Ctu' ),
                            ( 'ConcealmentMVEBestSize32','Opt CU 32' ),
                            ( 'ConcealmentMVEBestSize16','Opt CU 16' ),
                          ]

Configs[2].title    = 'Condition'
Configs[2].tab      = 4

for i in range( len( ConfigsCond.details ) ):
  for j in range( len( ConfigsConceal.details ) ):
    currConfig = ConfigsCond.details[i][0] + "_" + ConfigsConceal.details[j][0]
    currName = ""
    if ConfigsCond.details[i][1] != "":
      currName += ConfigsCond.details[i][1]
    if currName != "":
      currName += " "
    if ConfigsConceal.details[j][1] != "":
      currName += ConfigsConceal.details[j][1]
    Configs[2].details.append( [ currConfig, currName ] )


###################################################################################################################
# Configure results columns

XValues = [(4, "Method"), (6, "Bitrate [kbps]"), (7, "Packet Loss Ratio [%]")]
#XValues = [(7, "Packet Loss Ratio [%]")]
YValues = [(8, "PSNR [dB]"), (9, "SSIM"), (10, "WPSNR"), (11, "Affected PSNR")]



###################################################################################################################
# Gnuplot template

GnuPlotTemplate = """
set terminal postscript eps enhanced font 'TimesNewRoman,16'

set grid
set size {0.75,0.75}
set title   font 'TimesNewRoman,20' offset character    0, -0.7, 0
set ylabel  font 'TimesNewRoman,18' offset character  0.9,    0, 0
set ytics   font 'TimesNewRoman,16'
set key     font 'TimesNewRoman,16'

set key spacing 1  top right width 0

#set auto x
set style data histogram
set style histogram cluster gap 1
set style fill solid border 18
set boxwidth 0.6
set xtic rotate by -45 scale 0.1

set style line 1 lc 4 lt  4 lw 3 pt 10 ps 1
set style line 2 lc 2 lt  2 lw 3 pt  3 ps 1
set style line 3 lc 3 lt  4 lw 3 pt  4 ps 1
set style line 4 lc 1 lt  1 lw 3 pt  2 ps 1
set style line 5 lc 7 lt  3 lw 3 pt  6 ps 1
set style line 6 lc 8 lt  6 lw 3 pt  8 ps 1
set style line 7 lc 2 lt  7 lw 3 pt  8 ps 1
set style line 8 lc 3 lt  8 lw 3 pt  9 ps 1
set style line 9 lc 4 lt  9 lw 3 pt 10 ps 1

set style line 100 lc 18 lw 3 pt 10 ps 1
set style line 101 lc 18 lw 3 pt 10 ps 1
set style line 102 lc 18 lw 3 pt 10 ps 1


"""

#set xlabel  font 'TimesNewRoman,18' offset character    0,  0.4, 0
#set xtics   font 'TimesNewRoman,16' offset character    0,    0, 0
