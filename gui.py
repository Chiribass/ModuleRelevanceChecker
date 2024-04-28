import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from report_maker import LibraryChecker


class LibraryCheckerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Library Version Checker")

        # Create the input fields
        self.mode_label = ttk.Label(master, text="Choose mode:")
        self.mode_label.grid(row=0, column=0, padx=5, pady=5)

        self.mode_var = tk.StringVar()
        self.mode_combobox = ttk.Combobox(master, textvariable=self.mode_var, state="readonly")
        self.mode_combobox["values"] = (
            "1. Generate report for the entire log",
            "2. Check specific libraries",
            "3. Find libraries with versions before a certain date",
        )
        self.mode_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.mode_combobox.current(0)

        self.input_label = ttk.Label(master, text="Input Log File:")
        self.input_label.grid(row=1, column=0, padx=5, pady=5)

        self.input_text = ttk.Entry(master, width=50)
        self.input_text.grid(row=1, column=1, padx=5, pady=5)

        self.browse_button = ttk.Button(master, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=1, column=2, padx=5, pady=5)

        self.input_data_label = ttk.Label(master, text="Input Data:")
        self.input_data_label.grid(row=2, column=0, padx=5, pady=5)

        self.input_data_text = ttk.Entry(master, width=50)
        self.input_data_text.grid(row=2, column=1, padx=5, pady=5)

        self.make_report_button = ttk.Button(master, text="Make Report", command=self.make_report)
        self.make_report_button.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        self.output_label = ttk.Label(master, text="Output:")
        self.output_label.grid(row=4, column=0, padx=5, pady=5)

        self.output_text = tk.Text(master, height=10, width=80)
        self.output_text.grid(row=4, column=1, columnspan=2, padx=5, pady=5)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        self.input_text.delete(0, tk.END)
        self.input_text.insert(0, file_path)

    def make_report(self):
        mode = self.mode_var.get().split(".")[0]
        input_file = self.input_text.get()
        input_data = self.input_data_text.get()

        if mode == "3":
            checker = LibraryChecker(input_file, "./report.txt", mode, input_data)
        else:
            checker = LibraryChecker(input_file, "./report.txt", mode)

        checker.run()

        with open("./report.txt", "r") as f:
            report = f.read()

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, report)


root = tk.Tk()
app = LibraryCheckerGUI(root)
root.mainloop()
