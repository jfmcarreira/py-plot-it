#!/bin/python

mappings_loaded = False
mappings_file = "/nfs/home/jcarreira.it/RnD//RunningTests/02_RunningTestsFunctions/Python/Mappins_1001.py"

if not mappings_loaded and os.path.isfile( mappings_file ):
  exec(open( mappings_file ).read())
  mappings_loaded = True

mappings_file = os.environ['HOME'] + "/RnD/RunningTests/02_RunningTestsFunctions/Python/Mappins_1001.py"
if not mappings_loaded and os.path.isfile( mappings_file ):
  exec(open( mappings_file ).read())
  mappings_loaded = True

mappings_file = os.environ['HOME'] + "/Nextcloud/Research/RunningTests/RunningTestsFunctions/Python/Mappins_1001.py"
if not mappings_loaded and os.path.isfile( mappings_file ):
  exec(open( mappings_file ).read())
  mappings_loaded = True



####################################################################################################################
## Column Configuration
#ConfigVersion = 3

#NumberOfColumns = 6
#Configs = [ ConfigurationList() for i in range(NumberOfColumns)]
#ci = -1;

### Base
#ci = ci + 1
#Configs[ci].title      = 'Script+Version'
#Configs[ci].label      = 'SCRIPT'
#Configs[ci].selectAll  = 1

### Base
#ci = ci + 1
#Configs[ci].title      = 'Base'
#Configs[ci].label      = 'BASE'
#Configs[ci].selectAll  = 1

### Projection
#ci = ci + 1
#Configs[ci].title      = 'Projection'
#Configs[ci].label      = 'PROJECTION'
#Configs[ci].selectAll  = 1

### Sequence
#ci = ci + 1
#Configs[ci].title      = 'Sequence'
#Configs[ci].label      = 'SEQUENCE'
#Configs[ci].selectAll  = 1
#Configs[ci].sort       = 1

### Condition
#ci = ci + 1
#Configs[ci].title      = 'Condition'
#Configs[ci].label      = 'CONDITION'
#Configs[ci].selectAll  = 1
#Configs[ci].sort       = 0
#Configs[ci].numColumns = 3

### QP / Rate
#ci = ci + 1
#Configs[ci].title      = 'Rate/QP'
#Configs[ci].label      = 'RATE_QP'
#Configs[ci].selectAll  = 1

## PLR
#ci = ci + 1
#Configs[ci].title      = 'PacketLossRatio'
#Configs[ci].tab        = 7
#Configs[ci].selectAll  = 1
#Configs[ci].sort       = 0

###################################################################################################################
# Configure results columns

#AxisValues = [
  #(7, "Number of Frames"),
  #('-', "Bitrate [kbps]"),
  #('-', "Bitstream size [MB]"),
  #('-', "PSNR-YUV [dB]"),
  #('-', "PSNR-Y [dB]"),
  #('-', "WS-PSNR-Y [dB]"),
  #('-', "Bitstream size (-20%) [MB]"),
  #('-', "PSNR-Y (-20%) [dB]"),
  #('-', "WS-PSNR-Y (-20%) [dB]"),
  #]

###################################################################################################################
# Defaults

ResultsFileDefault = "summary_enconding"
FilterNonExistent = 1


