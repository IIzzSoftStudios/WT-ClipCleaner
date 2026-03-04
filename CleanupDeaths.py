import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime, timedelta
from tkcalendar import DateEntry

class WTCleanerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("War Thunder Clip Purge v1.4")
        self.root.geometry("600x850")

        # UI Elements
        tk.Label(root, text="War Thunder Highlight Cleaner", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Folder Selection
        tk.Label(root, text="Highlights Folder:").pack(anchor="w", padx=20)
        self.default_path = Path.home() / "Videos" / "NVIDIA" / "Highlights" / "War Thunder"
        self.path_var = tk.StringVar(value=str(self.default_path))
        
        folder_frame = tk.Frame(root)
        folder_frame.pack(fill="x", padx=20)
        tk.Entry(folder_frame, textvariable=self.path_var, width=50).pack(side="left", padx=5)
        tk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side="left")

        # --- NEW: CLIP TYPE SELECTION ---
        type_frame = tk.LabelFrame(root, text="Clip Types to Process", padx=10, pady=10)
        type_frame.pack(fill="x", padx=20, pady=10)

        self.type_death = tk.BooleanVar(value=True)
        self.type_kill = tk.BooleanVar(value=False)
        self.type_capture = tk.BooleanVar(value=False)

        tk.Checkbutton(type_frame, text="Moment of death", variable=self.type_death).pack(anchor="w")
        tk.Checkbutton(type_frame, text="Enemy destruction", variable=self.type_kill).pack(anchor="w")
        tk.Checkbutton(type_frame, text="The moment of capture of the zone", variable=self.type_capture).pack(anchor="w")

        # --- CALENDAR DATE RANGE ---
        date_frame = tk.LabelFrame(root, text="Date Range Filter", padx=10, pady=10)
        date_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(date_frame, text="Start Date:").grid(row=0, column=0, sticky="w")
        self.start_cal = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.start_cal.grid(row=0, column=1, padx=10, pady=5)
        self.start_cal.set_date(datetime.now() - timedelta(days=30))

        tk.Label(date_frame, text="End Date:").grid(row=1, column=0, sticky="w")
        self.end_cal = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.end_cal.grid(row=1, column=1, padx=10, pady=5)

        # Threshold Setting
        tk.Label(root, text="Duplicate Sensitivity (Seconds):").pack(anchor="w", padx=20)
        self.threshold_var = tk.IntVar(value=10)
        self.threshold_slider = tk.Scale(root, from_=1, to=30, orient="horizontal", variable=self.threshold_var)
        self.threshold_slider.pack(fill="x", padx=20)

        # --- OPTIONS ---
        options_frame = tk.Frame(root)
        options_frame.pack(pady=10)

        self.dry_run_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Dry Run (Safe Mode)", variable=self.dry_run_var).pack(anchor="w")

        self.delete_all_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="DELETE ALL in range (Ignore Duplicates)", variable=self.delete_all_var, fg="red", command=self.toggle_delete_warning).pack(anchor="w")

        self.warning_label = tk.Label(root, text="⚠ WARNING: ALL SELECTED CLIP TYPES IN RANGE WILL BE DELETED ⚠", fg="red", font=("Arial", 8, "bold"))

        # Log Area
        self.log_area = scrolledtext.ScrolledText(root, height=10, width=70, state='disabled')
        self.log_area.pack(pady=10, padx=10)

        # Action Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        self.run_btn = tk.Button(btn_frame, text="START CLEANUP", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), width=20, command=self.run_cleanup)
        self.run_btn.pack(side="left", padx=5)
        self.reset_btn = tk.Button(btn_frame, text="RESET", bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=10, command=self.reset_defaults)
        self.reset_btn.pack(side="left", padx=5)

    def toggle_delete_warning(self):
        if self.delete_all_var.get():
            self.warning_label.pack(after=self.log_area)
            self.threshold_slider.config(state="disabled", fg="gray")
        else:
            self.warning_label.pack_forget()
            self.threshold_slider.config(state="normal", fg="black")

    def browse_folder(self):
        selected = filedialog.askdirectory()
        if selected: self.path_var.set(selected)

    def reset_defaults(self):
        self.path_var.set(str(self.default_path))
        self.start_cal.set_date(datetime.now() - timedelta(days=30))
        self.end_cal.set_date(datetime.now())
        self.threshold_var.set(10)
        self.dry_run_var.set(True)
        self.delete_all_var.set(False)
        self.type_death.set(True)
        self.type_kill.set(False)
        self.type_capture.set(False)
        self.toggle_delete_warning()
        self.log_area.config(state='normal')
        self.log_area.delete('1.0', tk.END)
        self.log_area.config(state='disabled')

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        self.root.update_idletasks()

    def run_cleanup(self):
        target_dir = Path(self.path_var.get())
        if not target_dir.exists():
            messagebox.showerror("Error", "Folder not found!")
            return

        # Build list of active search terms
        search_terms = []
        if self.type_death.get(): search_terms.append("Moment of death")
        if self.type_kill.get(): search_terms.append("Enemy destruction")
        if self.type_capture.get(): search_terms.append("The moment of capture of the zone")

        if not search_terms:
            messagebox.showwarning("Warning", "Select at least one clip type!")
            return

        start_dt = datetime.combine(self.start_cal.get_date(), datetime.min.time())
        end_dt = datetime.combine(self.end_cal.get_date(), datetime.max.time())
        is_dry_run = self.dry_run_var.get()
        delete_all = self.delete_all_var.get()
        threshold = self.threshold_var.get()
        
        self.log(f"--- Starting Cleanup (Range: {start_dt.date()} to {end_dt.date()}) ---")

        try:
            # Filter by date and by any of the selected search terms
            all_files = [f for f in target_dir.iterdir() if f.is_file() and any(term in f.name for term in search_terms)]
            filtered_files = [f for f in all_files if start_dt <= datetime.fromtimestamp(f.stat().st_ctime) <= end_dt]
            filtered_files.sort(key=lambda x: x.stat().st_ctime)
        except Exception as e:
            self.log(f"Error: {e}"); return

        if not filtered_files:
            self.log("No matching clips found."); return

        if delete_all and not is_dry_run:
            if not messagebox.askyesno("Final Warning", f"Nuke ALL {len(filtered_files)} selected clips?"): return

        last_kept_times = {term: 0 for term in search_terms} # Track separately for each type
        action_count = 0

        for f in filtered_files:
            current_time = f.stat().st_ctime
            # Determine which type this file is
            file_type = next((term for term in search_terms if term in f.name), None)
            
            should_delete = False
            if delete_all:
                should_delete = True
            elif file_type and (current_time - last_kept_times[file_type]) < threshold:
                should_delete = True
            
            if should_delete:
                if is_dry_run: self.log(f"[PREVIEW] {f.name}")
                else:
                    f.unlink()
                    self.log(f"[DELETED] {f.name}")
                action_count += 1
            else:
                self.log(f"[KEEPING] {f.name}")
                if file_type: last_kept_times[file_type] = current_time

        self.log(f"\nFinished. Processed {action_count} files.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WTCleanerGUI(root)
    root.mainloop()