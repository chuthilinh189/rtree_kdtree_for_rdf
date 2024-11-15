import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import json

# Thêm đường dẫn để nhập các module cần thiết
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import rstar_tree.rstartree as rstartree
import pandas as pd
import sys

def draw_rect_3d(ax, rect, color, level):
    """Vẽ hình chữ nhật trong không gian 3 chiều"""
    mx, my, mz = rect.minima
    Mx, My, Mz = rect.maxima

    # Tạo các đỉnh của hình chữ nhật 3D
    vertices = [
        [mx, my, mz], [mx, My, mz], [Mx, My, mz], [Mx, my, mz],  # mặt đáy
        [mx, my, Mz], [mx, My, Mz], [Mx, My, Mz], [Mx, my, Mz]   # mặt trên
    ]

    # Tạo các mặt của hình hộp chữ nhật
    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],  # mặt đáy
        [vertices[4], vertices[5], vertices[6], vertices[7]],  # mặt trên
        [vertices[0], vertices[1], vertices[5], vertices[4]],  # mặt bên
        [vertices[2], vertices[3], vertices[7], vertices[6]],  # mặt đối diện
        [vertices[1], vertices[2], vertices[6], vertices[5]],  # mặt trước
        [vertices[4], vertices[7], vertices[3], vertices[0]]   # mặt sau
    ]

    # Vẽ các mặt của hình hộp chữ nhật
    ax.add_collection3d(Poly3DCollection(faces, facecolors=color, linewidths=1, edgecolors='k', alpha=0.3))

def draw_pts_3d(ax, pts):
    """Vẽ các điểm trong không gian 3 chiều"""
    for pt in pts:
        ax.scatter(pt[0], pt[1], pt[2], color='black', s=10)

def draw_leaf_3d(ax, rt_leaf, level, colors):
    """Vẽ lá và các điểm trong lá trong không gian 3 chiều"""
    draw_rect_3d(ax, rt_leaf.key, colors[level % len(colors)], level)
    draw_pts_3d(ax, rt_leaf.get_points())

def draw_r_tree_3d(ax, rt, level=0, colors=[], depth_chart=3):
    """Vẽ cây R*-Tree trong không gian 3 chiều"""
    color = colors[level % len(colors)]  # Lấy màu theo cấp độ
    # Vẽ các nút con
    for ch in rt.children:
        # print('level: ', level, ' depth: ', depth_chart)
        if(level<depth_chart):
            draw_r_tree_3d(ax, ch, level + 1, colors=colors, depth_chart=depth_chart)
    if rt.is_leaf:
        draw_leaf_3d(ax, rt, level, colors=colors)
    else:
        draw_rect_3d(ax, rt.key, color, level)

# Hàm chuyển đổi RStarTree thành dict
def rstartree_to_dict(rstartree):
    tree_dict = {
        "is_leaf": rstartree.is_leaf,
        "is_null": rstartree.is_null,
        "key": {
            "minima": rstartree.key.minima,
            "maxima": rstartree.key.maxima
        } if rstartree.key else None,
        "points": rstartree.points,
        "kdtree": None,
        "children": [rstartree_to_dict(child) for child in rstartree.children]
    }
    return tree_dict

# Hàm lưu trữ bộ mã hóa vào file (đã chỉnh sửa)
def save_rstar_tree(tree, file_path):
    # Tạo thư mục nếu nó chưa tồn tại
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    tree_dict = rstartree_to_dict(tree)
    with open(file_path, 'w', encoding='utf-8') as f:
       json.dump(tree_dict, f, ensure_ascii=False, indent=4)
    print(f"Cấu trúc r*-tree đã được lưu vào file: {file_path}") 

def run_rstar_tree(data, M, m, p, print_output, number_charts, depth_chart):
    mdh_directory = "storage/mdh/" + data
    i=1
    for file_name in os.listdir(mdh_directory):
        if file_name.endswith(".csv"):
            print("\n\nXÂY DỰNG CẤU TRÚC CHỈ MỤC R*-TREE CHO : " + file_name)
            rdf_file_path = os.path.join(mdh_directory, file_name)
            # Load dữ liệu
            df = pd.read_csv(rdf_file_path, usecols=[1, 2, 3, 4, 5])
            data3 = [x for x in enumerate(df.values.tolist())]
            # print(data3)
            # print(rstartree)
            rt3cursor = rstartree.create_tree_from_pts(pts_tuples=data3, M=M, m=m, p=p, print_output=print_output)
            
            rt_3 = rt3cursor.root

            # Lưu r*tree vào file
            file_name_no_ext = file_name.replace(".csv", "")
            save_rstar_tree(rt_3, f"storage/rstar_tree/{data}/{file_name_no_ext}.json")

            if(i <= number_charts):
                # Thiết lập không gian vẽ với matplotlib
                fig = plt.figure(figsize=(12, 10))  # Tăng kích thước biểu đồ
                ax = fig.add_subplot(111, projection='3d')

                # Thiết lập không gian vẽ (điều chỉnh phạm vi để phù hợp với dữ liệu của bạn)
                print(rt_3.key.minima[1])
                L_x, U_x = rt_3.key.minima[0]*0.8, rt_3.key.maxima[0]*1.2
                L_y, U_y = rt_3.key.minima[1]*0.8, rt_3.key.maxima[1]*1.2
                L_z, U_z = rt_3.key.minima[2]*0.8, rt_3.key.maxima[2]*1.2

                # Màu sắc cho các cấp độ khác nhau
                colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff", "#ffa500", "#800080", "#008000"]

                    # Gọi hàm vẽ cho cây
                ax.set_xlabel('X Axis')
                ax.set_ylabel('Y Axis')
                ax.set_zlabel('Z Axis')
                ax.set_xlim([L_x, U_x])
                ax.set_ylim([L_y, U_y])
                ax.set_zlim([L_z, U_z])

                draw_r_tree_3d(ax, rt_3, level=0, colors=colors, depth_chart=depth_chart)

                # Hiển thị biểu đồ
                plt.show()
            i+=1