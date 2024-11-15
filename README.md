BƯỚC 1: TẢI CÁC THƯ VIỆN CẦN SỬ DỤNG

BƯỚC 2: TẢI DỮ LIỆU RDF LUBM_Data (nếu sử dụng dữ liệu test hoặc demo thì bỏ qua bước này)
cd data
<!-- java -jar LUBM_Data -->
Chạy downloaddata.ipynb

-> Bộ dữ liệu sử dụng:
- data: Bộ dữ liệu LUBM về dữ liệu của các trường đại học
- data_test: 1 vài dữ liệu nhỏ của data
- data_demo: dữ liệu để demo nhỏ


BƯỚC 3: XÂY DỰNG BIỂU ĐỒ PHÂN ĐOẠN 3 CHIỀU 
cd system
python main.py --mdh=True --data=data_demo --print=True --visualize=True
python main.py --mdh=True --data=data_test --print=False  
python main.py --mdh=True --data=data --print=False --number_charts=3     

-> Các điểm dữ liệu RDF trong không gian 3 chiều và bộ mã hóa được lưu ở system/storage/mdh/


BƯỚC 4: XÂY DỰNG CẤU TRÚC CHỈ MỤC R*-TREE TỪ CÁC ĐIỂM RDF
- demo cấu trúc chỉ mục r*-tree với dữ liệu điểm 2d
python rstar_tree/datagen2d.py --data=30
python rstar_tree/rtvis_2d.py --M=4 --m=2 --p=1
- xây dựng cấu trúc chỉ mục R*-tree cho dữ liệu RDF
python main.py --rstar_tree=True --data=data_demo --M=4 --m=2 --p=1
python main.py --rstar_tree=True --data=data_test --M=4 --m=2 --p=1 --print=False
python main.py --rstar_tree=True --data=data --M=32 --m=12 --p=10 --print=False --number_charts=1 --depth_chart=3


BƯỚC 5: XÂY DỰNG CẤU TRÚC CHỈ MỤC K-D TREE



BƯỚC 6: TRUY VẤN DỮ LIỆU
- Kiểm tra Q isSPARQL() trả về tập hợp các truy vấn đơn
- FilterPhase(Các cây R*tree, truy vấn đơn) trả về các id của cây k-d tree
- RefinePhase(Các cây k-d tree, truy vấn đơn) trả về 1 tupleset
- JOIN(tuplesets1, tupleset2, Q) trả về 1 tupleset (Q để xác định điều kiện truy vấn)

split_leaf