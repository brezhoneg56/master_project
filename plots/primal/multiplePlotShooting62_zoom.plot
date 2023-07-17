set grid

set title 'Plot Comparison over [2, 3, 5, 7, 10] subintervals'

set xlabel 'Total Accumulated Time [s]'
set ylabel 'Pressure Drop [Nm]'
#set yrange [0:1.3e-07]
#set xrange [0:531.622]

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
set output 'plot_6_2_Comparison_intervals_zoom.eps'

plot '1_intervals_05-06-23/logtable1.csv' using 6:2 with linespoints title '1 intervals' , \
'2_intervals_05-06-23/logtable2.csv' using 6:2 with linespoints title '2 intervals' , \
'3_intervals_05-06-23/logtable3.csv' using 6:2 with linespoints title '3 intervals' , \
'5_intervals_05-06-23/logtable5.csv' using 6:2 with linespoints title '5 intervals' , \
'7_intervals_05-06-23/logtable7.csv' using 6:2 with linespoints title '7 intervals' , \
'10_intervals_05-06-23/logtable10.csv' using 6:2 with linespoints title '10 intervals'

set output 'plot_6_2_Comparison_intervals_zoom.png'

plot '1_intervals_05-06-23/logtable1.csv' using 6:2 with linespoints title '1 intervals' , \
'2_intervals_05-06-23/logtable2.csv' using 6:2 with linespoints title '2 intervals' , \
'3_intervals_05-06-23/logtable3.csv' using 6:2 with linespoints title '3 intervals' , \
'5_intervals_05-06-23/logtable5.csv' using 6:2 with linespoints title '5 intervals' , \
'7_intervals_05-06-23/logtable7.csv' using 6:2 with linespoints title '7 intervals' , \
'10_intervals_05-06-23/logtable10.csv' using 6:2 with linespoints title '10 intervals'
