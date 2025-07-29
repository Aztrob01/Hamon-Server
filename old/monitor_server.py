from flask import Flask, render_template, jsonify, request
import multiprocessing
import platform
import datetime 
import cpuinfo
import psutil 
import sys

app = Flask(__name__)

if __name__ == "__main__":
    multiprocessing.freeze_support()

last_io = {
    "read": 0,
    "write": 0,
    "time": datetime.datetime.now(),
}

def get_top_mem_process():
    processes = [];
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

def get_system_data():    
    # recursos base
    global last_io
    mem = psutil.virtual_memory() ### 
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time()) ### uptime = (hora atual) - (hora do boot)
    cpu_name = cpuinfo.get_cpu_info().get('brand_raw', platform.processor())
    now = datetime.datetime.now()
    user_agent = request.headers.get('User-Agent', 'Desconhecido') # user agent request pro html

    # configs de disco
    io_counters = psutil.disk_io_counters()
    elapsed_disk_time = (now - last_io["time"]).total_seconds()
    read_diff = io_counters.read_bytes - last_io["read"]
    write_diff = io_counters.write_bytes - last_io["write"]
    read_speed = read_diff / (1024 ** 2) / elapsed_disk_time
    write_speed = write_diff / (1024 ** 2) / elapsed_disk_time
    last_io['read'] = io_counters.read_bytes
    last_io['write'] = io_counters.write_bytes
    last_io['time'] = now

    # processos em uso maximo
    top_proc = get_top_mem_process()
    top_cpu_proc = max(psutil.process_iter(['name', 'pid', 'cpu_percent']), key=lambda p: p.info.get('cpu_percent', 0))
    top_cpu_name = f"{top_cpu_proc.info['name']} (PID {top_cpu_proc.info['pid']})"
    top_cpu_usag = f"{top_cpu_proc.info.get('cpu_percent', 0):.1f}%"

    return {
        # Dados do Processador
        "cpu": cpu_name, 
        "cpu_percent": psutil.cpu_percent(interval=1),
        "top_cpu_name":top_cpu_name,
        "top_cpu_usag":top_cpu_usag,
        # Dados da Memoria
        "mem_total": f"{mem.total / (1024 ** 3):.1f} GB",
        "mem_used": f"{mem.used / (1024 ** 3):.1f} GB",
        "mem_percent": psutil.virtual_memory().percent,
        "top_mem_name": top_proc['name'],
        "top_mem_usag": top_proc['mem_usage'],
        # Dados de Disco
        "disk_read":f"{read_speed:.2f}",
        "disk_write":f"{write_speed:.2f}", 
        # Dados do Sistema
        "os": f"{platform.system()} {platform.release()}",
        "uptime": str(uptime).split('.')[0], # remove ms
        "timestamp": datetime.datetime.now().strftime('%H:%M:%S'),
        # Dados de Otimização
        "user_agent": user_agent,
    }

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/data')
def data():
    return jsonify(get_system_data())

if __name__ == '__main__':
    if hasattr(sys, 'frozen'):
        print('Servidor Iniciando...')
        app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    else:
        app.run(host='0.0.0.0', port=8080, debug=True)