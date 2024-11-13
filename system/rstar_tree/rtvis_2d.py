from tkinter import *
import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import rstartree as rstartree
import pandas as pd
import sys

parser = argparse.ArgumentParser(description="")
parser.add_argument("--M", type=int, default=4, help="maximum number of children")
parser.add_argument("--m", type=int, default=2, help="minimum number of children. try m = floor(0.4*M)")
parser.add_argument("--p", type=int, default=1, help="Parameter controlling how overflow is treated. try p = floor(0.3*M)")
args = parser.parse_args()

# Load dữ liệu
df = pd.read_csv('rstar_tree/generated_data.csv', index_col=0)
data2 = [x for x in enumerate(df.values.tolist())]
print(data2)
rt2cursor = rstartree.create_tree_from_pts(data2, M=args.M, m=args.m, p=args.p)
rt_2 = rt2cursor.root


# Cấu hình cửa sổ Tkinter
root = Tk()
root.title("An R*-Tree")

canvas_width = 800  # Điều chỉnh chiều rộng canvas
canvas_height = 800  # Điều chỉnh chiều cao canvas

canvas = Canvas(root, width=canvas_width, height=canvas_height, background='gray75')
canvas.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Thiết lập không gian vẽ (điều chỉnh phạm vi để phù hợp với dữ liệu của bạn)
L_x, U_x = -150.0, 150.0
L_y, U_y = -150.0, 150.0

# Màu sắc cho các cấp độ khác nhau
colors = ["blue", "green", "red", "purple", "orange", "pink", "cyan"]

#width cho các cấp độ khác nhau
widths = [1, 2, 3, 4, 5, 6, 7, 8, 9,]

def to_tk_coord(x, y):
    """Chuyển đổi tọa độ không gian thành tọa độ Tkinter"""
    u = round(canvas_width * (x - L_x) / (U_x - L_x))
    v = round(canvas_height * (U_y - y) / (U_y - L_y))
    return u, v

def draw_rect(rect, color, level):
    """Vẽ hình chữ nhật và thêm nhãn cấp độ"""
    mx, my = rect.minima[0], rect.minima[1]
    Mx, My = rect.maxima[0], rect.maxima[1]
    mu, mv = to_tk_coord(mx, my)
    Mu, Mv = to_tk_coord(Mx, My)
    
    # Vẽ hình chữ nhật
    canvas.create_rectangle(mu, Mv, Mu, mv, outline=color, width=2*(4-level))
    
    # Thêm nhãn cấp độ
    label_x, label_y = to_tk_coord((mx + Mx) / 2, (my + My) / 2)
    canvas.create_text(label_x, label_y, text=f"Level {level}", fill=color, font=("Arial", 8))

def draw_pts(pts):
    """Vẽ các điểm trong không gian"""
    for pt in pts:
        u, v = to_tk_coord(pt[0], pt[1])
        canvas.create_oval(u - 2, v - 2, u + 2, v + 2, fill="black")

def draw_leaf(rt_leaf, level):
    """Vẽ lá và các điểm trong lá"""
    draw_rect(rt_leaf.key, colors[level % len(colors)], level)
    draw_pts(rt_leaf.get_points())

def draw_r_tree(rt, level=0):
    """Vẽ cây R*-Tree"""
    color = colors[level % len(colors)]  # Lấy màu theo cấp độ

    if rt.is_leaf:
        draw_leaf(rt, level)
    else:
        draw_rect(rt.key, color, level)

    # Vẽ các nút con
    #print(len(rt.children))
    for ch in rt.children:
        draw_r_tree(ch, level + 1)

# Gọi hàm vẽ cho cây
draw_r_tree(rt_2)

# Bắt đầu vòng lặp Tkinter
root.mainloop()
