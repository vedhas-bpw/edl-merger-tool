import tkinter as tk
from tkinter import filedialog, messagebox
import re

def normalize_clip_name(clip_name):
    return clip_name.replace("_mov", ".mov")

def parse_edl(file_path):
    with open(file_path, 'r', errors='ignore') as file:
        lines = file.readlines()
    events = []
    current_event = []
    for line in lines:
        if re.match(r'^\d{3,8}\s', line):
            if current_event:
                events.append(current_event)
            current_event = [line.rstrip()]
        else:
            if line.strip() or current_event:
                current_event.append(line.rstrip())
    if current_event:
        events.append(current_event)
    return events

def write_edl(events, output_path):
    with open(output_path, 'w') as f:
        for event in events:
            f.write("\n".join(event) + "\n")

def merge_color_data(primary_path, secondary_path, output_path):
    primary_events = parse_edl(primary_path)
    secondary_events = parse_edl(secondary_path)
    clip_to_asc_data = {}
    for event in primary_events:
        clip_name, asc_sop, asc_sat = None, None, None
        for line in event:
            if "* FROM CLIP NAME:" in line:
                clip_name = normalize_clip_name(line.split(":")[-1].strip())
            elif "* ASC_SOP" in line:
                asc_sop = line
            elif "* ASC_SAT" in line:
                asc_sat = line
        if clip_name:
            clip_to_asc_data[clip_name] = {"ASC_SOP": asc_sop, "ASC_SAT": asc_sat}
    updated_events = []
    for event in secondary_events:
        updated_event = list(event)
        clip_name = None
        for line in event:
            if "* FROM CLIP NAME:" in line:
                clip_name = normalize_clip_name(line.split(":")[-1].strip())
                break
        if clip_name and clip_name in clip_to_asc_data:
            asc_data = clip_to_asc_data[clip_name]
            insert_index = len(updated_event)
            for idx, line in enumerate(updated_event):
                if "* FROM CLIP NAME:" in line:
                    insert_index = idx + 1
                    break
            if asc_data["ASC_SOP"]:
                updated_event.insert(insert_index, asc_data["ASC_SOP"])
                insert_index += 1
            if asc_data["ASC_SAT"]:
                updated_event.insert(insert_index, asc_data["ASC_SAT"])
        updated_events.append(updated_event)
    write_edl(updated_events, output_path)

def run_merge():
    primary_path = filedialog.askopenfilename(title="Select PRIMARY EDL")
    if not primary_path: return
    secondary_path = filedialog.askopenfilename(title="Select SECONDARY EDL")
    if not secondary_path: return
    output_path = filedialog.asksaveasfilename(defaultextension=".edl", title="Save Merged EDL As")
    if not output_path: return
    try:
        merge_color_data(primary_path, secondary_path, output_path)
        messagebox.showinfo("Success", f"Merged EDL saved to:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("EDL Color Data Merger")
frame = tk.Frame(root, padx=20, pady=20)
frame.pack()
label = tk.Label(frame, text="Drag-and-Drop EDL Merger", font=("Arial", 14))
label.pack(pady=10)
button = tk.Button(frame, text="Select EDLs and Merge", command=run_merge, padx=10, pady=5)
button.pack()
root.mainloop()