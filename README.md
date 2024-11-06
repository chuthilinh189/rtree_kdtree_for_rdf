BƯỚC 1: TẢI CÁC THƯ VIỆN CẦN SỬ DỤNG

BƯỚC 2: TẢI DỮ LIỆU RDF LUBM_Data (nếu sử dụng dữ liệu test hoặc demo thì bỏ qua bước này)
cd data
java -jar LUBM_Data
pip install rdflib
Chạy downloaddata.ipynb


BƯỚC 3: XÂY DỰNG BIỂU ĐỒ PHÂN ĐOẠN 3 CHIỀU 
Cách 1: Chạy main.ipynb trong system_test
Cách 2:
cd system
python main.py --data=data_demo --print=True > output/data_demo.out 2>&1