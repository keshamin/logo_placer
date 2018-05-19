from PIL import Image
import os
import time


class Corner:
    TOP_LEFT = 11
    TOP_RIGHT = 12
    BOTTOM_LEFT = 21
    BOTTOM_RIGHT = 22


class LogoPainter(object):
    def __init__(self,
                 logo_path,
                 target_path,  # Path to a certain image OR to a directory with images
                 save_to_path='result',
                 logo_resize_rate=0.2,  # logo_min_dimension / img_min_dimension
                 margin_rate=0.01,  # margin_size / img_min_dimension
                 min_logo_min_dim=300,  # px, minimum size of logo min_dimension
                 corner=Corner.BOTTOM_RIGHT):

        self.init_time = time.time()

        # Input paths to abs:
        logo_path = os.path.abspath(logo_path)
        target_path = os.path.abspath(target_path)
        save_to_path = os.path.abspath(save_to_path)

        # Painting parameters
        self.logo_resize_rate = logo_resize_rate
        self.margin_rate = margin_rate
        self.corner_left = True if corner in (Corner.TOP_LEFT, Corner.BOTTOM_LEFT) else False
        self.corner_top = True if corner in (Corner.TOP_LEFT, Corner.TOP_RIGHT) else False
        self.min_logo_min_dim = min_logo_min_dim

        if not os.path.isdir(save_to_path):
            os.makedirs(save_to_path)
        self.save_to_path = save_to_path

        self.logo = Image.open(logo_path)

        to_open = []
        if os.path.isfile(target_path):
            to_open.append(target_path)
            self.parent_dir = os.path.dirname(target_path)
        elif os.path.isdir(target_path):
            to_open += self.get_all_dir_files(target_path)
            self.parent_dir = target_path

        validation_start_time = time.time()
        valid_image_paths = []
        for file in to_open:
            try:
                Image.open(file)
                valid_image_paths.append(file)
            except Exception:
                print('Unsupported file format: {}'.format(file))
        print('Checked {0} file(s) in {1:.3f}s'.format(len(to_open), time.time() - validation_start_time))

        self.images = (Image.open(path) for path in valid_image_paths)
        self.current_image = None

    def resize_img_if_needed(self, img):
        img_min_dim = min(img.width, img.height)

        k = img_min_dim * self.logo_resize_rate / self.min_logo_min_dim
        if k < 1:
            img_resize_rate = 1 / k
            new_width = int(img.width * img_resize_rate)
            new_height = int(img.height * img_resize_rate)
            img = img.resize((new_width, new_height))
        return img

    def get_resized_logo(self, img_min_dim):
        logo = self.logo
        logo_min_dim = min(logo.width, logo.height)

        related_resize_rate = img_min_dim * self.logo_resize_rate / logo_min_dim
        new_width = int(logo.width * related_resize_rate)
        new_height = int(logo.height * related_resize_rate)

        return logo.resize((new_width, new_height))

    def paint_logo(self, img):
        # Image and logo resizes if needed
        img = self.resize_img_if_needed(img)
        img_min_dim = min(img.width, img.height)
        logo = self.get_resized_logo(img_min_dim)

        # Coordinates calculation
        x, y = self.calculate_x_y(img, logo)

        # Painting
        img.paste(logo, (x, y), logo)
        return img

    def calculate_x_y(self, img, logo):
        img_min_dim = min(img.width, img.height)
        if self.corner_left:
            x_pos = int(img_min_dim * self.margin_rate)
        else:
            x_pos = int(img.width - logo.width - img_min_dim * self.margin_rate)

        if self.corner_top:
            y_pos = int(img_min_dim * self.margin_rate)
        else:
            y_pos = int(img.height - logo.height - img_min_dim * self.margin_rate)
        return x_pos, y_pos

    def save_painted(self, img):
        relative_path = os.path.relpath(self.current_image.filename, self.parent_dir)
        path_to_result = os.path.join(self.save_to_path, relative_path)

        # Making missing dirs if any
        if not os.path.exists(os.path.dirname(path_to_result)):
            os.makedirs(os.path.dirname(path_to_result))

        img.save(path_to_result)

    def process_one(self, image):
        self.current_image = image
        result_img = self.paint_logo(image)
        self.save_painted(result_img)

    def process_all(self):
        for image in self.images:
            self.process_one(image)

    @classmethod
    def get_all_dir_files(cls, dir_path):
        files_list = []
        for name in os.listdir(dir_path):
            path_from_start = os.path.join(dir_path, name)
            if os.path.isfile(path_from_start):
                files_list.append(path_from_start)
            elif os.path.isdir(path_from_start):
                files_list += cls.get_all_dir_files(path_from_start)
        return files_list


if __name__ == '__main__':
    LogoPainter(logo_path='samples/logo.png',
                target_path='samples/pics',
                save_to_path='result',
                corner=Corner.TOP_RIGHT
                ).process_all()
