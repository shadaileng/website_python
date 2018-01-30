#!usr/bin/python3
#-*- coding: utf-8 -*-

'''
	******************
	*      Main      *
	******************
	     Powered By %s
'''

__author__ = 'Shadaileng'

import tkinter as tk
import tkinter.messagebox

window = tk.Tk()
window.title('Main Loop')
window.geometry('400x600')

textVar = tk.StringVar()
textVar.set('Test String')
listVar = tk.StringVar()
listVar.set((1, 2, 3, 4))
radiobuttonselect = tk.StringVar()
checkbuttonvalues = []
isClick = False
label = None
button = None
entry = None
listbox = None
scale = None
canvas = None

def main():
	global label, button, entry, listbox, scale, canvas
	label = tk.Label(window, textvariable=textVar, bg='#BFEFFF', font=('Arial', 12), width=16, height=2)
	label.pack()
	button = tk.Button(window, text='click', bg='#C1FFC1', font=('Arial', 12), width=16, height=2, command=click)
	button.pack()
	entry = tk.Entry(window, width=21)
	entry.pack()
	listbox = tk.Listbox(window, listvariable=listVar, width=21, height=4)
	listbox.pack()
	for x in ['A', 'B']:
		radiobutton = tk.Radiobutton(window, text=x, variable=radiobuttonselect, value=x)
		radiobutton.pack()
	scale = tk.Scale(window, label='drag it', from_=5, to=11, orient=tk.HORIZONTAL, length=200, showvalue=1, tickinterval=2, resolution=0.1, command=scaleValue)
	scale.pack()
	for x in ['Python', 'C++']:
		var = tk.StringVar()
		checkbutton = tk.Checkbutton(window, text=x, variable=var, onvalue='love %s' % x, offvalue=None)
		checkbutton.pack()
		checkbuttonvalues.append(var)
	canvas = tk.Canvas(window, bg='#00FFFF', width=200, height=200)
	canvas.pack()
	image_file = tk.PhotoImage(file='ins.gif')
	image = canvas.create_image(100, 100, anchor='nw', image=image_file)
	x0, y0, x1, y1 = 30, 30, 80, 80
	line = canvas.create_line(x0, y0, x1, y1)
	oval = canvas.create_oval(x0, y0, x1, y1, fill='#AB82FF')
	arc = canvas.create_arc(x0 + 50, y0 + 50, x1 + 50, y1 + 50, start=0, extent=180)
	rect = canvas.create_rectangle(x0 + 100, y0, x1 + 100, y1)
	if isClick:
		canvas.move(arc, 0, 1)

	menubar = tk.Menu(window)
	file = tk.Menu(menubar, tearoff=0)
	menubar.add_cascade(label='File', menu=file)

	file.add_command(label='Info', command=info)
	file.add_separator()
	file.add_command(label='Warning', command=warning)
	file.add_separator()
	file.add_command(label='Error', command=error)
	file.add_separator()
	file.add_command(label='Querstion', command=question)

	window.config(menu=menubar)

	frame = tk.Frame(window, bg='red')
	tk.Label(frame, text='L', bg='#CCCFFF', font=('Arial', 12), width=4, height=2).pack(side='left')
	tk.Label(frame, text='T', bg='#CCCFFF', font=('Arial', 12), width=4, height=2).pack(side='top')
	tk.Label(frame, text='R', bg='#CCCFFF', font=('Arial', 12), width=4, height=2).pack(side='right')
	tk.Label(frame, text='B', bg='#CCCFFF', font=('Arial', 12), width=4, height=2).pack(side='bottom')
	frame.place(x = 10, y = 100, anchor='nw')

	frame = tk.Frame(window, bg='red')
	for x in range(4):
		for y in range(5):
			tk.Label(frame, text='B', bg='#CCCFFF',).grid(row=x, column=y, padx=10, pady=5)
	frame.place(x = 220, y = 150, anchor='nw')


def info():
	tk.messagebox.showinfo(title='信息', message='info')

def warning():
	tk.messagebox.showwarning(title='警告', message='warning')

def error():
	tk.messagebox.showerror(title='错误', message='error')

def question():
	tk.messagebox.askquestion(title='是否', message='question')

def click():
	global isClick, label, button, entry
	if isClick:
		textVar.set(entry.get() or 'None')
		entry.insert('insert', '*')
	else:
		textVar.set('Click It')
		entry.insert('end', '*')
	if listbox.curselection():
		entry.insert('end', listbox.get(listbox.curselection()))
#	entry.insert('end', radiobuttonselect)
	for x in checkbuttonvalues:
		if x:
			print(x.get())
	isClick = not isClick

def scaleValue(value):
	entry.insert('end', value + ' ')

if __name__ == '__main__':
	print(__doc__ % __author__)
	print(int('0xC1FFC1', 16))
	main()
	window.mainloop()
