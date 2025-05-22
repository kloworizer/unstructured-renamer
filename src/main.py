import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging
from datetime import datetime
import re


class FileRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Renamer Tool")
        self.root.geometry("600x400")

        # Set up directories
        self.base_dir = (
            os.getcwd()
        )  # Use current working directory instead of script location
        self.log_dir = os.path.join(self.base_dir, "logs")
        self.input_dir = os.path.join(self.base_dir, "input")
        self.output_dir = os.path.join(self.base_dir, "output")

        # Create all necessary directories at startup
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        # Log file will be created when needed
        self.log_file_path = None

        self.setup_ui()

    def setup_ui(self):
        # Input folder selection
        input_frame = ttk.LabelFrame(self.root, text="Input Folder")
        input_frame.pack(fill="x", padx=10, pady=10)

        self.input_path_var = tk.StringVar(value=self.input_dir)
        ttk.Entry(input_frame, textvariable=self.input_path_var, width=50).pack(
            side="left", padx=5, pady=5
        )
        ttk.Button(input_frame, text="Browse", command=self.browse_input).pack(
            side="left", padx=5, pady=5
        )

        # Status and progress
        status_frame = ttk.LabelFrame(self.root, text="Status")
        status_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.status_text = tk.Text(status_frame, height=15, width=60, wrap="word")
        self.status_text.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(self.status_text, command=self.status_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.status_text.config(yscrollcommand=scrollbar.set)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            status_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill="x", padx=5, pady=5)

        # Actions
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(
            action_frame, text="Start Renaming", command=self.start_renaming
        ).pack(side="left", padx=5, pady=5)
        ttk.Button(action_frame, text="Open Log File", command=self.open_log_file).pack(
            side="left", padx=5, pady=5
        )
        ttk.Button(action_frame, text="Exit", command=self.root.quit).pack(
            side="right", padx=5, pady=5
        )

        # Show startup status
        self.update_status(f"Application started. Created required directories:")
        self.update_status(f"Input: {self.input_dir}")
        self.update_status(f"Output: {self.output_dir}")
        self.update_status(f"Logs: {self.log_dir}")

    def browse_input(self):
        dir_path = filedialog.askdirectory(initialdir=self.input_dir)
        if dir_path:
            self.input_path_var.set(dir_path)

    def update_status(self, message):
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()

    def initialize_log_file(self):
        # Create log file only when needed
        self.log_file_path = os.path.join(
            self.log_dir, f"rename_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        # Set up CSV header format
        logging.basicConfig(
            filename=self.log_file_path,
            level=logging.INFO,
            format="%(message)s",
            force=True,
        )
        # Write CSV header
        logging.info("folder;original_filename;destination_filename")
        return self.log_file_path

    def log_file_operation(self, folder, original_filename, destination_filename):
        log_message = f"{folder};{original_filename};{destination_filename}"
        logging.info(log_message)

    def open_log_file(self):
        if self.log_file_path and os.path.exists(self.log_file_path):
            os.startfile(self.log_file_path)
        else:
            messagebox.showerror("Error", "No log file has been created yet!")

    def contains_compressed_files(self, input_path):
        # Define compressed file extensions
        compressed_exts = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.cab', '.iso'}
        for root, _, files in os.walk(input_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in compressed_exts:
                    return True
        return False

    def start_renaming(self):
        input_path = self.input_path_var.get()
        if not os.path.isdir(input_path):
            messagebox.showerror("Error", f"Input directory not found: {input_path}")
            return

        # Check for compressed files before proceeding
        if self.contains_compressed_files(input_path):
            proceed = messagebox.askyesno(
                "Konfirmasi",
                "Terdapat file kompresi (zip/rar/lainnya) pada folder input. yakin akan lanjut?"
            )
            if not proceed:
                self.update_status("Proses dibatalkan oleh pengguna karena ada file kompresi.")
                return

        # Don't initialize log file yet - only if successful
        file_operations = []  # Store operations to be logged

        try:
            self.status_text.delete(1.0, tk.END)
            self.update_status(f"Starting rename process from: {input_path}")
            self.update_status(f"Results will be in: {self.output_dir}")

            # Count total files for progress bar
            total_files = 0
            for root, _, files in os.walk(input_path):
                total_files += len(files)

            if total_files == 0:
                self.update_status("No files found to rename.")
                return

            self.update_status(f"Found {total_files} files to process.")

            # Clear output directory
            if os.path.exists(self.output_dir):
                shutil.rmtree(self.output_dir)
            os.makedirs(self.output_dir, exist_ok=True)

            files_processed = 0
            for root, dirs, files in os.walk(input_path):
                # Get relative path from input directory
                rel_path = os.path.relpath(root, input_path)
                if rel_path == ".":
                    continue  # Skip the root input directory itself

                # Create corresponding directory in output
                output_folder = os.path.join(self.output_dir, rel_path)
                os.makedirs(output_folder, exist_ok=True)

                # Get ticket number from folder name (assumed to be the last part of folder name)
                ticket_match = re.search(r"[A-Za-z0-9]+$", os.path.basename(root))
                if ticket_match:
                    ticket_num = ticket_match.group(0)
                else:
                    ticket_num = os.path.basename(root)  # Use folder name as is

                # Process files in current directory
                file_count = 1
                for file in files:
                    # Update progress
                    files_processed += 1
                    progress = (files_processed / total_files) * 100
                    self.progress_var.set(progress)

                    src_file = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1]
                    new_filename = f"{ticket_num}{file_count:03d}{file_ext}"
                    dst_file = os.path.join(output_folder, new_filename)

                    # Copy file with new name to output location
                    shutil.copy2(src_file, dst_file)

                    # Store the operation for logging
                    file_operations.append((rel_path, file, new_filename))
                    self.update_status(f"Renamed: {file} -> {new_filename}")
                    file_count += 1

            # Only create log file and write entries after successful completion
            self.initialize_log_file()
            for operation in file_operations:
                self.log_file_operation(*operation)

            self.update_status(f"Complete! {files_processed} files processed.")
            messagebox.showinfo(
                "Success",
                f"Renamed {files_processed} files successfully.\nLog file saved to: {self.log_file_path}",
            )

        except Exception as e:
            error_msg = f"Error during renaming: {str(e)}"
            self.update_status(error_msg)
            messagebox.showerror("Error", error_msg)
            # No log file is created when there's an error


if __name__ == "__main__":
    root = tk.Tk()
    app = FileRenamerApp(root)
    root.mainloop()
