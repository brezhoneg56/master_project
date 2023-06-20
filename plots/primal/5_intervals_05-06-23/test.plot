set grid

set xlabel "Index"
set ylabel "Value"

set terminal pngcairo
set output "plot.png"

plot "logtable.csv" using 1:2 with linespoints title "Column 2"