## Mappings
ConfigMappingAppend = [
( 'BYTES_RANDOM_ACCESS_FOV_SAL_AVG','Avg. Bytes Required Random-Access' ),
( 'EncoderVVC360_VTM-73-360Lib-10','VVC-7.3' ),
( 'EncoderVVC360_VTM-73-360Lib-10-MCTSSliceLevel','VVC-7.3+MCTS-Slice' ),
( 'EncoderVVC360_VTM-91-360Lib-101','VVC-9.1' ),
##
( 'ExtConv_Ref','Reference' ),
( 'ExtConv_Tiles_2x2Ctus_1S_Const','FixedTiles+2x2Ctus' ),
( 'ExtConv_Tiles_3x3Ctus_1S_Const','FixedTiles+3x3Ctus' ),
( 'ExtConv_Tiles_4x4Ctus_1S_Const','FixedTiles+4x4Ctus' ),
( 'ExtConv_Tiles_5x5Ctus_1S_Const','FixedTiles+5x5Ctus' ),
( 'ExtConv_Tiles_8x8Ctus_1S_Const','FixedTiles+8x8Ctus' ),
( 'ExtConv_Tiles_3x3Ctus_1S','Tiles3x3+NoMCTS' ),
( 'ExtConv_Tiles_3x3Ctus_1SpT_Const_RectTiles','Tiles3x3+RectS2x2' ),
##
( 'ExtConv_Tiles_3x3Ctus_1SpT_Const_AsymSalTiles_P10_T30','Tiles3x3+MergeLow.3' ),
( 'ExtConv_Tiles_3x3Ctus_1SpT_Const_AsymSalTiles_P10_T40','Tiles3x3+MergeLow.4' ),
( 'ExtConv_Tiles_3x3Ctus_1SpT_Const_AsymSalTiles_P10_T50','Tiles3x3+MergeLow.5' ),
( 'ExtConv_Tiles_3x3Ctus_1SpT_Const_AsymSalTiles_P20_T30','Tiles3x3+MergeHigh.3' ),
( 'ExtConv_Tiles_3x3Ctus_1SpT_Const_AsymSalTiles_P20_T40','Tiles3x3+MergeHigh.4' ),
( 'ExtConv_Tiles_3x3Ctus_1SpT_Const_AsymSalTiles_P20_T50','Tiles3x3+MergeHigh.5' ),
( 'ExtConv_Tiles_1x1Ctus_1SpT_Const_AsymSalTiles_P10_T30','Tiles1x1+MergeLow.3' ),
( 'ExtConv_Tiles_1x1Ctus_1SpT_Const_AsymSalTiles_P10_T40','Tiles1x1+MergeLow.4' ),
( 'ExtConv_Tiles_1x1Ctus_1SpT_Const_AsymSalTiles_P10_T50','Tiles1x1+MergeLow.5' ),
( 'ExtConv_Tiles_1x1Ctus_1SpT_Const_AsymSalTiles_P20_T30','Tiles1x1+MergeHigh.3' ),
( 'ExtConv_Tiles_1x1Ctus_1SpT_Const_AsymSalTiles_P20_T40','Tiles1x1+MergeHigh.4' ),
( 'ExtConv_Tiles_1x1Ctus_1SpT_Const_AsymSalTiles_P20_T50','Tiles1x1+MergeHigh.5' ),
( 'ExtConv_Tiles_3x3Ctus_1SpT_AsymSalTiles_P20_T30','Tiles3x3+MergeHigh.3+NoMCTS' ),
##
( 'ExtConv_DynTilesCenterOut_2to10_1S_Const','AdaptiveTiles2to10' ),
( 'ExtConv_DynTilesCenterOut_2to5_1S_Const','AdaptiveTiles2to5' ),
( 'ExtConv_DynTilesCenterOut_5to3_1S_Const','AdaptiveTiles5to3' ),
( 'ExtConv_DynTilesCenterOut_5to2_1S_Const','AdaptiveTiles5to2' ),
( 'ExtConv_DynTilesCenterOut_4to2_1S_Const','AdaptiveTiles4to2' ),
#
( 'ExtConv_AsymmetricTilesVariance','AdaptiveVariance+6x3Tiles' ),
( 'ExtConv_AsymmetricTilesVariance8x4','AdaptiveVariance+8x4Tiles0+Sobel' ),
( 'ExtConv_AsymmetricTilesVariance8x4WithSobel','AdaptiveVariance+8x4Tiles+Sobel' ),
( 'ExtConv_AsymmetricTilesVariance8x4WithEntropy','AdaptiveVariance+8x4Tiles+Entropy' ),
( 'ExtConv_AsymmetricTilesVariance8x4WithTemporal','AdaptiveVariance+8x4Tiles+Temporal+Sobel' ),
( 'ExtConv_AsymmetricTilesVariance8x4WithTemporalEntropy','AdaptiveVariance+8x4Tiles+Temporal+Entropy' ),

( 'ExtConv_AsymmetricTilesVariance8x4WithTrueBits','AdaptiveVariance+8x4Tiles+TrueBits' ),
( 'ExtConv_AsymmetricTilesVariance7x4WithTrueBits','AdaptiveVariance+7x4Tiles+TrueBits' ),
( 'ExtConv_AsymmetricTilesVariance7x3WithTrueBits','AdaptiveVariance+7x3Tiles+TrueBits' ),

( 'BYTES_RANDOM_ACCESS_FOV_SAL_AVG','Avg. Bytes Required Random-Access PY' ),
( 'TILE_BITS_AVG: Avg Tile Size YAML','Avg. Tile Size PY' ),

( 'ExtConv_AsymmetricTilesVariance8x4WithTrueBits302','AdaptiveVariance+8x4Tiles+TrueBits302' ),
( 'ExtConv_AsymmetricTilesVariance6x3WithTrueBits302','AdaptiveVariance+6x3Tiles+TrueBits302' ),

( 'ExtConv_AsymmetricTilesVariance8x4WithSobelSpatioTemporal','AdaptiveVariance+8x4Tiles+SpatioTemporal' ),
( 'ExtConv_AsymmetricTilesVariance6x3WithSobelSpatioTemporal','AdaptiveVariance+6x3Tiles+SpatioTemporal' ),

( 'ExtConv_AsymmetricTilesVariance8x4WithSobelSpatioTemporalSaliency','AdaptiveVariance+8x4Tiles+SpatioTemporal+Saliency+L1' ),
( 'ExtConv_AsymmetricTilesVariance8x4WithSobelSpatioTemporalSaliency10','AdaptiveVariance+8x4Tiles+SpatioTemporal+Saliency+L10' ),
( 'ExtConv_AsymmetricTilesVariance8x4WithSobelSpatioTemporalSaliency01','AdaptiveVariance+8x4Tiles+SpatioTemporal+Saliency+L0.1' ),
( 'ExtConv_AsymmetricTilesVariance8x4WithSobelSpatioTemporalSaliency100','AdaptiveVariance+8x4Tiles+SpatioTemporal+Saliency+L100' ),
( 'ExtConv_AsymmetricTilesVariance8x4WithSobelSpatioTemporalSaliency1000','AdaptiveVariance+8x4Tiles+SpatioTemporal+Saliency+L1000' ),
( 'ExtConv_AsymmetricTilesVariance8x4WithSobelSpatioTemporalSaliency10000','AdaptiveVariance+8x4Tiles+SpatioTemporal+Saliency+L10000' ),


]

