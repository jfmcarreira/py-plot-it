#!/bin/python

###################################################################################################################
# Column Configuration
ConfigVersion = 3

NumberOfColumns = 5
Configs = [ ConfigurationList() for i in range(NumberOfColumns)]

## Base
Configs[0].title      = 'Base'
Configs[0].tab        = 1
Configs[0].selectAll  = 1

## Sequence
Configs[1].title      = 'Sequence'
Configs[1].tab        = 2
Configs[1].selectAll  = 0
Configs[1].sort       = 1

## QP / Rate
Configs[2].title      = 'Rate/QP'
Configs[2].tab        = 3
Configs[2].selectAll  = 0

## Condition
Configs[3].title      = 'Condition'
Configs[3].tab        = 4
Configs[3].selectAll  = 0
Configs[3].sort       = 0

## PLR
Configs[4].title      = 'Packet Loss Ratio'
Configs[4].tab        = 5
Configs[4].selectAll  = 1
Configs[4].sort       = 0

###################################################################################################################
# Configure results columns

AxisValues = [ (5, "Packet Loss Ratio [%]"), (4, "ECM"), (6, "PSNR [dB]")]

###################################################################################################################
# Defaults

ResultsFileDefault = "summary"
FilterNonExistent = 1

PlotFileDefault = "pyPlotQuality"
KeepPlotFileDefault = 1
PlotLegendDefault = 3

ConfigurationSelectAll = 1
XValueDefault = 5
YValueDefault = 6

GenerateBarPlotDefault = 0

# EPS | PDF
GnuplotTerminalDefault = 1


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


###################################################################################################################
# Mappings
ConfigMapping = [
( 'lowdelay_P_4R_slice_single', 'Low-Delay - Single' ),
( 'randomaccess_slice_single', 'Low-Delay - Single' ),
( 'lowdelay_P_4R_slice_1200B', 'Low-Delay - 1200B' ),
( 'lowdelay_P_4R_slice_2400B', 'Low-Delay - 2400B' ),
( 'randomaccess_slice_1200B', 'Random-access - 1200B' ),
( 'randomaccess_slice_2400B', 'Random-access - 2400B' ),
( 'lowdelay_P_4R_intra_8_slice_1200B', 'Low-Delay - Intra=8 - 1200B' ),
( 'lowdelay_P_4R_intra_32_slice_1200B', 'Low-Delay - Intra=32 - 1200B' ),
( 'lowdelay_P_4R_intra_64_slice_1200B', 'Low-Delay - Intra=64 - 1200B' ),
( 'lowdelay_P_4R_intra_128_slice_1200B', 'Low-Delay - Intra=128 - 1200B' ),
( 'lowdelay_P_4R_intra_32_slice_2400B', 'Low-Delay - Intra=32 - 2400B' ),
( 'randomaccess_intra_8_slice_1200B', 'Random-access - Intra=8 - 1200B' ),
( 'randomaccess_intra_32_slice_1200B', 'Random-access - Intra=32 - 1200B' ),
( 'randomaccess_intra_64_slice_1200B', 'Random-access - Intra=64 - 1200B' ),
( 'randomaccess_intra_32_slice_2400B', 'Random-access - Intra=32 - 2400B' ),
# Sequences
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
# Rate / QP
( 'rate_single',      'Main rate'      ),
( 'rate_single_90pc', '10% Reduction'  ),
( 'rate_single_80pc', '20% Reduction'  ),
( 'rate_single_70pc', '30% Reduction'  ),
( 'rate_single_60pc', '40% Reduction '  ),
( 'rate_single_50pc', '50% Reduction'  ),
( 'qp_22', 'QP=22' ),
( 'qp_27', 'QP=27' ),
( 'qp_32', 'QP=32' ),
( 'qp_37', 'QP=37' ),
# PLR
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
# Configuration
( 'NoTMVP','REF' ),
( 'NoTMVP_ConcealmentFC','FC' ),
( 'NoTMVP_ConcealmentMC', 'MC' ),
( 'NoTMVP_ConcealmentMVE', 'MVE' ),
( 'NoTMVP_ConcealmentMVEBestVersion2_ConcealmentBestSizeDyn13_BestLambda01', 'SECM13' ),
( 'NoTMVP_ConcealmentMVEBestVersion2_ConcealmentBestSizeDynSaliency22_BestLambda01', 'SECM22' ),
( 'NoTMVP_ConcealmentMVEBestVersion2_ConcealmentBestSizeDynSplitEcmSaliency36_BestLambda01', 'SECM36' ),
( 'NoTMVP_ConcMVEResidueGOPLD10_ConcealmentWithDiff', 'EL10' ),
( 'NoTMVP_ConcMVEResidueGOPLD20_ConcealmentWithDiff', 'EL20' ),
( 'NoTMVP_mixedExp2_ConcealmentMVEEnhanced', 'EXP' ),
( 'NoTMVP_mixedExp2_ConcMVE_ConcResGOPLD10_ConcealmentWithDiff', 'EXP+EL10' ),
( 'NoTMVP_mixedExp2_ConcMVE_ConcResGOPLD20_ConcealmentWithDiff', 'EXP+EL20' ),
]
