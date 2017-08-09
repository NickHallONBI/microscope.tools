#!/usr/bin/python
# -*- coding: utf-8
#
# Copyright 2017 Mick Phillips (mick.phillips@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Display a window that allows the user to select a circular area."""
import Tkinter as tk
from PIL import Image
import numpy as np
from resizeimage import resizeimage

class App(tk.Frame):
    def __init__(self, filename, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.filename = str(filename)
        self.create_widgets()


    def create_widgets(self):
        self.canvas = Canvas(self, width=600, height=600)
        temp = Image.open(self.filename)
        if len(np.shape(temp)) == 2:
            temp = resizeimage.resize_cover(temp, [512, 512])
            temp = temp.save("photo.ppm", "ppm")
        elif len(np.shape(temp)) == 3:
            temp = resizeimage.resize_cover(temp[0,:,:], [512, 512])
            temp = temp.save("photo.ppm", "ppm")
        self.image = tk.PhotoImage(file = "photo.ppm")
        self.canvas.create_image(45, 50, anchor = tk.NW, image = self.image)
        self.canvas.pack()

        self.btn_quit = tk.Button(self, text="Quit", command=self.quit)
        self.btn_quit.pack()


class Canvas(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.bind("<Button-1>", self.on_click)
        self.bind("<Button-3>", self.on_click)
        self.bind("<B1-Motion>", self.circle_resize)
        self.bind("<B3-Motion>", self.circle_drag)
        self.bind("<ButtonRelease>", self.on_release)
        self.circle = None
        self.p_click = None
        self.bbox_click = None
        self.centre = (0,0)
        self.diameter = 0

    def on_release(self, event):
        self.p_click = None
        self.bbox_click = None

    def on_click(self, event):
        if self.circle == None:
            self.circle = self .create_oval((event.x-1, event.y-1, event.x+1, event.y+1))
            self.centre = (event.x, event.y)
            self.diameter = event.x+1 - event.x+1 + 1
            np.savetxt('circleParameters.txt', (self.centre[0], self.centre[1], self.diameter))

    def circle_resize(self, event):
        if self.circle is None:
            return
        if self.p_click is None:
            self.p_click = (event.x, event.y)
            self.bbox_click = self.bbox(self.circle)
            return
        bbox = self.bbox(self.circle)
        self.centre = ((bbox[2] + bbox[0])/2, (bbox[3] + bbox[1])/2)
        r0 = ((self.p_click[0] - self.centre[0])**2 + (self.p_click[1] - self.centre[1])**2)**0.5
        r1 = ((event.x - self.centre[0])**2 + (event.y - self.centre[1])**2)**0.5
        scale = r1 / r0
        self.diameter = (r0 + r1)/2
        self.scale(self.circle, self.centre[0], self.centre[1], scale, scale)
        self.p_click= (event.x, event.y)
        np.savetxt('circleParameters.txt', (self.centre[0], self.centre[1], self.diameter))

    def circle_drag(self, event):
        if self.circle is None:
            return
        if self.p_click is None:
            self.p_click = (event.x, event.y)
            return
        self.move(self.circle,
                  event.x - self.p_click[0],
                  event.y - self.p_click[1])
        self.p_click = (event.x, event.y)
        self.centre = self.p_click
        np.savetxt('circleParameters.txt', (self.centre[0], self.centre[1], self.diameter))
        self.update()


if __name__ == '__main__':
    app = App('DeepSIM_interference_test.png')
    app.master.title('Select a circle.')
    app.mainloop()