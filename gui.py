from tkinter import *
from tkinter import filedialog, ttk
from painter import LogoPainter, Corner
import os


class App(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.root = master

        # Logo placed parameters
        self.logo_path = StringVar()
        self.target_path = StringVar()
        self.result_path = StringVar()
        self.target_mode = StringVar()
        self.rewrite = BooleanVar()
        self.logo_resize_rate = DoubleVar()
        self.margin_rate = DoubleVar()
        self.min_logo_size = IntVar()
        self.corner = StringVar()

        self.init_ui()
        self.init_var_listeners()

        # Setting default values
        self.margin_scale.set(1)
        self.logo_resize_scale.set(20)
        self.logo_min_size_scale.set(300)

    def init_ui(self):
        padx = 10
        pady = 10

        self.pack()
        self.root.title('Logo Painter by Innokentiy Min')
        self.width = 800
        self.height = 500
        self.root.geometry('{}x{}'.format(self.width, self.height))
        self.root.resizable(width=False, height=False)

        self.left_half = Frame(self, width=self.width / 2, height=self.height)
        self.left_half.pack(side=LEFT, padx=padx, pady=pady)
        self.left_half.pack_propagate(False)    # Prevent resizing to fit more content
        self.right_half = Frame(self, width=self.width / 2, height=self.height)
        self.right_half.pack(side=RIGHT, padx=padx, pady=pady)
        self.right_half.pack_propagate(False)

        # --- Left half ---

        logo_path_frame = Frame(self.left_half)
        logo_path_frame.pack(anchor=NW, fill=X)
        self.logo_path_text = Text(logo_path_frame, width=40, height=3, highlightbackground='grey', wrap=CHAR)
        self.logo_path_text.insert(0.0, 'Укажите логотип')
        self.logo_path_text.config(state=DISABLED)
        self.logo_path_text.pack(side=LEFT, ipadx=5, ipady=5)
        Button(logo_path_frame, text='Выбрать', command=self.choose_logo).pack(side=RIGHT, anchor=N, padx=10)

        mode_frame = Frame(self.left_half)
        mode_frame.pack(anchor=NW)
        Label(mode_frame, text='Режим: ').pack(side=LEFT)
        file = Radiobutton(mode_frame, text='Фото', variable=self.target_mode, value='file')
        file.select()
        file.pack(side=LEFT)
        directory = Radiobutton(mode_frame, text='Папка', variable=self.target_mode, value='directory')
        directory.deselect()
        directory.pack(side=LEFT)

        target_path_frame = Frame(self.left_half)
        target_path_frame.pack(anchor=NW, fill=X)
        self.target_path_text = Text(target_path_frame, width=40, height=3, highlightbackground='grey', wrap=CHAR)
        self.target_path_text.insert(0.0, 'Укажите путь')
        self.target_path_text.config(state=DISABLED)
        self.target_path_text.pack(side=LEFT)
        Button(target_path_frame, text='Выбрать', command=self.choose_target).pack(side=RIGHT, padx=10)

        Checkbutton(self.left_half, text='Редактировать оригиналы', variable=self.rewrite).pack(anchor=NW)

        self.result_path_frame = Frame(self.left_half)
        self.result_path_frame.pack(anchor=NW, fill=X)
        self.result_path_text = Text(self.result_path_frame, width=40, height=3, highlightbackground='grey', wrap=CHAR)
        self.result_path_text.insert(0.0, 'Укажите папку для сохранения результата')
        self.result_path_text.config(state=DISABLED)
        self.result_path_text.pack(side=LEFT)
        Button(self.result_path_frame, text='Выбрать', command=self.choose_result).pack(side=RIGHT, anchor=N, padx=10)

        Label(self.left_half, text='Отступ (в % от размера изображения)').pack(anchor=NW, pady=pady)
        self.margin_scale = Scale(self.left_half, orient=HORIZONTAL, length=350, variable=self.margin_rate)
        self.margin_scale.pack(anchor=NW)

        Label(self.left_half, text='Размер лого (в % от размера изображения)').pack(anchor=NW, pady=pady)
        self.logo_resize_scale = Scale(self.left_half, orient=HORIZONTAL, length=350, variable=self.logo_resize_rate)
        self.logo_resize_scale.pack(anchor=NW)

        Label(self.left_half, text='Минимальный размер лого в пикселях').pack(anchor=NW, pady=pady)
        self.logo_min_size_scale = Scale(self.left_half, orient=HORIZONTAL, length=350, variable=self.min_logo_size,
              from_=20, to=1000, resolution=5)
        self.logo_min_size_scale.pack(anchor=NW)

        self.message = Label(self.left_half, text='')
        self.message.pack(side=BOTTOM, anchor=NW)

        # --- Right half ---
        Label(self.right_half, text='Выберите угол расположения лого').pack(anchor=NW)
        corner_frame = Frame(self.right_half)
        corner_frame.pack(anchor=NW)
        top_left = Radiobutton(corner_frame, text='Верхний левый', variable=self.corner, value='TOP_LEFT')
        top_left.select()
        top_left.grid(row=0, column=0, sticky='nw')
        top_right = Radiobutton(corner_frame, text='Верхний правый', variable=self.corner, value='TOP_RIGHT')
        top_right.deselect()
        top_right.grid(row=0, column=1, sticky='nw')
        bottom_left = Radiobutton(corner_frame, text='Нижний левый', variable=self.corner, value='BOTTOM_LEFT')
        bottom_left.deselect()
        bottom_left.grid(row=1, column=0, sticky='nw')
        bottom_right = Radiobutton(corner_frame, text='Нижний правый', variable=self.corner, value='BOTTOM_RIGHT')
        bottom_right.deselect()
        bottom_right.grid(row=1, column=1, sticky='nw')

        preview_frame = Frame(self.right_half)
        preview_frame.pack(pady=pady)
        Button(preview_frame, text='<').pack(side=LEFT)
        self.preview_area = Frame(preview_frame, width=280, height=300, bg='grey')
        self.preview_area.pack(side=LEFT, fill=BOTH)
        Button(preview_frame, text='>').pack(side=LEFT)

        self.progress = ttk.Progressbar(self.right_half, orient=HORIZONTAL, length=350, mode='determinate')

        Button(self.right_half, text='Run', width=100, command=self.run_painter).pack(side=BOTTOM)
        Button(self.right_half, text='Preview', width=100).pack(side=BOTTOM)
        self.progress.pack(side=BOTTOM, pady=pady)

    def init_var_listeners(self):
        self.logo_path.trace('w', self.update_logo_path_text)
        self.target_path.trace('w', self.update_target_path_text)
        self.rewrite.trace('w', self.set_result_inputs_state)
        self.result_path.trace('w', self.update_result_path_text)

    def update_logo_path_text(self, _, _0, _1):
        self.logo_path_text.config(state=NORMAL)
        self.logo_path_text.delete(1.0, END)
        self.logo_path_text.insert(END, self.logo_path.get())
        self.logo_path_text.config(state=DISABLED)

    def update_target_path_text(self, _, _0, _1):
        self.target_path_text.config(state=NORMAL)
        self.target_path_text.delete(1.0, END)
        self.target_path_text.insert(END, self.target_path.get())
        self.target_path_text.config(state=DISABLED)

    def update_result_path_text(self, _, _0, _1):
        self.result_path_text.config(state=NORMAL)
        self.result_path_text.delete(1.0, END)
        self.result_path_text.insert(END, self.result_path.get())
        self.result_path_text.config(state=DISABLED)

    def set_result_inputs_state(self, _, _0, _1):
        state = DISABLED if self.rewrite.get() else ACTIVE
        self.set_widget_state(self.result_path_frame, state=state)

    def set_widget_state(self, widget, state='disabled'):
        try:
            widget.configure(state=state)
        except TclError:
            pass
        for child in widget.winfo_children():
            self.set_widget_state(child, state=state)

    def choose_logo(self):
        # Seems not working on Mac OS (at least)
        file_types = [
            ('Изображения', '*.bmp;*.eps;*.gif;*.icns;*.ico;*.im;*.jpeg;*.msp;*.pcx;*.png;*.ppm;*.sgi;*.spider;*.tiff;*.webp;*.xbm'),
            ('Все файлы', '*.*')
        ]
        self.logo_path.set(filedialog.askopenfilename())

    def choose_target(self):
        mode = self.target_mode.get()
        path = filedialog.askopenfilename() if mode == 'file' else filedialog.askdirectory()
        self.target_path.set(path)

    def choose_result(self):
        self.result_path.set(filedialog.askdirectory())

    def run_painter(self):
        logo = self.logo_path.get()
        target = self.target_path.get()
        result_directory = self.target_path.get() if self.rewrite.get() else self.result_path.get()

        # Data pre-processing
        logo_resize_rate = self.logo_resize_rate.get() / 100
        margin_rate = self.margin_rate.get() / 100

        # Data validation
        if logo == '':
            self.message.config(text='Ошибка: не выбран логотип', fg='red')
            return
        elif target == '':
            self.message.config(text='Ошибка: не выбрано(ы) фото', fg='red')
            return
        elif result_directory == '':
            self.message.config(text='Ошибка: не выбрана папка для сохранения результата', fg='red')
            return

        painter = LogoPainter(logo, target, save_to_path=result_directory,
                              logo_resize_rate=logo_resize_rate, margin_rate=margin_rate,
                              corner=Corner.__dict__[self.corner.get()], min_logo_min_dim=self.min_logo_size.get())
        self.message.config(text='Размещаю лого...', fg='green')
        painter.process_all()
        self.message.config(text='Готово!', fg='green')


root = Tk()
root.focus_force()
app = App(master=root)
app.mainloop()
