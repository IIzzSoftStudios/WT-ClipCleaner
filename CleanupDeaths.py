import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime, timedelta
from tkcalendar import DateEntry

class WTCleanerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("War Thunder Clip Purge v1.3")
        self.root.geometry("600x800")

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

        # --- CALENDAR DATE RANGE ---
        date_frame = tk.LabelFrame(root, text="Date Range Filter", padx=10, pady=10)
        date_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(date_frame, text="Start Date:").grid(row=0, column=0, sticky="w")
        self.start_cal = DateEntry(date_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.start_cal.grid(row=0, column=1, padx=10, pady=5)
        self.start_cal.set_date(datetime.now() - timedelta(days=30))

        tk.Label(date_frame, text="End Date:").grid(row=1, column=0, sticky="w")
        self.end_cal = DateEntry(date_frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
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
        tk.Checkbutton(options_frame, text="DELETE ALL clips in range (Ignore Duplicates)", 
                       variable=self.delete_all_var, fg="red", command=self.toggle_delete_warning).pack(anchor="w")

        self.warning_label = tk.Label(root, text="⚠ WARNING: ALL CLIPS IN RANGE WILL BE PERMANENTLY DELETED ⚠", 
                                      fg="red", font=("Arial", 8, "bold"))
        # Hidden by default

        # Log Area
        self.log_area = scrolledtext.ScrolledText(root, height=12, width=70, state='disabled')
        self.log_area.pack(pady=10, padx=10)

        # Action Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.run_btn = tk.Button(btn_frame, text="START CLEANUP", bg="#2ecc71", fg="white", 
                                 font=("Arial", 10, "bold"), width=20, command=self.run_cleanup)
        self.run_btn.pack(side="left", padx=5)

        self.reset_btn = tk.Button(btn_frame, text="RESET", bg="#e74c3c", fg="white", 
                                   font=("Arial", 10, "bold"), width=10, command=self.reset_defaults)
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
        if selected:
            self.path_var.set(selected)

    def reset_defaults(self):
        self.path_var.set(str(self.default_path))
        self.start_cal.set_date(datetime.now() - timedelta(days=30))
        self.end_cal.set_date(datetime.now())
        self.threshold_var.set(10)
        self.dry_run_var.set(True)
        self.delete_all_var.set(False)
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
            messagebox.showerror("Error", f"Folder not found:\n{target_dir}")
            return

        start_dt = datetime.combine(self.start_cal.get_date(), datetime.min.time())
        end_dt = datetime.combine(self.end_cal.get_date(), datetime.max.time())
        is_dry_run = self.dry_run_var.get()
        delete_all = self.delete_all_var.get()
        threshold = self.threshold_var.get()
        
        mode_text = "DELETE ALL" if delete_all else "CLEAN DUPLICATES"
        self.log(f"--- Starting {mode_text} ({'DRY RUN' if is_dry_run else 'LIVE'}) ---")
        
        try:
            # We filter for files with "Moment of death" as per your original request
            all_files = [f for f in target_dir.iterdir() if f.is_file() and "Moment of death" in f.name]
            filtered_files = [f for f in all_files if start_dt <= datetime.fromtimestamp(f.stat().st_ctime) <= end_dt]
            filtered_files.sort(key=lambda x: x.stat().st_ctime)
        except Exception as e:
            self.log(f"Error: {e}")
            return

        if not filtered_files:
            self.log("No clips found in this range.")
            return

        # Confirmation for Live Delete All
        if delete_all and not is_dry_run:
            confirm = messagebox.askyesno("Final Warning", f"You are about to delete ALL {len(filtered_files)} clips in this range. Continue?")
            if not confirm:
                self.log("Operation cancelled by user.")
                return

        last_kept_time = 0
        action_count = 0

        for f in filtered_files:
            current_time = f.stat().st_ctime
            
            # Logic: If delete_all is true, we flag it. 
            # Otherwise, we only flag it if it's within the threshold of the last kept file.
            should_delete = False
            if delete_all:
                should_delete = True
            elif (current_time - last_kept_time) < threshold:
                should_delete = True
            
            if should_delete:
                if is_dry_run:
                    self.log(f"[PREVIEW] Would delete: {f.name}")
                else:
                    try:
                        f.unlink()
                        self.log(f"[DELETED] {f.name}")
                    except Exception as e:
                        self.log(f"[ERR] {f.name}: {e}")
                action_count += 1
            else:
                self.log(f"[KEEPING] {f.name}")
                last_kept_time = current_time

        self.log(f"\nDone. {mode_text} complete.")
        self.log(f"{'Identified' if is_dry_run else 'Removed'} {action_count} clips.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WTCleanerGUI(root)
    root.mainloop()