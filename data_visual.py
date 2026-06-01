import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import numpy as np
import pandas as pd
import dataset


class VisualApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data visual")
        self.root.geometry("1200x900")

        if not hasattr(dataset, 'df') or dataset.df is None:
            if hasattr(dataset, 'load_data'):
                dataset.load_data()
            else:
                dataset.df = pd.DataFrame()

        self.df = dataset.df

        if self.df.empty:
            messagebox.showerror("Ошибка", "Датасет пуст или файл 'dataset.csv' не найден!")
            self.root.destroy()
            return

        self.all_cols = self.df.columns.tolist()

        self.cmaps = [
            'Accent', 'Blues', 'BrBG', 'BuGn', 'BuPu', 'Dark2', 'GnBu',
            'Greens', 'Greys', 'OrRd', 'Oranges', 'PRGn', 'Paired', 'Pastel1',
            'Pastel2', 'PiYG', 'PuBu', 'PuBuGn', 'PuOr', 'PuRd', 'Purples',
            'RdBu', 'RdGy', 'RdPu', 'RdYlBu', 'RdYlGn', 'Reds', 'Set1'
        ]

        self.x_col = self.all_cols[0]
        self.y_col = self.all_cols[0]
        self.current_cmap_name = 'PuBu'

        self.setup_ui()
        self.update_plot()

    def setup_ui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.y_frame = tk.Frame(self.main_frame)
        self.y_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        tk.Label(self.y_frame, text="", font=('Arial', 10, 'bold')).pack(pady=5)

        canvas_y = tk.Canvas(self.y_frame, width=160)
        scrollbar_y = tk.Scrollbar(self.y_frame, orient="vertical", command=canvas_y.yview)
        self.scroll_frame_y = tk.Frame(canvas_y)
        self.scroll_frame_y.bind("<Configure>", lambda e: canvas_y.configure(scrollregion=canvas_y.bbox("all")))
        canvas_y.create_window((0, 0), window=self.scroll_frame_y, anchor="nw")
        canvas_y.configure(yscrollcommand=scrollbar_y.set)
        canvas_y.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.y_buttons = []
        for col in self.all_cols:
            btn = tk.Button(self.scroll_frame_y, text=col, width=18,
                            command=lambda c=col: self.set_axis(c, 'y'))
            btn.pack(pady=1)
            self.y_buttons.append((col, btn))

        self.plot_frame = tk.Frame(self.main_frame)
        self.plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.fig, self.ax = plt.subplots(figsize=(9, 7), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.bottom_panel = tk.Frame(self.root)
        self.bottom_panel.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=10)

        x_btns_container = tk.Frame(self.bottom_panel)
        x_btns_container.pack(side=tk.TOP, fill=tk.X, pady=5)
        tk.Label(x_btns_container, text="", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        self.x_buttons = []
        for col in self.all_cols:
            btn = tk.Button(x_btns_container, text=col, command=lambda c=col: self.set_axis(c, 'x'))
            btn.pack(side=tk.LEFT, padx=2)
            self.x_buttons.append((col, btn))

        ctrl_frame = tk.Frame(self.bottom_panel)
        ctrl_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        self.cmap_var = tk.StringVar(value=self.current_cmap_name)
        ttk.OptionMenu(ctrl_frame, self.cmap_var, self.current_cmap_name, *self.cmaps, command=self.change_cmap).pack(
            side=tk.LEFT, padx=10)
        tk.Button(ctrl_frame, text="Сохранить график", bg="#2E7D32", fg="white", command=self.save_graph).pack(
            side=tk.RIGHT, padx=20)

    def set_axis(self, col_name, axis):
        if axis == 'x':
            self.x_col = col_name
        else:
            self.y_col = col_name
        self.update_plot()

    def change_cmap(self, val):
        self.current_cmap_name = val
        self.update_plot()

    def update_plot(self):
        if hasattr(self, 'x_buttons') and hasattr(self, 'y_buttons'):
            for col, btn in self.x_buttons:
                btn.config(bg="lightblue" if col == self.x_col else "SystemButtonFace")
            for col, btn in self.y_buttons:
                btn.config(bg="lightblue" if col == self.y_col else "SystemButtonFace")

        self.ax.clear()
        self.ax.grid(True)

        x_raw = self.df[self.x_col]
        y_raw = self.df[self.y_col]

        x_series = x_raw.iloc[:, 0] if isinstance(x_raw, pd.DataFrame) else x_raw
        y_series = y_raw.iloc[:, 0] if isinstance(y_raw, pd.DataFrame) else y_raw

        valid_idx = x_series.notna() & y_series.notna()
        xv = x_series[valid_idx]
        yv = y_series[valid_idx]

        if xv.empty:
            self.ax.text(0.5, 0.5, "Нет данных", ha='center')
            self.canvas.draw()
            return

        is_x_num = pd.api.types.is_numeric_dtype(xv)
        is_y_num = pd.api.types.is_numeric_dtype(yv)
        color = plt.get_cmap(self.current_cmap_name)(0.6)

        is_pie_chart = False

        if self.x_col == self.y_col:
            if is_x_num:
                self.ax.hist(xv, color=color, edgecolor='black')
            else:
                is_pie_chart = True
                c = xv.value_counts().head(10)
                pie_colors = plt.get_cmap(self.current_cmap_name)(np.linspace(0.3, 0.8, len(c)))
                self.ax.pie(c, labels=[str(i) for i in c.index], autopct='%1.1f%%', colors=pie_colors)
        elif not is_y_num and is_x_num:
            cats = yv.value_counts().head(10).index
            self.ax.boxplot([xv[yv == c] for c in cats], tick_labels=[str(c) for c in cats], vert=False)
        elif not is_x_num and is_y_num:
            m = yv.groupby(xv).mean().sort_values(ascending=False).head(15)
            self.ax.bar([str(i) for i in m.index], m.values, color=color)
        else:
            self.ax.scatter(xv, yv, marker='*', color=color)

        if is_pie_chart:
            self.ax.set_xlabel("")
            self.ax.set_ylabel("")
            self.ax.set_title(self.x_col, fontsize=12, fontweight='bold', pad=20)
        else:
            self.ax.set_title("")
            self.ax.set_xlabel(self.x_col)
            self.ax.set_ylabel(self.y_col)

        self.fig.tight_layout()
        self.canvas.draw()

    def save_graph(self):
        fname = datetime.datetime.now().strftime("graph%H_%M_%S.png")
        try:
            self.fig.savefig(fname, bbox_inches='tight', dpi=150)
            messagebox.showinfo("Спасибо", f"Файл {fname} сохранен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить график: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = VisualApp(root)
    root.mainloop()
