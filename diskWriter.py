import logging
import psutil
import time
import datetime

# monitor CPU usage

# with every run of the script, this file is rewritten
def write_cpu_usage():
    # monitor CPU usage
    f = open("cpu_usage.csv", "w")
    f.write(f"Number,Time,CPU,RAM\n")
    logging.info("Writing to file started")
    timer = 1
    while True:
        f.write(f"{timer}, {datetime.datetime.now()}, {str(psutil.cpu_percent())}, {str(psutil.virtual_memory().percent)} \n")
        f.flush()
        timer = timer + 1
        time.sleep(2) #slee for 60 seconds


# this is necessary with every server downgrade or upgrade
def empty_file_contents():
    f = open("cpu_usage.csv", "w")
    f.write('Number,Time,CPU,RAM\n')
    f.close()