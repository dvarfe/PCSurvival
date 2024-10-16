import GPUtil
import psutil
import time
import signal
import os
import csv

# Data is collected once in GET_STATS_TIMEOUT seconds and 
# recorded on hard drive once in NUM_GET_STATS_ITERS * GET_STATS_TIMEOUT
NUM_GET_STATS_ITERS = 5
GET_STATS_TIMEOUT = 2
FILE_PATH = "data.csv"

DISK_PATH = '/'


csv_keys = [["timestamp", "device", "measure", "value"]]
cpu_general_info = {"logical_CPU" : psutil.cpu_count(), 
                    "physical_CPU" : psutil.cpu_count(logical = False)}
ram_general_info = {"total_memory" : psutil.virtual_memory().total,
                    "total_swap" : psutil.swap_memory().total}
disks_general_info = {"num_partitions" : len(psutil.disk_partitions(all=True)),
                      "physical_partitions" : len(psutil.disk_partitions(all=False))}

data = []

def initialize_data():
    with open(FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_keys)
        writer.writerows(get_general_info("cpu", cpu_general_info))
        writer.writerows(get_general_info("ram", ram_general_info))
        writer.writerows(get_general_info("disks", disks_general_info))
        writer.writerows(get_temp_general_info())
        writer.writerows(get_gpu_general_info())

def get_general_info(device, meaurements):
    gen_info = []
    for key in meaurements:
        cur_dict = [0, device, key, meaurements[key]]
        gen_info.append(cur_dict)
    return gen_info

def get_temp_general_info():
    info = []
    sensors = psutil.sensors_temperatures()
    for name, entries in sensors.items():
        for entry in entries:
            info.append([0, 'tempertature', 'critical_' + name + '|' + entry.label, entry.critical])
    return info
def get_gpu_general_info():
    info = []
    gpus = GPUtil.getGPUs()
    for gpu in gpus:
        this_device = "gpu_" + gpu.uuid
        info.append([0, this_device, "gpu_name", gpu.name])
        info.append([0, this_device, "gpu_memory_total", gpu.memoryTotal])
        info.append([0, this_device, "driver", gpu.driver])
    print(info)
    return info


def save_data():
    with open(FILE_PATH, "a") as csvfile:
        print('writing data')
        writer = csv.writer(csvfile)
        for line in data:
            writer.writerows(line)

def signal_handler(sig, frame):
    save_data()
    print("Данные сохранены перед отключением.")
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def get_cpu_info():
    cur_time = int(time.time())
    cpu_percent = psutil.cpu_percent()
    cpu_time = psutil.cpu_times()
    cpu_freq = psutil.cpu_freq().current
    measurement_dict = {"cpu_percent" : cpu_percent, "user_time" : cpu_time.user,
                        "system_time" : cpu_time.system, "idle_time" : cpu_time.idle, 
                        "frequency" : cpu_freq}
    info = []   
    for key in measurement_dict:
        info.append([cur_time, "cpu", key, measurement_dict[key]])
    return info

def get_ram_info():
    cur_time = int(time.time())
    ram_percent = psutil.virtual_memory().percent
    swap_percent = psutil.swap_memory().percent
    measurement_dict = {"ram_percent" : ram_percent, "swap_percent" : swap_percent}
    info = []
    for key in measurement_dict:
        info.append([cur_time, "ram", key, measurement_dict[key]])
    return info

def get_disk_info():
    cur_time = int(time.time())
    disk_percent = psutil.disk_usage(DISK_PATH).percent
    disk_io = psutil.disk_io_counters()
    measurement_dict = {"disk_percent" : disk_percent, "write_count" : disk_io.write_count,
                        "write_bytes" : disk_io.write_bytes, "read_count" : disk_io.read_count,
                        "read_bytes" : disk_io.read_bytes}
    info = []
    for key in measurement_dict:
        info.append([cur_time, "disks", key, measurement_dict[key]])
    return info

def get_temperature():
    cur_time = int(time.time())
    sensors = psutil.sensors_temperatures()
    info = []
    for name, entries in sensors.items():
        for entry in entries:
            info.append([cur_time, 'tempertature', name + '|' + entry.label, entry.current])
    return info

# def get_one_gpu_info(gpu):
#     cur_time = int(time.time())
#     info = []
#     this_device = "gpu_" + gpu.uuid
#     info.append([cur_time, this_device, "gpu_load", gpu.load * 100])
#     info.append([cur_time, this_device, "gpu_memory_used", gpu.memoryUsed])
#     info.append([cur_time, this_device, "gpu_memory_util", gpu.memoryUtil])
#     info.append([cur_time, this_device, "gpu_temperature", gpu.temperature])
#     return info


def get_gpu_info():
    GPUs = GPUtil.getGPUs()
    info = []
    for gpu in GPUs:
        cur_time = int(time.time())
        info = []
        this_device = "gpu_" + gpu.uuid
        info.append([cur_time, this_device, "gpu_load", gpu.load * 100])
        info.append([cur_time, this_device, "gpu_memory_used", gpu.memoryUsed])
        info.append([cur_time, this_device, "gpu_memory_util", gpu.memoryUtil])
        info.append([cur_time, this_device, "gpu_temperature", gpu.temperature])
    return info
 

    
def collect_stats():
    i = 1
    global data

    while True:
        data.append(get_cpu_info())
        data.append(get_ram_info())
        data.append(get_disk_info())
        data.append(get_temperature())
        data.append(get_gpu_info()) 
        if i == NUM_GET_STATS_ITERS:
            i = 0
            save_data()
            data = []
        i += 1
        time.sleep(GET_STATS_TIMEOUT)

if __name__ == "__main__":
    initialize_data()
    collect_stats()

