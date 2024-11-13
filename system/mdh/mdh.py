import os
import networkx as nx
import matplotlib.pyplot as plt
from rdflib import Graph, URIRef
import hashlib
from collections import Counter
from mpl_toolkits.mplot3d import Axes3D
import json
import csv

# Hàm nén URI và trả về danh sách các bộ ba RDF trong 1 file
def compress_uri_triples(rdf_file_path):
    g = Graph()
    g.parse(rdf_file_path, format="application/rdf+xml")
    triples = []
    for subj, pred, obj in g:
        subj = URIRef(subj).split("/")[-1]  # Lấy phần cuối cùng của URI
        obj = URIRef(obj).split("/")[-1]  # Lấy phần cuối cùng của URI
        pred = URIRef(pred).split("#")[-1]  # Lấy phần cuối cùng của URI
        triples.append((subj, pred, obj))
    return triples

# Hàm in bộ ba RDF
def print_triples(triples):
    print("\nDANH SÁCH CÁC BỘ BA RDF SAU KHI NÉN URI:")
    if len(triples[0]) == 3:
        for idx, (subj, pred, obj) in enumerate(triples, start=1):
            print(f"{idx}. ({subj}, {pred}, {obj})")
    elif len(triples[0]) == 5:
        for idx, (x, y, z, alpha, beta) in enumerate(triples, start=1):
            print(f"{idx}. ({x}, {y}, {z}, α = {alpha}, β = {beta})")

def visualize_rdf_graph(triples, file_name):
    nx_graph = nx.DiGraph()
    for subj, pred, obj in triples:
        nx_graph.add_edge(subj, obj, label=pred)
    pos = nx.spring_layout(nx_graph, k=0.5, seed=42)
    plt.figure(figsize=(12, 12))
    nx.draw(nx_graph, pos, with_labels=True, node_size=800, node_color="lightblue", font_size=12, font_weight="bold", arrows=True)
    edge_labels = nx.get_edge_attributes(nx_graph, 'label')
    nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels=edge_labels, font_size=12)
    plt.title(f"Mô hình hóa dữ liệu RDF - {file_name}")
    plt.show()

def save_triples_with_frequency_to_file(triples_with_frequency, file_path):
    # Tạo thư mục nếu nó chưa tồn tại
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Lưu bộ ba vào tệp CSV
    csv_file_path = file_path.replace('.json', '.csv')
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['', '0', '1', '2', '3', '4', '5'])  # Header của file CSV
        for idx, (x, y, z, alpha, beta) in enumerate(triples_with_frequency):
            csv_writer.writerow([idx, x, y, z, alpha, beta])
    print(f"Dữ liệu bộ ba đã được lưu vào file: {csv_file_path}")

# Hàm lưu trữ bộ mã hóa vào file (đã chỉnh sửa)
def save_entity_mapping_to_file(entity_mapping, file_path):
    # Tạo thư mục nếu nó chưa tồn tại
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(entity_mapping, f, ensure_ascii=False, indent=4)
    print(f"Bộ mã hóa đã được lưu vào file: {file_path}")

def convert_triples_to_coordinates(triples):
    data_size = len(triples) * 10  # Đảm bảo data_size lớn hơn số lượng triples để giảm khả năng trùng lặp
    coordinates = []
    entity_mapping = {}

    for subj, pred, obj in triples:
        # Tạo mã hóa cho mỗi thực thể
        entity_mapping[subj] = generate_unique_code(entity_mapping, subj, data_size)
        entity_mapping[pred] = generate_unique_code(entity_mapping, pred, data_size)
        entity_mapping[obj] = generate_unique_code(entity_mapping, obj, data_size)

        x = entity_mapping[subj]
        y = entity_mapping[pred]
        z = entity_mapping[obj]
        coordinates.append((x, y, z))

    # In ra mã hóa của các thực thể
    print("\nMÃ HÓA CÁC THỰC THỂ:")
    for entity, code in entity_mapping.items():
        print(f"{entity} = {code}")

    return coordinates, entity_mapping

