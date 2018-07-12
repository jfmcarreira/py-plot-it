set terminal pdfcairo mono \
font 'TimesNewRoman,14'

set datafile missing '-'

set grid
#set size square {1,.5}

set title center  offset character 0, -.9

set xlabel center
set ylabel center offset character 1, 0


set key spacing 1 width 0

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

set xlabel 'Packet Loss Ratio [%]'
set ylabel 'PSNR [dB]'
set key bottom left Left reverse

set output 'lowdelay_P_4R_slice_1200B_seq_cactus_rate_single.pdf'
set title 'Low-Delay - 1200B - Cactus - Main rate'
plot '-' using 2:1 w lp ls 1 title 'Reference', '-' using 2:1 w lp ls 2 title 'Constant', '-' using 2:1 w lp ls 3 title 'Best', '-' using 2:1 w lp ls 4 title 'Predicted'
38.00 0.0 
37.13 0.5 
36.51 1.0 
36.26 1.2 
35.79 1.6 
35.51 2.0 
35.29 2.2 
35.22 2.4 
34.99 2.6 
34.83 2.8 
34.78 3.0 
33.68 5.0 
31.93 10.0 
e 
37.56 0.0 
37.48 0.5 
37.42 1.0 
37.37 1.2 
37.28 1.6 
37.18 2.0 
37.19 2.2 
37.11 2.4 
37.00 2.6 
37.02 2.8 
36.92 3.0 
36.35 5.0 
34.24 10.0 
e 
38.00 0.0 
37.51 0.5 
37.42 1.0 
37.37 1.2 
37.28 1.6 
37.18 2.0 
37.19 2.2 
37.11 2.4 
37.00 2.6 
37.02 2.8 
36.92 3.0 
36.35 5.0 
34.24 10.0 
e 
38.00 0.0 
37.48 0.5 
37.42 1.0 
37.37 1.2 
37.28 1.6 
37.18 2.0 
37.19 2.2 
37.11 2.4 
37.00 2.6 
37.02 2.8 
36.92 3.0 
36.12 5.0 
34.15 10.0 
e 