#ConfigMappingAppend = [
#( 'BYTES_RANDOM_ACCESS_FOV_SAL_AVG','Avg. Bytes Required Random-Access' ),
#( 'EncoderVVC360_VTM-73-360Lib-10','VVC-7.3' ),
#( 'EncoderVVC360_VTM-73-360Lib-10-MCTSSliceLevel','VVC-7.3+MCTS-Slice' ),
#( 'EncoderVVC360_VTM-91-360Lib-101','VVC-9.1' ),

#( 'ExtConv_Tiles_4x4Ctus_1S_Const','Fixed (8x4)' ),
#( 'ExtConv_Tiles_5x5Ctus_1S_Const','Fixed (6x3)' ),
#( 'ExtConv_AsymmetricTilesVariance8x4WithSobelSpatioTemporal','Prop (8x4)' ),
#( 'ExtConv_AsymmetricTilesVariance6x3WithSobelSpatioTemporal','Prop (6x3)' ),
#]

ConfigMapping.extend( ConfigMappingAppend )

#( 'ExtConv_Tiles_3x3Ctus_1SpT','Tiles3x3+NoMCTS' ),
#( 'ExtConv_Tiles_1x1Ctus_1SpT','Tiles1x1+NoMCTS' ),
#( 'ExtConv_Tiles_1x1Ctus_1SpT_Const','Tiles1x1' ),
#( 'ExtConv_Tiles_2x2Ctus_1SpT_Const','Tiles2x2' ),
#( 'ExtConv_Tiles_3x3Ctus_1SpT_Const','Tiles3x3' ),
#( 'ExtConv_Tiles_4x4Ctus_1SpT_Const','Tiles4x4' ),
#( 'ExtConv_Tiles_8x8Ctus_1SpT_Const','Tiles8x8' ),


###################################################################################################################
# Template

GnuPlotTemplateExtra = """
# Extra template
set style line 1 lc 4 lt  1 lw 2 pt  10 ps 1
set style line 2 lc 2 lt  1 lw 2 pt  3 ps 1
set style line 3 lc 3 lt  1 lw 2 pt  4 ps 1
set style line 4 lc 1 lt  1 lw 2 pt  2 ps 1
set style line 5 lc 7 lt  1 lw 2 pt  6 ps 1
set style line 6 lc 8 lt  6 lw 2 pt  8 ps 1
set style line 7 lc 2 lt  7 lw 2 pt  8 ps 1
set style line 8 lc 3 lt  8 lw 2 pt  9 ps 1
set style line 9 lc 4 lt  9 lw 2 pt  10 ps 1
"""

GnuPlotTemplateBarPlotExtra = """
# Extra template for bar graph
"""


LatexTemplateDefault = """
% Extra latex argurment before begin document
"""


