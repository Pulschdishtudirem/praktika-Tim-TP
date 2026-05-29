import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import dataset

class ScatterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Scatter")

        self.df = dataset.df
        self.cols = self.df.select_dtypes(include=['number']).columns.tolist()

        if len(self.cols) < 1:
            messagebox.showerror("Ошибка", "В датасете нет числовых колонок!")
            self.root.destroy()
            return

        self.current_x_idx = 0
        self.current_y_idx = 1 if len(self.cols) > 1 else 0

        self.setup_ui()
        self.update_plot()

    def setup_ui(self):

        self.y_frame = ttk.Frame(self.root, padding=5)
        self.y_frame.grid(row=0, column=0, sticky="ns")
        ttk.Label(self.y_frame, text="", font=('Arial', 10, 'bold')).pack()

        self.y_buttons = []
        for i, col_name in enumerate(self.cols):
            btn = tk.Button(self.y_frame, text=col_name, width=15,
                            command=lambda idx=i: self.set_axis('y', idx))
            btn.pack(pady=2, fill=tk.X)
            self.y_buttons.append(btn)

        self.plot_frame = ttk.Frame(self.root, padding=5)
        self.plot_frame.grid(row=0, column=1, sticky="nsew")

        self.x_frame = ttk.Frame(self.root, padding=5)
        self.x_frame.grid(row=1, column=1, sticky="ew")
        ttk.Label(self.x_frame, text="", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

        self.x_buttons = []
        for i, col_name in enumerate(self.cols):
            btn = tk.Button(self.x_frame, text=col_name,
                            command=lambda idx=i: self.set_axis('x', idx))
            btn.pack(side=tk.LEFT, padx=2)
            self.x_buttons.append(btn)

        self.save_btn = ttk.Button(self.root, text="Сохранить график", command=self.save_plot)
        self.save_btn.grid(row=2, column=1, pady=10)

        self.canvas = None
        self.fig = None

    def set_axis(self, axis, index):
        if axis == 'x':
            self.current_x_idx = index
        else:
            self.current_y_idx = index
        self.update_plot()

    def update_plot(self):
        for i, btn in enumerate(self.x_buttons):
            btn.config(bg="lightblue" if i == self.current_x_idx else "SystemButtonFace")
        for i, btn in enumerate(self.y_buttons):
            btn.config(bg="lightblue" if i == self.current_y_idx else "SystemButtonFace")

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        x_label = self.cols[self.current_x_idx]
        y_label = self.cols[self.current_y_idx]

        self.fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(self.df[x_label], self.df[y_label], marker='*', color='black', edgecolors='orange')

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(f"Диаграмма: {y_label} и {x_label}")
        ax.grid(True, linestyle='--', alpha=0.6)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def save_plot(self):
        now = datetime.now()
        filename = now.strftime("graph%H_%M_%S.png")

        try:
            self.fig.savefig(filename)
            messagebox.showinfo("Сохранение", f"Файл {filename} успешно сохранен!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScatterApp(root)
    root.mainloop()