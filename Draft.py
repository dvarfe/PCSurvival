import psutil
import time
import signal
import os
import csv

# Data is collected once in GET_STATS_TIMEOUT seconds and 
# recorded on hard drive once in NUM_GET_STATS_ITERS * GET_STATS_TIMEOUT
#RECORD_TIMEOUT = 15
NUM_GET_STATS_ITERS = 5
GET_STATS_TIMEOUT = 1

cpu_stats_keys = [["timestamp", "cpu_usage"]]
ram_stats_keys = [["timestamp", "memory_usage"]]
disk_stats_keys = [["timestamp", "disk_usage"]]

CPU_FILE_PATH = "cpu.csv"
RAM_FILE_PATH = "ram.csv"
DISK_FILE_PATH = "disk.csv"

data = [[], [], []]

def initialize_one_file(path, keys):
    with open(path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(keys) 

def initialize_files():
    initialize_one_file(CPU_FILE_PATH, cpu_stats_keys)
    initialize_one_file(RAM_FILE_PATH, ram_stats_keys)
    initialize_one_file(DISK_FILE_PATH, disk_stats_keys)

def save_one_file(path, data):
    with open(path, "a") as csvfile:
        print('writing data')
        writer = csv.writer(csvfile)
        writer.writerows(data)

def save_data():
    save_one_file(CPU_FILE_PATH, data[0])
    save_one_file(RAM_FILE_PATH, data[1])
    save_one_file(DISK_FILE_PATH, data[2])

def signal_handler(sig, frame):
    save_data()
    print("Данные сохранены перед отключением.")
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def collect_stats():
    i = 1
    global data

    while True:
        data[0].append([int(time.time()), psutil.cpu_percent()])
        data[1].append([int(time.time()), psutil.virtual_memory().percent])
        data[2].append([int(time.time()), psutil.disk_usage("/").percent])
       
        if i == NUM_GET_STATS_ITERS:
            i = 0
            save_data()
            data = [[], [], []]
        i += 1
        time.sleep(GET_STATS_TIMEOUT)
if __name__ == "__main__":
    initialize_files()
    collect_stats()

