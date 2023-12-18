# logging_example.py

import logging
import sys

f_format = logging.Formatter('[%(asctime)s] [%(levelname)s] | %(message)s')


std_out_handler = logging.StreamHandler(sys.stdout)
std_out_handler.setLevel(level=logging.ERROR)
std_out_handler.setFormatter(f_format)


# Create a daily runs logger
daily_logger = logging.getLogger("runs")
daily_logger.setLevel(logging.DEBUG)
daily_f_handler = logging.FileHandler('/Users/goram/Code_files/Trading-full-stack-app/log/daily_run.log')
daily_f_handler.setLevel(logging.DEBUG)
daily_f_handler.setFormatter(f_format)
daily_logger.addHandler(daily_f_handler)
# daily_logger.addHandler(std_out_handler)





# Create a trades_executer logger
trades_executer_logger = logging.getLogger("trades")
trades_executer_logger.setLevel(logging.DEBUG)
trades_executer_f_handler = logging.FileHandler('/Users/goram/Code_files/Trading-full-stack-app/log/trades_executer.log')
trades_executer_f_handler.setLevel(logging.DEBUG)
trades_executer_f_handler.setFormatter(f_format)
trades_executer_logger.addHandler(trades_executer_f_handler)

# Create a real_time logger
real_time_logger = logging.getLogger("realtime")
real_time_logger.setLevel(logging.DEBUG)
real_time_f_handler = logging.FileHandler('/Users/goram/Code_files/Trading-full-stack-app/log/ticks.log')
real_time_f_handler.setLevel(logging.DEBUG)
real_time_f_handler.setFormatter(f_format)
real_time_logger.addHandler(real_time_f_handler)