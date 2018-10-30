from tkinter import *
from tkinter import filedialog, ttk
from painter import LogoPainter, Corner
import os
from shutil import rmtree
from PIL import Image, ImageTk


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

        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Init temp dir
        user_home = os.path.expanduser('~')
        self.temp_dir = os.path.join(user_home, 'logo_painter_temp')
        self.init_temp_dir()

        self.reset_defaults()
        # self.init_dbg_input()

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
        self.logo_path_text.pack(side=LEFT)
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
        self.target_path_text.pack(side=LEFT)
        Button(target_path_frame, text='Выбрать', command=self.choose_target).pack(side=RIGHT, padx=10)

        Checkbutton(self.left_half, text='Редактировать оригиналы', variable=self.rewrite).pack(anchor=NW)

        self.result_path_frame = Frame(self.left_half)
        self.result_path_frame.pack(anchor=NW, fill=X)
        self.result_path_text = Text(self.result_path_frame, width=40, height=3, highlightbackground='grey', wrap=CHAR)
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
        self.previous_button = Button(preview_frame, text='<', state=DISABLED, command=self.preview_previous)
        self.previous_button.pack(side=LEFT)
        self.preview_area = Frame(preview_frame, width=280, height=280, bg='grey')
        self.preview_area.pack(side=LEFT, fill=BOTH)
        self.preview_area.pack_propagate(False)
        self.preview_photo_label = Label(self.preview_area)
        self.next_button = Button(preview_frame, text='>', state=DISABLED, command=self.preview_next)
        self.next_button.pack(side=LEFT)

        self.progress = ttk.Progressbar(self.right_half, orient=HORIZONTAL, length=350, mode='determinate')

        Button(self.right_half, text='Запуск', width=100, command=self.run_painter).pack(side=BOTTOM)
        Button(self.right_half, text='Превью', width=100, command=self.preview).pack(side=BOTTOM)
        Button(self.right_half, text='Сбросить', width=100, command=self.reset_defaults).pack(side=BOTTOM)
        self.progress.pack(side=BOTTOM, pady=pady)

    def init_var_listeners(self):
        self.logo_path.trace('w', self.update_logo_path_text)
        self.target_mode.trace('w', self.reset_target_path_text)
        self.target_path.trace('w', self.update_target_path_text)
        self.rewrite.trace('w', self.set_result_inputs_state)
        self.result_path.trace('w', self.update_result_path_text)

    def init_temp_dir(self):
        self.remove_temp_dir()
        os.mkdir(self.temp_dir)

    def remove_temp_dir(self):
        if os.path.exists(self.temp_dir):
            rmtree(self.temp_dir)

    def reset_defaults(self):
        # Setting default values
        self.logo_path.set('')
        self.set_logo_path_text('Укажите логотип')
        
        self.target_mode.set('file')
        
        self.target_path.set('')
        self.set_target_path_text('Укажите файл(ы) для редактирования')

        self.rewrite.set(False)

        self.result_path.set('')
        self.set_result_path_text('Укажите папку для сохранения результата')

        self.margin_scale.set(1)
        self.logo_resize_scale.set(20)
        self.logo_min_size_scale.set(300)

        self.corner.set('TOP_LEFT')

        self.reset_preview()

    def set_logo_path_text(self, text):
        self.logo_path_text.config(state=NORMAL)
        self.logo_path_text.delete(1.0, END)
        self.logo_path_text.insert(END, text)
        self.logo_path_text.config(state=DISABLED)
    
    def set_target_path_text(self, text):
        self.target_path_text.config(state=NORMAL)
        self.target_path_text.delete(1.0, END)
        self.target_path_text.insert(END, text)
        self.target_path_text.config(state=DISABLED)

    def set_result_path_text(self, text):
        self.result_path_text.config(state=NORMAL)
        self.result_path_text.delete(1.0, END)
        self.result_path_text.insert(END, text)
        self.result_path_text.config(state=DISABLED)

    def update_logo_path_text(self, _, _0, _1):
        self.set_logo_path_text(self.logo_path.get())

    def update_target_path_text(self, _, _0, _1):
        self.set_target_path_text(self.target_path.get())
        self.reset_preview()

    def reset_target_path_text(self, _, _0, _1):
        self.target_path.set('')
        self.set_target_path_text('Укажите файл(ы) для редактирования')
        self.reset_preview()
        
    def update_result_path_text(self, _, _0, _1):
        self.set_result_path_text(self.result_path.get())

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

    def get_inputs(self):
        # Keys are parameters to init LogoPainter
        inputs = dict(
            logo_path=self.logo_path.get(),
            target_path=self.target_path.get(),
            save_to_path=self.target_path.get() if self.rewrite.get() else self.result_path.get(),
            logo_resize_rate=self.logo_resize_rate.get() / 100,
            margin_rate=self.margin_rate.get() / 100,
            min_logo_min_dim=self.min_logo_size.get(),
            corner=Corner.__dict__[self.corner.get()]
        )
        return inputs

    def validate_inputs(self, inputs):
        if inputs['logo_path'] == '':
            self.message.config(text='Ошибка: не выбран логотип', fg='red')
            return False
        elif inputs['target_path'] == '':
            self.message.config(text='Ошибка: не выбрано(ы) фото', fg='red')
            return False
        elif inputs['save_to_path'] == '':
            self.message.config(text='Ошибка: не выбрана папка для сохранения результата', fg='red')
            return False
        return True

    def paint_temp_img(self, image_path):
        inputs = self.get_inputs()
        inputs['target_path'] = image_path
        inputs['save_to_path'] = self.temp_dir

        if not self.validate_inputs(inputs):
            return False

        LogoPainter(**inputs).process_all()
        return True

    def preview(self):

        # if len(self.preview_list) == 0:
        if self.target_mode.get() == 'file':
            self.preview_list.append(self.target_path.get())
        else:   # self.target_mode.get() == 'directory'
            target = self.target_path.get()
            self.preview_list = [os.path.join(target, name) for name in os.listdir(target)]

            # Enable arrows to switch preview image
            self.set_arrows_state(ACTIVE)

        # if self.current_preview_position is None:
        self.current_preview_position = 0

        temp_target = self.preview_list[self.current_preview_position]

        res = self.paint_temp_img(temp_target)
        if not res:
            return

        result_image_path = os.path.join(self.temp_dir, os.path.basename(temp_target))
        self.display_preview(result_image_path)

    def display_preview(self, image_path):
        if self.preview_displayed:
            self.preview_photo_label.pack_forget()
            self.preview_displayed = False

        image = Image.open(image_path)

        image = image.resize(self.get_normalized_preview_size(image.width, image.height))
        photo = ImageTk.PhotoImage(image)

        self.preview_photo_label = Label(self.preview_area, image=photo)
        self.preview_photo_label.image = photo  # keep a reference!
        self.preview_photo_label.pack()
        self.preview_displayed = True

    def preview_previous(self):
        self.current_preview_position = (self.current_preview_position + 1) % len(self.preview_list)
        temp_target = self.preview_list[self.current_preview_position]

        res = self.paint_temp_img(temp_target)
        if not res:
            return

        result_image_path = os.path.join(self.temp_dir, os.path.basename(temp_target))
        self.display_preview(result_image_path)

    def preview_next(self):
        self.current_preview_position = (self.current_preview_position - 1) % len(self.preview_list)
        temp_target = self.preview_list[self.current_preview_position]

        res = self.paint_temp_img(temp_target)
        if not res:
            return

        result_image_path = os.path.join(self.temp_dir, os.path.basename(temp_target))
        self.display_preview(result_image_path)

    def get_normalized_preview_size(self, width, height):
        preview_width = self.preview_area.winfo_width()
        preview_height = self.preview_area.winfo_height()
        if width > height:
            k = preview_width / width
            return preview_width - 1, int(height * k) - 1
        else:
            k = preview_height / height
            return int(width * k) - 1, preview_height - 1

    def run_painter(self):
        inputs = self.get_inputs()
        if not self.validate_inputs(inputs):
            return

        painter = LogoPainter(**inputs)

        self.message.config(text='Размещаю лого...', fg='green')
        painter.process_all()
        self.message.config(text='Готово!', fg='green')

    def reset_preview(self):
        self.preview_photo_label.pack_forget()
        self.set_arrows_state(DISABLED)
        self.preview_list = []
        self.current_preview_position = None
        self.preview_displayed = False
        self.init_temp_dir()    # clean up temp dir

    def set_arrows_state(self, state):
        self.next_button.config(state=state)
        self.previous_button.config(state=state)

    def init_dbg_input(self):
        self.logo_path.set('/Users/innokentijmin/PycharmProjects/logo_painter/samples/logo.png')
        self.target_mode.set('directory')
        self.target_path.set('/Users/innokentijmin/PycharmProjects/logo_painter/samples/pics/caucasian')
        self.result_path.set('/Users/innokentijmin/Downloads')

    def on_close(self):
        self.remove_temp_dir()
        self.root.destroy()

root = Tk()
root.focus_force()
app = App(master=root)
root.protocol("WM_DELETE_WINDOW", app.on_close)

app.mainloop()
