import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from report_maker import LibraryChecker


class LibraryCheckerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Library Version Checker")

        self.mode_label = ttk.Label(self.master, text="Выбор режима:")
        self.mode_label.grid(row=0, column=0, padx=5, pady=5)

        self.mode_var = tk.StringVar()
        self.mode_combobox = ttk.Combobox(self.master, textvariable=self.mode_var, state="readonly")
        self.mode_combobox["values"] = (
            "1.Отчет на основе лога",
            "2.Проверить конкретные библиотеки",
            "3.Найти библиотеки с версией до указанной даты",
        )
        self.mode_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.mode_combobox.current(0)

        self.input_label = ttk.Label(self.master, text="Файл лога:")
        self.input_label.grid(row=1, column=0, padx=5, pady=5)

        self.input_text = ttk.Entry(self.master, width=50)
        self.input_text.grid(row=1, column=1, padx=5, pady=5)

        self.browse_button = ttk.Button(self.master, text="Открыть", command=self.browse_file)
        self.browse_button.grid(row=1, column=2, padx=5, pady=5)

        self.input_data_label = ttk.Label(self.master, text="Входные данные:")
        self.input_data_label.grid(row=2, column=0, padx=5, pady=5)

        self.input_data_text = ttk.Entry(self.master, width=50)
        self.input_data_text.grid(row=2, column=1, padx=5, pady=5)

        self.make_report_button = ttk.Button(self.master, text="Создать отчет", command=self.make_report)
        self.make_report_button.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        self.output_label = ttk.Label(self.master, text="Отчет:")
        self.output_label.grid(row=5, column=0, padx=5, pady=5)

        self.output_text = tk.Text(self.master, height=10, width=80)
        self.output_text.grid(row=5, column=1, columnspan=1, padx=3, pady=1)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        self.input_text.delete(0, tk.END)
        self.input_text.insert(0, file_path)

    def make_report(self):
        self.output_text.delete("1.0", tk.END)

        mode = self.mode_var.get().split(".")[0]
        input_file = self.input_text.get()
        if len(input_file) == 0:
            tk.messagebox.Message(self.master, message="Не добавлен файл!").show()
            return
        input_data = self.input_data_text.get()
        if mode == "1":
            checker = LibraryChecker(input_file, "./report.txt", mode)
        elif mode == "2":
            if len(input_data) == 0:
                tk.messagebox.Message(self.master, message="Не указаны библиотеки для поиска!").show()
                return
            checker = LibraryChecker(input_file, "./report.txt", mode, search_libs=input_data)
        elif mode == "3":
            if len(input_data) == 0:
                tk.messagebox.Message(self.master, message="Не указаны даты для поиска!").show()
                return
            checker = LibraryChecker(input_file, "./report.txt", mode, report_date=input_data)
        status = checker.run()
        if not status:
            tk.messagebox.Message(self.master, message="Нет подключения к интернету!").show()
            return
        with open("./report.txt", "r") as f:
            report = f.read()

        self.output_text.insert(tk.END, report)


root = tk.Tk()
app = LibraryCheckerGUI(root)
root.mainloop()
