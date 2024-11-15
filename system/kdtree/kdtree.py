import os
import json
import numpy as np

# Class đại diện cho một nút trong cây k-d
class Node:
    def __init__(self, point, left=None, right=None, axis=None):
        self.point = point  # Điểm tại nút này (tọa độ 3 chiều)
        self.left = left  # Nhánh trái của nút
        self.right = right  # Nhánh phải của nút
        self.axis = axis  # Trục phân chia (0: x, 1: y, 2: z)

# Hàm xây dựng cây k-d từ danh sách các điểm
def build_kd_tree(points, depth=0, use_variance=False):
    n = len(points)
    if n == 0:
        return None

    k = 3  # Số chiều của dữ liệu (3 chiều)
    axis = depth % k  # Xác định trục phân chia dựa trên độ sâu

    if use_variance:
        # Chọn trục phân chia dựa trên phương sai lớn nhất của các tọa độ
        variances = [np.var([p[i] for p in points]) for i in range(k)]
        axis = int(np.argmax(variances))

    # Sắp xếp các điểm theo trục hiện tại và chọn điểm trung vị làm điểm gốc
    points.sort(key=lambda x: x[axis])
    median = n // 2

    # Tạo nút và đệ quy xây dựng cây cho hai nhánh trái và phải
    return Node(
        point=[float(coord) if isinstance(coord, np.generic) else coord for coord in points[median]],
        left=build_kd_tree(points[:median], depth + 1, use_variance),
        right=build_kd_tree(points[median + 1:], depth + 1, use_variance),
        axis=axis
    )

# Hàm xử lý một file R*-tree JSON và tạo file k-d tree tương ứng
def process_rtree_json(rtree_json_path, kdtree_output_path):
    # Tạo thư mục nếu chưa tồn tại
    os.makedirs(os.path.dirname(kdtree_output_path), exist_ok=True)
    
    with open(rtree_json_path, 'r') as f:
        rtree_data = json.load(f)

    kdtrees = {}
    kdtree_id_counter = 1

    # Hàm đệ quy duyệt qua các nút của cây R*-tree
    def traverse_rtree(node):
        nonlocal kdtree_id_counter
        if node['is_leaf'] and node['points']:
            # Xây dựng cây k-d cho các điểm trong lá
            points = list(node['points'].values())
            kd_tree = build_kd_tree(points, use_variance=True)

            # Gán một ID duy nhất cho cây k-d này và lưu lại
            kdtree_id = f"kdtree_{kdtree_id_counter}"
            kdtree_id_counter += 1
            kdtrees[kdtree_id] = kd_tree_to_dict(kd_tree)

            # Cập nhật nút R*-tree với ID của cây k-d
            node['kdtree'] = kdtree_id

            # In ra cây k-d đã tạo
            print(f"Cấu trúc cây k-d với ID {kdtree_id}:")
            print_kd_tree_readable(kd_tree)
            print("***********")
        else:
            # Duyệt qua các nút con
            for child in node.get('children', []):
                traverse_rtree(child)

    traverse_rtree(rtree_data)

    # Lưu lại file R*-tree JSON đã cập nhật
    with open(rtree_json_path, 'w') as f:
        json.dump(rtree_data, f, indent=4)

    # Lưu các cây k-d vào file JSON mới
    with open(kdtree_output_path, 'w') as f:
        json.dump(kdtrees, f, indent=4)
    print(f"Cấu trúc kdtree đã được lưu vào file: {os.path.relpath(kdtree_output_path, start=current_directory)}")

# Hàm chuyển đổi cây k-d thành dạng từ điển để lưu trữ
def kd_tree_to_dict(node):
    if node is None:
        return None
    return {
        'point': [float(coord) if isinstance(coord, np.generic) else coord for coord in node.point],  # Tọa độ của điểm tại nút này
        'axis': node.axis,  # Trục phân chia tại nút này
        'left': kd_tree_to_dict(node.left),  # Nhánh trái của cây
        'right': kd_tree_to_dict(node.right)  # Nhánh phải của cây
    }

# Hàm in ra cây k-d theo định dạng dễ đọc
def print_kd_tree(node, depth=0):
    if node is not None:
        print(f"{'  ' * depth}Node(point={node.point}, axis={node.axis})")
        print_kd_tree(node.left, depth + 1)
        print_kd_tree(node.right, depth + 1)

# Hàm in ra cây k-d theo định dạng dễ đọc với phân cấp rõ ràng hơn
def print_kd_tree_readable(root, depth=0, prefix="Root"):
    if root is not None:
        axis_name = ['x', 'y', 'z'][root.axis] if root.axis is not None else 'None'
        print("  " * depth + f"{prefix}: {root.point} (axis={axis_name})")
        print_kd_tree_readable(root.left, depth + 1, prefix="Left")
        print_kd_tree_readable(root.right, depth + 1, prefix="Right")

# Hàm xử lý tất cả các file R*-tree JSON trong thư mục được chỉ định
def process_all_rtree_files(rstar_directory, kdtree_directory):
    for file_name in os.listdir(rstar_directory):
        if file_name.endswith('.json'):
            rtree_json_path = os.path.join(rstar_directory, file_name)
            kdtree_output_path = os.path.join(kdtree_directory, f"kdtree_{file_name}")
            process_rtree_json(rtree_json_path, kdtree_output_path)

# Chương trình chính
if __name__ == "__main__":
    # Sử dụng các đường dẫn tương đối để dễ dàng chuyển đổi trên các hệ thống khác
    current_directory = os.path.dirname(os.path.abspath(__file__))
    rstar_directory = os.path.join(current_directory, "..", "storage", "rstar_tree", "data")  # Thư mục chứa các file R*-tree JSON
    kdtree_directory = os.path.join(current_directory, "..", "storage", "kdtree", "data")  # Thư mục để lưu các file k-d tree JSON
    process_all_rtree_files(rstar_directory, kdtree_directory)
