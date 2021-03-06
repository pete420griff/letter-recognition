# This program program collects the letters you draw and stores them as data
# Requires ghostscript to work
# When a letter is printed to command line, draw it on the tkinter canvas and when done press space to proceed to next letter
from tkinter import *
from tkinter.colorchooser import askcolor
from PIL import ImageEnhance
from PIL import Image
from PIL.ImageOps import invert
import numpy as np
import random
import pickle
import os

class Paint(object):

    DEFAULT_PEN_SIZE = 1.0
    DEFAULT_COLOR = 'black'
    
    def __init__(self):
        self.root = Tk()
        
        self.root.bind('<space>',self.space_pressed)
        
        self.images = np.array([])
        self.labels = np.array([])
        self.class_names = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.letter = random.choice(self.class_names)
        print(self.letter,'\n')
        
        self.pen_button = Button(self.root, text='pen', command=self.use_pen)
        self.pen_button.grid(row=0, column=0)

        self.brush_button = Button(self.root, text='brush', command=self.use_brush)
        self.brush_button.grid(row=0, column=1)

        self.color_button = Button(self.root, text='color', command=self.choose_color)
        self.color_button.grid(row=0, column=2)

        self.eraser_button = Button(self.root, text='eraser', command=self.use_eraser)
        self.eraser_button.grid(row=0, column=3)
        
        self.clear_button = Button(self.root, text='clear', command=self.clear_canvas)
        self.clear_button.grid(row=0, column=4)

        self.choose_size_button = Scale(self.root, from_=40, to=100, orient=HORIZONTAL)
        self.choose_size_button.grid(row=0, column=5)

        self.c = Canvas(self.root, bg='white', width=700, height=600)
        self.c.grid(row=1, columnspan=5)
        
        self.setup()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        if input('Save data? (y/n) ') == 'y':
            self.save_path = 'data/user_data/person1/'
            if os.path.exists(os.path.join(os.getcwd(),self.save_path+'train_images.pkl')): # If file already exists, it loads and combines it with the new data
                with open(self.save_path+'train_images.pkl', 'rb') as f:
                    self.old_images = pickle.load(f)
                self.images = np.vstack((self.old_images,self.images))
                with open(self.save_path+'train_labels.pkl', 'rb') as f:
                    self.old_labels = pickle.load(f)
                self.labels = np.append(self.old_labels,self.labels)
                
            with open(self.save_path+'train_images.pkl', 'wb') as f:
                pickle.dump(self.images, f)
            with open(self.save_path+'train_labels.pkl', 'wb') as f:
                pickle.dump(self.labels, f)
        self.root.destroy()
    
    def save(self):
        self.path = 'tmp/image.ps'
        self.c.postscript(file=self.path, colormode='color')
        self.im = Image.open(self.path).resize((28,28)).convert('L')
        self.im = ImageEnhance.Sharpness(self.im).enhance(0)
        self.im.save('tmp/image.png')
        self.image1 = np.asarray(invert(self.im)).reshape(1,28,28) / 255.0
        
        if len(self.images) == 0:
            self.images = self.image1
            self.labels = np.array([self.class_names.index(self.letter.lower())])
        else:
            self.images = np.vstack((self.images,self.image1))
            self.labels = np.append(self.labels,self.class_names.index(self.letter.lower()))
        
        self.letter = random.choice(self.class_names)
        print(self.letter,'\n')

    def space_pressed(self,key):
        self.save()
        self.clear_canvas()
    
    def setup(self):
        self.old_x = None
        self.old_y = None
        self.line_width = self.choose_size_button.get()
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = self.pen_button
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)

    def use_pen(self):
        self.activate_button(self.pen_button)

    def use_brush(self):
        self.activate_button(self.brush_button)

    def choose_color(self):
        self.eraser_on = False
        self.color = askcolor(color=self.color)[1]

    def use_eraser(self):
        self.activate_button(self.eraser_button, eraser_mode=True)
    
    def clear_canvas(self):
        self.c.delete('all')
        
    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief=RAISED)
        some_button.config(relief=SUNKEN)
        self.active_button = some_button
        self.eraser_on = eraser_mode

    def paint(self, event):
        self.line_width = self.choose_size_button.get()
        paint_color = 'white' if self.eraser_on else self.color
        if self.old_x and self.old_y:
            self.c.create_line((self.old_x, self.old_y, event.x, event.y),
                               width=self.line_width, fill=paint_color,
                               capstyle=ROUND, smooth=TRUE, splinesteps=36)
            
            
        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        self.old_x, self.old_y = None, None


if __name__ == '__main__':
    Paint()
