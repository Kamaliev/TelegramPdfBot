from fpdf import FPDF
import os
from PIL import Image


def add_image(image_path, caption):
    pdf = FPDF()

    p = os.listdir(os.path.abspath(image_path))

    for x in p:
        pdf.add_page()
        filename = f'{image_path}/{x}'
        im = Image.open(filename)
        width, height = im.size
        print(width, height)
        pdf.image(filename, x=0, y=0, h=height / 4.2)
        # x=210
        print(height / 4.2)
        im.close()
        os.remove(filename)

    pdf.output(f'{caption}.pdf')
    return f'{caption}.pdf'


os.system(add_image('503760079', '1'))
