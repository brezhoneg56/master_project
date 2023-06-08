set grid

set title 'Plot Comparison over [2, 3, 5, 7, 10] subintervals'

set xlabel 'Sweep [-]'
set ylabel 'Momentum Defect [kg m/s]'
set yrange [0.0:3]
set xrange [0:10]

## Labels
# 1 : Sweep
# 2 : PressureDrop
# 3 : Velocity Defect
# 4 : Continuity Defect
# 5 : WallTime for PimpelDyMFoam
# 6 : Total Accumulated WallTime

set key bottom right

#set style line 1 lc rgb 'black' lt 1 lw 4 pt 7 pi -1 ps 0.9
#set style line 2 lc rgb 'black' lt 1 lw 1 pt 5 pi -1 ps 0.9
#set style line 7 lc rgb 'black' lt 2 lw 1 pt 5 pi -1 ps 0.75

#set style line 4 lt 1 lc rgb "black" pi -1 pt 7 ps 0.6 lw 2.0

#set pointintervalbox 1.4

set terminal postscript eps 18 dashed lw 1 enhanced 
set output 'plot_1_3_Comparison_intervals_zoom.eps'


plot 'logtable2.csv' using 1:($3/2) with linespoints title '2 intervals' , \
'logtable3.csv' using 1:($3/3) with linespoints title '3 intervals' , \
'logtable5.csv' using 1:($3/5) with linespoints title '5 intervals' , \
'logtable7.csv' using 1:($3/7) with linespoints title '7 intervals' , \
'logtable10.csv' using 1:($3/10) with linespoints title '10 intervals'

set terminal pngcairo size 2400, 1600 dashed lw 1 enhanced 
set output 'plot_1_3_Comparison_intervals_zoom.png'

replot
