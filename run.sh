python tcpcwnd.py -n 10 -o output_raw.txt
python formatOutput.py -f output_raw.txt -o output_formatted.txt
python plot_figure.py -f output_formatted.txt -o fig6.png