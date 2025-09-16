from flask import Flask, render_template, jsonify
# TODO from colorama import Fore as color, Style, init
from ctypes import * 

import os, datetime, time, subprocess, json
import platform, socket
import psutil, cpuinfo

# TODO init()
mainInterval = 0
selectMode = 0
run_proc = 0
#? psutil/cpuinfo/socket/platform SYS catch
cpu_info = cpuinfo.get_cpu_info()
cpu_thrd = psutil.cpu_count()
cpu_phys = psutil.cpu_count(logical=False)
hst_name = socket.gethostname()
sys_name = platform.system()
sys_vers = platform.version()

cpu_name = cpu_info['brand_raw']
#? psutil CPU catch
cpu_percent = psutil.cpu_percent(interval=0.5)
#? Memory catch
memory = psutil.virtual_memory()
memory_t = memory.total / (1024 ** 3)
#? Swap Memory catch
swap = psutil.swap_memory()
swap_t = swap.total / (1024 ** 3)
mem_all = round((swap_t + memory_t), 1)
#? Main Menu
def run_interval():
    try:
        global mainInterval
        mainInterval = float(input("Select an interval in seconds: "))
        if mainInterval < 0.5 or mainInterval > 1.5:
            print("The value cant be lower than 0.5 or higher than 1.5!")
            run_interval()
    except ValueError:
        print("Unnescpected value... Please try again!")
        run_interval()
def run_mode():
    try:
        global selectMode
        selectMode = int(input("Please, select the Operation Mode:\n 1. Precision\n 2. Exit\n"))
        if selectMode == 2:
            print("Bye bye!")
            exit(0)
    except ValueError:
        print("Unnespected value... Please try again!")
        run_mode()
#? run executable in output
def run_exe():
        print("Trying to find the exe...")
        time.sleep(0.5)
        global run_proc
        try:
            run_proc = subprocess.Popen("./output/main.exe")
        except Exception as error:
            print("An fatal error has occurred: ", error)
            run_proc.terminate()
            exit(-1)
            
        

def main():
    print("Starting...")
    time.sleep(0.5)
    run_interval()
    print("-" * 40)
    time.sleep(0.5)
    run_mode()
    print("-" * 40)

    def run_flask():
        if selectMode == 1:
            run_exe()
        print("Flask is starting in mode ", selectMode)
        app = Flask(__name__)

        def mode_one():
            try:
                while True:
                    time.sleep(mainInterval)
                    #TODO: Limit reading to only when the json is "OK!"
                    with open("./data.json", "r") as data:
                        content = json.load(data)
                        cpu_percent = round(content.get("cpu"), 1)
                        cpu_timestamp = content.get("timestamp")
                        cpu_interval = content.get("interval")
                        
                        json_name = content.get("name")

                        gpu_percent = content.get("gpu")
                        gpu_name = content.get("gpuname")
                        directX = content.get("directX")

                        return{
                            "cpu_per": f"{cpu_percent}%",
                            "cpu_upd": cpu_timestamp,
                            "cpu_int": f"{cpu_interval}ms",
                            "program_interval": mainInterval
                        }
            except KeyboardInterrupt:
                run_proc.terminate()
        
        # app route and run
        @app.route('/')
        def index():
            return render_template('index.html')
        
        @app.route('/data')
        def data():
            return jsonify(mode_one())

        app.run(host="0.0.0.0", port="8080")
    run_flask()
main()