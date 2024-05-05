#phyphox configuration
import time
import os
import threading
from datetime import datetime

import numpy as np
import requests
import PySimpleGUI as sg


def start_collecting(IP_address):
    url = IP_address + "control?cmd=start"
    print(url)
    data = requests.get(url=url).json()


def stop_collecting(IP_address):
    url = IP_address + "control?cmd=stop"
    data = requests.get(url=url).json()


def save_collection(IP_address, save_path):
    url = IP_address + "export?format=2"
    data = requests.get(url=url).content

    with open(save_path, 'wb') as file:
        file.write(data)


def clear_collection(IP_address):
    url = IP_address + "control?cmd=clear"
    data = requests.get(url=url).json()


def timer(stop_flag, leaved_time=10):
    start_time = time.time()
    
    leaved_time = float(leaved_time)
    if leaved_time <= 0:
        levaed_time = np.inf
    
    while True:
        current_time = time.time()
        
        delta_time = current_time - start_time
        
        window['timer_display'].update(f'{delta_time:.2f} s')
        window.Refresh()
        
        time.sleep(0.1)
        
        if stop_flag():
            break
            
        if delta_time > leaved_time:
            time_format = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = os.path.join(CWD, f'{time_format}_{values["save_name"]}.rar')
        
            stop_collecting(values['ip_port'])
            save_collection(values['ip_port'], save_path)
            window['timer_display'].update(f'0.0 s')
            window['display'].update(f'Auto Save: {save_path}')
            window['save_name'].update('temp')
            window.Refresh()
            
            break

CWD = os.getcwd()

# Define the window's contents
layout = [[sg.Text(f'IP Address and Port Number of the Device', size=(80, 1))],
          [sg.Input(key='ip_port', size=(80, 1))],
          [sg.Text(f'Save Path (cwd: {CWD})', size=(80, 1))],
          [sg.Input('temp', key='save_name', size=(80, 1))],
          [sg.Text('Init', size=(80, 1), key='display')],
          [sg.Text('leaved time:', size=(12, 1)), sg.Input('10', key='leaved_time', size=(5, 1)), sg.Text('timer:', size=(6, 1)), sg.Text('0.0 s', size=(10, 1), key='timer_display')],
          [sg.Button('AutoStart'), sg.Button('Start'), sg.Button('Stop'), sg.Button('Save')],
          [sg.Button('Clear'), sg.Button('Quit')]]

# Create the window
window = sg.Window('PhyPhox Remote APP', layout)
stop_flag = True

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED or event == 'Quit':
        break
    elif event == 'AutoStart':
        message = 'AutoStart Collecting'
        
        stop_flag = False
        timer_thread = threading.Thread(target=timer, args=(lambda: stop_flag, values['leaved_time']), daemon=True)
        
        clear_collection(values['ip_port'])
        start_collecting(values['ip_port'])
        timer_thread.start()
    elif event == 'Start':
        message = 'Start Collecting'
        
        stop_flag = False
        timer_thread = threading.Thread(target=timer, args=(lambda: stop_flag, values['leaved_time']), daemon=True)
        
        start_collecting(values['ip_port'])
        timer_thread.start()
    elif event == 'Stop':
        message = 'Stop Collecting'
        
        stop_flag = True
        del timer_thread
        
        stop_collecting(values['ip_port'])
    elif event == 'Save':
        time_format = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_path = os.path.join(CWD, f'{time_format}_{values["save_name"]}.rar')
        message = f'Save Data to {save_path}'
        save_collection(values['ip_port'], save_path)
        window['save_name'].update('temp')
    elif event == 'Clear':
        message = 'Clear Collection'
        clear_collection(values['ip_port'])
        window['timer_display'].update(f'0.0 s')

    # Output a message to the window
    window['display'].update(message)

# Finish up by removing from the screen
window.close()
