from html2image import Html2Image
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from PIL import Image, ImageChops


class CodeToPng:
    def __init__(self, code_text, style='default', font='Courier'):
        self.font_size = 13
        self.max_width = 1920
        self.max_height = 1080
        self.line_height = 20
        self.letter_width = 0.64 * self.font_size
        self.code_text = code_text
        self.style = style
        self.font = font

    def save_code_as_image(self, code_text, return_image=False, file_index=0):
        size = self.calculate_image_size(self.code_text)
        lexer = get_lexer_by_name("python")
        formatter = HtmlFormatter(style=self.style)
        html = highlight(code_text, lexer, formatter)
        css = formatter.get_style_defs('.highlight')
        css = f'<style>{css[:25]}font-size: {self.font_size}px;font-family:{self.font};{css[25:]}</style>'
        html_css = f'<html><head>{css}</head><body>{html}</body></html>'
        html_file = f"code_{file_index}.html"
        with open(html_file, "w") as file:
            file.write(html_css)
        hti = Html2Image()
        temp_image_path = f"temp_image_{file_index}.png"
        hti.screenshot(html_file=html_file, save_as=temp_image_path, size=size)
        if return_image:
            image = Image.open(temp_image_path)
            return image
        else:
            self.resize_image(temp_image_path, f"final_image_{file_index}.png")
            return f"final_image_{file_index}.png"

    @staticmethod
    def trim(image):
        bg = Image.new(image.mode, image.size, (255, 255, 255, 0))
        diff = ImageChops.difference(image, bg)
        bbox = diff.getbbox()
        if bbox:
            return image.crop(bbox)
        return image

    def concat_images(self, image_list):
        image_list = [self.trim(img) for img in image_list]
        total_height = sum(img.height for img in image_list)
        max_width = max(img.width for img in image_list)
        new_image = Image.new('RGBA', (max_width, total_height), (255, 255, 255, 0))
        current_height = 0
        for img in image_list:
            new_image.paste(img, (0, current_height), img)
            current_height += img.height
        return new_image

    def calculate_image_size(self, code_text):
        lines = code_text.count('\n') + 1
        width = round(max([len(line) for line in code_text.split('\n')]) * self.letter_width)
        estimated_height = lines * self.line_height
        height = min(estimated_height, self.max_height)
        width = min(width, self.max_width)
        return width, height

    def resize_image(self, input_image_path, output_image_path):
        original_image = Image.open(input_image_path)
        resized_image = original_image.resize((self.max_width, self.max_height), Image.LANCZOS)
        resized_image.save(output_image_path)

    @staticmethod
    def split_code_into_pages(code_text, lines_per_page=50):
        lines = code_text.split('\n')
        pages = [lines[i:i + lines_per_page] for i in range(0, len(lines), lines_per_page)]
        return pages

    def save_code_pages(self, base_file_name, lines_per_page=50, concat_screenshots=False):
        pages = self.split_code_into_pages(self.code_text, lines_per_page)
        images = []
        for i, page in enumerate(pages):
            page_text = "\n".join(page)
            image = self.save_code_as_image(page_text, return_image=True, file_index=i)
            if concat_screenshots:
                images.append(image)
            else:
                file_name = f"{base_file_name}_part{i + 1}.png"
                image.save(file_name)
        if concat_screenshots:
            final_image = self.concat_images(images)
            final_image.save(f"{base_file_name}_concat.png")
