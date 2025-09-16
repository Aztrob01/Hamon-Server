from flask import Flask, render_template, jsonify
# TODO from colorama import Fore as color, Style, init
from ctypes import * 

import os, datetime, time, subprocess, json
import platform, socket
import psutil, cpuinfo

run = subprocess.Popen("./output/main.exe")