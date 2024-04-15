import tkinter as tk
from tkinter import filedialog, ttk
from pytube import Playlist, YouTube
import threading

class PlaylistDownloader:
    def __init__(self, root):
        self.root = root
        self.download_dir = ""
        self.playlist_link = ""
        self.playlist = None
        self.download_thread = None
        self.downloading = False

        # Plain Background
        self.background = tk.Frame(self.root, bg="#f0f0f0")
        self.background.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Label and Textbox for playlist link
        self.link_label = ttk.Label(self.root, text="Enter YouTube Playlist Link:")
        self.link_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        self.textbox = ttk.Entry(self.root, width=60)
        self.textbox.place(relx=0.5, rely=0.15, anchor=tk.CENTER)

        # Label 'Choose directory'
        self.directory_label = ttk.Label(self.root, text="Choose Directory:")
        self.directory_label.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        # Directory Chooser
        self.directory_button = ttk.Button(self.root, text="Choose", command=self.choose_directory)
        self.directory_button.place(relx=0.5, rely=0.25, anchor=tk.CENTER)

        # Download button
        self.download_button = ttk.Button(self.root, text="Download Playlist", command=self.start_download)
        self.download_button.place(relx=0.4, rely=0.3, anchor=tk.CENTER)

        # Stop button
        self.stop_button = ttk.Button(self.root, text="Stop Download", command=self.stop_download)
        self.stop_button.place(relx=0.6, rely=0.3, anchor=tk.CENTER)

        # Label for selected directory
        self.path_label = ttk.Label(self.root, text="")
        self.path_label.place(relx=0.5, rely=0.35, anchor=tk.CENTER)

        # Create a Frame for the table
        self.table_frame = ttk.Frame(self.root)
        self.table_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER, relwidth=0.8, relheight=0.4)

        # Create Treeview widget for downloaded videos
        self.columns = ("Title", "Complete")
        self.tree = ttk.Treeview(self.table_frame, columns=self.columns, show="headings")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Complete", text="Complete")
        self.tree.pack(side="left", fill="both", expand=True)

        # Add scrollbar
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Make everything resizable
        self.root.bind("<Configure>", self.on_resize)

        # Label for completion status
        self.complete_label = ttk.Label(self.root, text="", font=("Helvetica", 12, "bold"))
        self.complete_label.place(relx=0.5, rely=0.92, anchor=tk.CENTER)

        # Label for download cancelled
        self.cancel_label = ttk.Label(self.root, text="Download Cancelled", foreground="red")
        # self.cancel_label.place(relx=0.5, rely=1.0, anchor=tk.CENTER, y=-20)

    def choose_directory(self):
        directory = filedialog.askdirectory()
        self.download_dir = directory
        self.path_label.config(text="Selected Directory: " + directory)

    def on_resize(self, event):
        self.background.configure(width=event.width, height=event.height)

    def start_download(self):
        self.playlist_link = self.textbox.get()
        self.playlist = Playlist(self.playlist_link)
        # Insert all video titles into the table
        for video_url in self.playlist.video_urls:
            video = YouTube(video_url)
            title = video.title
            self.tree.insert("", tk.END, values=(title, "No"))
        # Start download thread
        self.download_thread = threading.Thread(target=self.download_videos)
        self.download_thread.start()

    def download_videos(self):
        self.downloading = True
        for video_url in self.playlist.video_urls:
            if not self.downloading:
                break
            video = YouTube(video_url)
            title = video.title
            video_stream = video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            video_stream.download(self.download_dir)
            # Mark video as complete in the table
            for child in self.tree.get_children():
                if self.tree.item(child, "values")[0] == title:
                    self.tree.set(child, "Complete", "Yes")
                    break
        self.complete_label.config(text="Complete")

    def stop_download(self):
        self.downloading = False
        self.cancel_label.place(relx=0.5, rely=1.0, anchor=tk.CENTER, y=-20)

# Create the main window
root = tk.Tk()
root.title("Playlist Downloader")
root.geometry("800x600")

app = PlaylistDownloader(root)

root.mainloop()
