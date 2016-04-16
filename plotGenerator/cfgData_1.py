###################################################################################################################
# Init

class ConfigurationList:
  def __init__(self):
    self.title = []
    self.configs = []
    self.name = []
    self.tab = 0
    self.use_for_plot = 0

Configs = [ ConfigurationList() for i in range(3)]
XValues = []
YValues = []

ResultsFile = "results_example_1"
PlotFile = "Plot"

###################################################################################################################
# Base
Configs[0].title    = 'Base'
Configs[0].tab      = 1
Configs[0].configs  = [ 'lowdelay_P_4R', 'randomaccess',  'randomaccess_SingleSlice', 'lowdelay_P_4R_SingleSlice']
Configs[0].name     = [ 'Lowdelay P',    'Random Access', 'Random Access Single',     'Lowdelay P Single', ]


###################################################################################################################
# Sequence

Configs[1].title    = 'Sequence'
Configs[1].tab      = 2
Configs[1].configs  = [ 'seq_kendo_c3',
                    'seq_book_arrival_c6',
                    'seq_basketball_drill',
                    'seq_race',
                    'seq_bqsquare',
                    'seq_park',
                    'seq_tennis',
                    'seq_kimono',
                    'seq_people',
                    'seq_traffic'
                  ]
Configs[1].name     = [ 'Kendo',
                    'Book Arrival',
                    'Basketball Drill',
                    'Race Horses',
                    'BQSquare',
                    'Park Scene',
                    'Tennis',
                    'Kimono',
                    'People',
                    'Traffic'
                  ]

###################################################################################################################
# Condition

ConfigsCond = ConfigurationList()
ConfigsConceal = ConfigurationList()

ConfigsCond.configs = [ 'NoTMVP',
                        'NoTMVP_IIR_Multi_Ref_Avg',
                        'NoTMVP_IIR_Multi_Ref_Avg_Weight',
                        'NoTMVP_ConcRedundantGOPLD10',
                        'NoTMVP_ConcRedundantGOPLD20',
                        'NoTMVP_ConcealEncodingGOPLD10',
                        'NoTMVP_ConcealEncodingGOPLD20',
                      ]
ConfigsCond.name    = [ 'Ref',
                        'MultiAvgW50',
                        'MultiAvgW75',
                        'ConcResidue10',
                        'ConcResidue20',
                        'ConcStream10',
                        'ConcStream20',
                      ]

#ConfigsConceal.configs  = [ 'ConcealmentMC', 'ConcealmentMVE' ]
#ConfigsConceal.name     = [ 'MC',            'MVE' ]

ConfigsConceal.configs  = [ 'ConcealmentMVE' ]
ConfigsConceal.name     = [ 'MVE' ]


Configs[2].title    = 'Condition'
Configs[2].tab      = 3
for i in range( len( ConfigsCond.configs ) ):
  for j in range( len( ConfigsConceal.configs ) ):
    Configs[2].configs.append( ConfigsCond.configs[i] + "_" + ConfigsConceal.configs[j] )
    Configs[2].name.append( ConfigsCond.name[i] + " " + ConfigsConceal.name[j] )


###################################################################################################################
# Configure results columns

XValues = [(6, "Bitrate [kbps]"), (7, "Packet Loss Ratio [%]") ]
YValues = [(8, "PSNR [dB]"), (9, "SSIM")]



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

set key spacing 1  top right width 0

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
