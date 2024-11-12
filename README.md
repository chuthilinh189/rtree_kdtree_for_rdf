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
Cách 1: Chạy main.ipynb trong system_test
Cách 2:
cd system
python main.py --data=data_demo --print=True 

BƯỚC 4: XÂY DỰNG CẤU TRÚC CHỈ MỤC R*-TREE TỪ CÁC ĐIỂM RDF

BƯỚC 5: XÂY DỰNG CẤU TRÚC CHỈ MỤC K-D TREE

BƯỚC 6: TRUY VẤN DỮ LIỆU