# Hàm sinh mã không trùng lặp
def generate_unique_code(entity_mapping, entity, data_size):
    code = int(hashlib.md5(entity.encode()).hexdigest(), 16) % (data_size) + 1
    # Kiểm tra và tinh chỉnh nếu bị trùng lặp
    while code in entity_mapping.values():
        code = (code + 1) % (data_size) + 1  # Tăng giá trị và lấy modulo để tránh trùng lặp
    return code


# Hàm thêm tần suất đếm vào các bộ ba
def add_frequency_to_triples(coordinates):
    subject_count = Counter()
    object_count = Counter()

    # Đếm tần suất xuất hiện của mỗi subject và object
    for x, y, z in coordinates:
        subject_count[x] += 1
        object_count[z] += 1

    triples_with_frequency = []
    for x, y, z in coordinates:
        alpha = object_count[x]  # Số lần xuất hiện của x làm object của bộ ba khác
        beta = subject_count[z]  # Số lần xuất hiện của z làm subject của bộ ba khác
        triples_with_frequency.append((x, y, z, alpha, beta))

    return triples_with_frequency

# Hàm vẽ biểu đồ phân đoạn ba chiều
def plot_3d_coordinates(triples, file_name):
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection='3d')

    # Trích xuất các tọa độ x, y, z từ danh sách các bộ ba
    xs = [x for x, y, z, alpha, beta in triples]
    ys = [y for x, y, z, alpha, beta in triples]
    zs = [z for x, y, z, alpha, beta in triples]

    # Vẽ các điểm trong không gian ba chiều
    ax.scatter(xs, ys, zs, c='r', marker='o', alpha=0.3, s=4)  # Màu đỏ, độ trong suốt 0.1, kích thước nhỏ hơn

    # Thiết lập nhãn cho các trục
    ax.set_xlabel('Subject')
    ax.set_ylabel('Predicate')
    ax.set_zlabel('Object')

    if(len(triples) < 100):
        # Gán nhãn cho các điểm là tọa độ của điểm đó
        for x, y, z, alpha, beta in triples:
            ax.text(x, y, z, f'({x}, {y}, {z})', fontsize=10, color='blue')

    # Thiết lập tiêu đề
    plt.title(f"Biểu đồ phân đoạn ba chiều của các bộ ba RDF - {file_name}")
    plt.show()


def run_mdh(data="data_demo", print_output=False, visualize = False, number_charts = 10):
    rdf_directory = "../data/LUBM_Data/" + data
    i = 1
    for file_name in os.listdir(rdf_directory):
        if file_name.endswith(".rdf"):
            print("\n\nXÂY DỰNG BIỂU ĐỒ PHÂN ĐOẠN BA CHIỀU CHO DỮ LIỆU TỆP: " + file_name)
            rdf_file_path = os.path.join(rdf_directory, file_name)
            triples = compress_uri_triples(rdf_file_path)
            if print_output == False:
                print(f"\n1.1. DANH SÁCH CÁC BỘ BA RDF SAU KHI NÉN URI - {file_name}:")
                print_triples(triples)

            if(len(triples) < 100 & visualize):
                visualize_rdf_graph(triples, file_name)

            triples, entity_mapping = convert_triples_to_coordinates(triples)
            if print_output == False:
                print(f"\n1.2. CHUYỂN HÓA GIÁ TRỊ S, P, O THÀNH TỌA ĐỘ SỐ HỌC - {file_name}:")
                print_triples(triples)
            # Lưu bộ mã hóa vào file
            file_name_no_ext = file_name.replace(".rdf", "")
            save_entity_mapping_to_file(entity_mapping, f"storage/mdh/{data}/{file_name_no_ext}_entity_mapping.json")

            # Thêm tần suất đếm vào các bộ ba và in ra
            triples_with_frequency = add_frequency_to_triples(triples)
            if print_output == False:
                print(f"\n1.3. THÊM TẦN SUẤT VÀO CÁC BỘ BA - {file_name}")
                print_triples(triples_with_frequency)
            # Lưu bộ ba vào file
            save_triples_with_frequency_to_file(triples_with_frequency, f"storage/mdh/{data}/{file_name_no_ext}_triples_data.json")

            if(i <= number_charts):
                # Vẽ biểu đồ phân đoạn ba chiều
                plot_3d_coordinates(triples_with_frequency, file_name)
            i+=1