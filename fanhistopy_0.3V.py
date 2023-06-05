import requests
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading

stop_flag = False
continue_flag = False

def allrv(wikiname, lang, start=1):
    global stop_flag, continue_flag
    prefix = 'https://'
    midfix = '.fandom.com/'
    suffix = '/api.php?action=query&prop=revisions&revids='
    suffix2 = '&format=json&formatversion=2'
    suffixt = '/api.php?action=query&meta=siteinfo&siprop=statistics&format=json'
    site = wikiname
    urlt = f"{prefix}{site}{midfix}{lang}{suffixt}"
    response = requests.get(urlt)
    data = response.json()
    total = data['query']['statistics']['edits']
    output_file = f"{lang}.{wikiname}-{start}-{total}.txt"
    with open(output_file, 'w', encoding='utf-8') as file:
        for idx in range(start, total + 1):
            if stop_flag:
                break
            if continue_flag:
                continue_flag = False
                continue
            url = f"{prefix}{site}{midfix}{lang}{suffix}{idx}{suffix2}"
            response = requests.get(url)
            data = response.json()
            rvstrm = [str(idx)]
            if 'pages' not in data['query']:
                rvstrm.extend(["error", "error", "error"])
            else:
                rvstrm.append(data['query']['pages'][0]['title'])
                if 'missing' in data['query']['pages'][0]:
                    rvstrm.extend(["error", "error"])
                else:
                    rvstrm.append(data['query']['pages'][0]['revisions'][0]['timestamp'])
                    rvstrm.append(data['query']['pages'][0]['revisions'][0]['user'])
            file.write('\t'.join(rvstrm) + '\n')
            print(f'已完成{idx}/{total}')
            progress_bar['value'] = (idx / total) * 100
            root.update_idletasks()
    return f"{lang}.{wikiname}已完成"

def run_program():
    global stop_flag, continue_flag
    stop_flag = False
    continue_flag = False
    wikiname = wikiname_entry.get()
    lang = lang_entry.get()
    start = int(start_entry.get()) if start_entry.get() else 1
    thread = threading.Thread(target=allrv, args=(wikiname, lang, start))
    thread.start()

def stop_program():
    global stop_flag
    stop_flag = True

def continue_program():
    global continue_flag
    continue_flag = True

root = tk.Tk()
root.title("Fanhistopy 0.3V")

wikiname_label = tk.Label(root, text="输入wiki名称:")
wikiname_label.grid(row=0, column=0)
wikiname_entry = tk.Entry(root)
wikiname_entry.grid(row=0, column=1)

lang_label = tk.Label(root, text="输入语言:")
lang_label.grid(row=1, column=0)
lang_entry = tk.Entry(root)
lang_entry.grid(row=1, column=1)

start_label = tk.Label(root, text="输入1确认开始:")
start_label.grid(row=2, column=0)
start_entry = tk.Entry(root)
start_entry.grid(row=2, column=1)

submit_button = tk.Button(root, text="开始", command=run_program)
submit_button.grid(row=3, column=1)

stop_button = tk.Button(root, text="停止", command=stop_program)
stop_button.grid(row=4, column=0)

continue_button = tk.Button(root, text="继续", command=continue_program)
continue_button.grid(row=4, column=1)

progress_label = tk.Label(root, text="Progress:")
progress_label.grid(row=5, column=0)
progress_bar = ttk.Progressbar(root, orient='horizontal', length=200, mode='determinate')
progress_bar.grid(row=5, column=1)

result_label = tk.Label(root, text="")
result_label.grid(row=6, column=1)

root.mainloop()

