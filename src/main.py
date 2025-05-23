VERSION = "0.1.2"

import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging
from datetime import datetime
import re


class FileRenamerApp:
    def __init__(self, master):
        self.root = master
        self.root.title(f"Unstructured File Renamer v{VERSION}")
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
        input_frame = ttk.LabelFrame(self.root, text="Folder Input")
        input_frame.pack(fill="x", padx=10, pady=10)

        self.input_path_var = tk.StringVar(value=self.input_dir)
        ttk.Entry(input_frame, textvariable=self.input_path_var, width=50).pack(
            side="left", padx=5, pady=5
        )
        ttk.Button(input_frame, text="Pilih", command=self.browse_input).pack(
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
            action_frame, text="Mulai Proses", command=self.start_renaming
        ).pack(side="left", padx=5, pady=5)
        ttk.Button(action_frame, text="Buka File Log", command=self.open_log_file).pack(
            side="left", padx=5, pady=5
        )
        ttk.Button(action_frame, text="Keluar", command=self.root.quit).pack(
            side="right", padx=5, pady=5
        )

        # Show startup status
        self.update_status("Aplikasi dimulai. Direktori yang diperlukan telah dibuat.")
        self.update_status(f"Input: {self.input_dir}")
        self.update_status(f"Output: {self.output_dir}")
        self.update_status(f"Log: {self.log_dir}")

    def browse_input(self):
        dir_path = filedialog.askdirectory(initialdir=self.input_dir)
        if dir_path:
            self.input_path_var.set(dir_path)
            self.update_status(f"Direktori input diubah menjadi: {dir_path}")
            self.update_status("Silakan klik 'Mulai Proses' untuk melanjutkan.")

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
        if os.path.exists(self.log_dir):
            os.startfile(self.log_dir)
        else:
            messagebox.showerror("Error", "Direktori log tidak ditemukan!")

    def has_invalid_folder_names(self, input_path):
        # Check if folders follow the required pattern (2 A-Z chars followed by 15 digits)
        for dir_path, dirs, _ in os.walk(input_path):
            for dir_name in dirs:
                # Skip checking the root input directory itself
                if dir_path == input_path:
                    if not re.match(r'^[A-Z]{2}\d{15}$', dir_name):
                        self.update_status(f"Format nama folder tidak valid: {dir_name}")
                        self.update_status("Nama folder harus 2 huruf kapital diikuti 15 digit angka.")
                        return True
        return False

    def contains_compressed_files(self, input_path):
        # Define compressed file extensions
        compressed_exts = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.cab', '.iso'}
        for _, _, files in os.walk(input_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in compressed_exts:
                    return True
        return False

    def start_renaming(self):
        input_path = self.input_path_var.get()
        if not os.path.isdir(input_path):
            messagebox.showerror("Error", f"Direktori input tidak ditemukan: {input_path}")
            return
        
        # Check if input path contains at least one folder
        folder_count = 0
        for _, dirs, _ in os.walk(input_path):
            folder_count += len(dirs)
            break  # Only check the first level

        if folder_count == 0:
            messagebox.showerror("Error", "Direktori input harus berisi minimal 1 folder!")
            self.update_status("Proses dibatalkan karena direktori input tidak berisi folder.")
            return
            
        # Check for invalid folder names before proceeding
        if self.has_invalid_folder_names(input_path):
            messagebox.showerror(
                "Format Folder Tidak Valid", 
                "Beberapa folder tidak mengikuti format yang diperlukan (2 huruf kapital + 15 digit)."
            )
            self.update_status("Proses dibatalkan karena ada nama folder yang tidak valid.")
            return
        
        # Check for compressed files before proceeding
        if self.contains_compressed_files(input_path):
            proceed = messagebox.askyesno(
                "Konfirmasi",
                "Terdapat file kompresi (zip/rar/lainnya) pada folder input. Yakin akan lanjut?"
            )
            if not proceed:
                self.update_status("Proses dibatalkan oleh pengguna karena ada file kompresi.")
                return

        file_operations = []  # Store operations to be logged

        try:
            self.status_text.delete(1.0, tk.END)
            self.update_status(f"Memulai proses penggantian nama dari: {input_path}")
            self.update_status(f"Hasil akan disimpan di: {self.output_dir}")

            # Count total files for progress bar (all files under all subfolders)
            total_files = 0
            for root_dir, dirs, files in os.walk(input_path):
                # Only count files inside valid folders (not in the root input folder)
                rel_path = os.path.relpath(root_dir, input_path)
                if rel_path == ".":
                    continue
                total_files += len(files)

            if total_files == 0:
                self.update_status("Tidak ada file yang ditemukan untuk diganti namanya.")
                return

            self.update_status(f"Ditemukan {total_files} file untuk diproses.")

            # Clear output directory
            if os.path.exists(self.output_dir):
                shutil.rmtree(self.output_dir)
            os.makedirs(self.output_dir, exist_ok=True)

            files_processed = 0

            # Only process first-level folders in input_path
            for folder_name in os.listdir(input_path):
                folder_path = os.path.join(input_path, folder_name)
                if not os.path.isdir(folder_path):
                    continue
                # Validate folder name
                if not re.match(r'^[A-Z]{2}\d{15}$', folder_name):
                    continue

                self.update_status(f"Processing folder: {folder_path}")

                # Create corresponding output folder
                output_folder = os.path.join(self.output_dir, folder_name)
                os.makedirs(output_folder, exist_ok=True)

                # Collect all files under this folder (recursively)
                all_files = []
                for dirpath, _, files in os.walk(folder_path):
                    for file in files:
                        all_files.append(os.path.join(dirpath, file))

                # Rename and copy files to output_folder, flattening structure
                file_count = 1
                for src_file in all_files:
                    files_processed += 1
                    progress = (files_processed / total_files) * 100
                    self.progress_var.set(progress)

                    file_ext = os.path.splitext(src_file)[1]
                    new_filename = f"{folder_name}{file_count:04d}{file_ext}"
                    dst_file = os.path.join(output_folder, new_filename)

                    shutil.copy2(src_file, dst_file)

                    file_operations.append((folder_path, os.path.relpath(src_file, folder_path), new_filename))
                    self.update_status(f"Mengganti nama: {os.path.relpath(src_file, folder_path)} -> {new_filename}")
                    file_count += 1

            # Only create log file and write entries after successful completion
            self.initialize_log_file()
            for operation in file_operations:
                self.log_file_operation(*operation)

            self.update_status(f"Selesai! {files_processed} file telah diproses.")
            messagebox.showinfo(
                "Sukses",
                f"Berhasil mengganti nama {files_processed} file.\nFile log disimpan di: {self.log_file_path}",
            )

        except (OSError, IOError, shutil.Error) as e:
            error_msg = f"Error selama operasi file: {str(e)}"
            self.update_status(error_msg)
            messagebox.showerror("Error", error_msg)
        except re.error as e:
            error_msg = f"Error pada expresi reguler: {str(e)}"
            self.update_status(error_msg)
            messagebox.showerror("Error", error_msg)
        except Exception as e:
            error_msg = f"Error tidak terduga: {str(e)}"
            self.update_status(error_msg)
            messagebox.showerror("Error", error_msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = FileRenamerApp(root)
    root.mainloop()
