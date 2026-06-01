import datetime
import tkinter as tk
from tkinter import colorchooser, messagebox, ttk
import dataset  
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DrawApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Data Draw")
        self.root.geometry("1200x800")

        if not hasattr(dataset, 'df') or dataset.df is None:
            if hasattr(dataset, 'load_data'):
                dataset.load_data()
            else:
                dataset.df = pd.DataFrame(columns=['Нет данных'])

        self.df = dataset.df
        self.all_cols = self.df.columns.tolist()

        self.drawing_mode = False
        self.drawn_lines = []
        self.current_line = None

        self.line_color = (16 / 255, 4 / 255, 34 / 255)
        self.line_width = 8

        self.x_col = self.all_cols[0]
        self.y_col = self.all_cols[0]
        self.current_cmap_name = "PuBu"

        self.setup_ui()
        self.update_plot()

        self.root.bind("<Control-z>", self.undo_last_line)
        self.root.bind("<Control-Z>", self.undo_last_line)

    def setup_ui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.y_frame = tk.Frame(self.main_frame)
        self.y_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        tk.Label(self.y_frame, text="", font=("Arial", 10, "bold")).pack()
        for col in self.all_cols:
            tk.Button(
                self.y_frame,
                text=col,
                width=15,
                command=lambda c=col: self.change_axis(c, "y"),
            ).pack(pady=1)

        self.plot_frame = tk.Frame(self.main_frame)
        self.plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.fig, self.ax = plt.subplots(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_move)
        self.canvas.mpl_connect("button_release_event", self.on_release)

        self.bottom_panel = tk.Frame(self.root)
        self.bottom_panel.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=10)

        draw_tools = tk.Frame(self.bottom_panel)
        draw_tools.pack(side=tk.LEFT, padx=10)

        self.draw_btn = tk.Button(
            draw_tools,
            text="✎ Рисовать",
            width=12,
            relief=tk.RAISED,
            command=self.toggle_draw_mode,
        )
        self.draw_btn.pack(side=tk.LEFT, padx=5)

        tk.Label(draw_tools, text="Цвет:").pack(side=tk.LEFT, padx=2)
        hex_color = "#%02x%02x%02x" % (
            int(self.line_color[0] * 255),
            int(self.line_color[1] * 255),
            int(self.line_color[2] * 255),
        )
        self.color_box = tk.Button(
            draw_tools, bg=hex_color, width=3, command=self.choose_color
        )
        self.color_box.pack(side=tk.LEFT, padx=5)

        tk.Label(draw_tools, text="Толщина:").pack(side=tk.LEFT, padx=2)
        self.width_spin = tk.Spinbox(
            draw_tools, from_=1, to=20, width=5, command=self.update_width
        )
        self.width_spin.delete(0, "end")
        self.width_spin.insert(0, str(self.line_width))
        self.width_spin.pack(side=tk.LEFT, padx=5)

        x_frame = tk.Frame(self.bottom_panel)
        x_frame.pack(side=tk.LEFT, padx=20)
        for col in self.all_cols:
            tk.Button(
                x_frame,
                text=col,
                command=lambda c=col: self.change_axis(c, "x"),
            ).pack(side=tk.LEFT, padx=2)

        self.save_btn = tk.Button(
            self.bottom_panel,
            text="💾 Сохранить",
            bg="#4CAF50",
            fg="white",
            command=self.save_graph,
        )
        self.save_btn.pack(side=tk.RIGHT, padx=10)

    def toggle_draw_mode(self):
        self.drawing_mode = not self.drawing_mode
        if self.drawing_mode:
            self.draw_btn.config(relief=tk.SUNKEN, bg="#ddd")
            self.canvas.get_tk_widget().config(cursor="pencil")
        else:
            self.exit_draw_mode()

    def exit_draw_mode(self):
        self.drawing_mode = False
        self.draw_btn.config(relief=tk.RAISED, bg="SystemButtonFace")
        self.canvas.get_tk_widget().config(cursor="arrow")

    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.color_box["bg"])[0]
        if color:
            self.line_color = (color[0] / 255, color[1] / 255, color[2] / 255)
            self.color_box.config(
                bg="#%02x%02x%02x"
                % (int(color[0]), int(color[1]), int(color[2]))
            )

    def update_width(self):
        self.line_width = int(self.width_spin.get())

    def on_press(self, event):
        if not self.drawing_mode or event.button == 3:
            self.exit_draw_mode()
            return
        if event.inaxes != self.ax:
            return

        (self.current_line,) = self.ax.plot(
            [event.xdata],
            [event.ydata],
            color=self.line_color,
            linewidth=self.line_width,
            solid_capstyle="round",
            solid_joinstyle="round",
        )
        self.canvas.draw_idle()

    def on_move(self, event):
        if (
            not self.drawing_mode
            or event.button != 1
            or event.inaxes != self.ax
        ) or self.current_line is None:
            return

        xdata = list(self.current_line.get_xdata())
        ydata = list(self.current_line.get_ydata())
        xdata.append(event.xdata)
        ydata.append(event.ydata)

        self.current_line.set_data(xdata, ydata)
        self.canvas.draw_idle()

    def on_release(self, event):
        if self.current_line is not None:
            self.drawn_lines.append(self.current_line)
            self.current_line = None

    def undo_last_line(self, event=None):
        if self.drawn_lines:
            line_to_remove = self.drawn_lines.pop()
            line_to_remove.remove()
            self.canvas.draw_idle()

    def change_axis(self, col, axis):
        self.exit_draw_mode()
        if axis == "x":
            self.x_col = col
        else:
            self.y_col = col
        self.drawn_lines = []
        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        self.ax.grid(True)
        x_raw = self.df[self.x_col]
        y_raw = self.df[self.y_col]
        x_s = x_raw.iloc[:, 0] if isinstance(x_raw, pd.DataFrame) else x_raw
        y_s = y_raw.iloc[:, 0] if isinstance(y_raw, pd.DataFrame) else y_raw

        v = x_s.notna() & y_s.notna()
        xv, yv = x_s[v], y_s[v]

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
            self.ax.scatter(xv, yv, marker='*', color='black', edgecolors='orange')

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
        fname = datetime.datetime.now().strftime("plot_%Y%m%d_%H%M%S.png")
        try:
            self.fig.savefig(fname, dpi=300)
            messagebox.showinfo("Успех", f"График успешно сохранен как {fname}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить график: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawApp(root)
    root.mainloop()
