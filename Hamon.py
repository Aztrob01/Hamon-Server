from flask import Flask, render_template, jsonify, request
import multiprocessing ### to hold multiple executions 
import platform, datetime, sys, os ### to get system informations
import cpuinfo, psutil


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

template_folder = resource_path("templates")
static_folder = resource_path("static")
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

if __name__ == "__main__":
    multiprocessing.freeze_support()

last_io = { ### write disk initial informations
    "read": 0,
    "write": 0,
    "time": datetime.datetime.now(),
}


def get_top_mem_proc():
    processes = []
    for p in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            if p.info.get('memory_info'):
                processes.append(p)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if not processes:
        return {'name': 'Desconhecido', 'mem_usage': '0 MB'}
    
    top_proc = max(processes, key=lambda p: p.info['memory_info'].rss)
    mem_usage = f"{top_proc.info['memory_info'].rss / (1024 **2):.1f}"
    return {'name': top_proc.info['name'], 'mem_usage': mem_usage}


def app_run():
    global last_io 
    psutil.cpu_percent()

    # get data    
    mem = psutil.virtual_memory() 
    cpu_name = cpuinfo.get_cpu_info().get('brand_raw', platform.processor())
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
    now = datetime.datetime.now()
    agent = request.headers.get('User-Agent', 'Desconhecido')

    # get data from disk
    io_counters = psutil.disk_io_counters()
    elapsed_disk_time = (now - last_io["time"]).total_seconds()
    read_diff = io_counters.read_bytes - last_io["read"]
    write_diff = io_counters.write_bytes - last_io["write"]
    read_speed = read_diff / (1024 ** 2) / elapsed_disk_time
    write_speed = write_diff / (1024 ** 2) / elapsed_disk_time
    last_io['read'] = io_counters.read_bytes
    last_io['write'] = io_counters.write_bytes
    last_io['time'] = now

    # max usage proccesses
    top_proc = get_top_mem_proc()
    top_cpu_proc = max(psutil.process_iter(['name', 'pid', 'cpu_percent']), key=lambda p: p.info.get('cpu_percent', 0))
    top_cpu_name = f"{top_cpu_proc.info['name']} (PID {top_cpu_proc.info['pid']})"
    top_cpu_usage = f"{top_cpu_proc.info.get('cpu_percent', 0):.1f}%"
    
    return {
        "cpu": cpu_name,
        "cpu_percent": psutil.cpu_percent(interval=None),
        "cpu_per_thread": psutil.cpu_percent(interval=0.1, percpu=True),
        "top_cpu_name": top_cpu_name,
        "top_cpu_usage": top_cpu_usage,

        "mem_total": f"{mem.total / (1024 ** 3):.1f} GB",
        "mem_used": f"{mem.used / (1024 ** 3):.1f} GB",
        "mem_percent": psutil.virtual_memory().percent,
        "top_mem_name": top_proc['name'],
        "top_mem_usage":top_proc['mem_usage'],

        "disk_read": f"{read_speed:.2f}",
        "disk_write": f"{write_speed:.2f}",

        "os": f"{platform.system()} {platform.release()}",
        "uptime": str(uptime).split('.')[0], 
        "timestamp": datetime.datetime.now().strftime('%H:%M:%S'),
        "user_agent": agent,
    }

@app.route('/')
def index():
    return render_template("index.html")

@app.route ("/data")
def data():
    return jsonify(app_run())
if __name__ == "__main__":
    if hasattr(sys, 'frozen'):
        print('Roubando dados da sua Maquina...')
        app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False, threaded=True)
    else:
        app.run(host="0.0.0.0", port=8080, debug=True, threaded=True)
