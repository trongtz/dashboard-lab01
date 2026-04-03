# 📊 Dashboard Phân Tích Xu Hướng Mua Hàng Tiki

## 🎯 Giới thiệu
Đây là dashboard trực quan hóa dữ liệu sản phẩm trên **Tiki**, được xây dựng bằng **Streamlit** và **Plotly**.

Mục tiêu của project là trả lời 3 nhóm câu hỏi chính:
- **Người dùng đang mua nhiều ở danh mục nào?**
- **Phân khúc giá nào là “điểm nóng” về nguồn cung và sức mua?**
- **Tỷ lệ giảm giá ảnh hưởng như thế nào đến hành vi mua hàng?**

Dashboard được thiết kế theo phong cách sáng, gọn, tập trung vào biểu đồ tương tác và tối ưu diện tích hiển thị.

---

## ✨ Công nghệ sử dụng
- **Python**
- **Streamlit** – dựng giao diện dashboard
- **Plotly Express** – vẽ biểu đồ tương tác
- **Pandas / NumPy** – xử lý dữ liệu

---

## 📁 Cấu trúc project
```text
Lab01/
├── app.py
├── data.csv
├── requirements.txt
└── tabs/
    ├── __init__.py
    ├── styles.py
    ├── chart_helpers.py
    ├── product_category_tab.py
    ├── price_segment_tab.py
    └── discount_rate_tab.py
```

### Ý nghĩa từng file
- `app.py`  
  File chính của ứng dụng. Chịu trách nhiệm:
  - nạp dữ liệu,
  - chuẩn hóa tên cột,
  - dựng giao diện tổng,
  - tạo bộ lọc danh mục / sắp xếp,
  - gọi từng tab.

- `data.csv`  
  Tập dữ liệu sản phẩm Tiki dùng để trực quan hóa.

- `requirements.txt`  
  Danh sách thư viện cần cài để chạy hoặc deploy app.

- `tabs/styles.py`  
  Chứa CSS dùng chung cho các tab và style khung biểu đồ.

- `tabs/chart_helpers.py`  
  Chứa helper định dạng biểu đồ Plotly và thông báo khi không có dữ liệu.

- `tabs/product_category_tab.py`  
  Logic cho tab **Doanh mục sản phẩm**.

- `tabs/price_segment_tab.py`  
  Logic cho tab **Phân khúc giá bán**.

- `tabs/discount_rate_tab.py`  
  Logic cho tab **Tỉ lệ giảm giá**.

---

## 🧭 Các tab trong dashboard

## 1) 🛍️ Doanh mục sản phẩm
Tab này tập trung vào câu hỏi:
> **Danh mục nào đang chiếm tỷ trọng mua lớn nhất trên Tiki?**

### Biểu đồ sử dụng
- **Biểu đồ tròn (donut chart)**
  - Thể hiện tỷ trọng lượt mua của các danh mục được chọn.
  - Phần còn lại được gộp vào nhóm **Khác** để đảm bảo tổng tỷ trọng luôn đúng trên toàn bộ dữ liệu.

- **Biểu đồ cột**
  - So sánh trực tiếp tỷ trọng lượt mua giữa các danh mục.
  - Dễ nhìn hơn khi muốn so sánh chênh lệch giữa top nhóm sản phẩm.

### Ý nghĩa
Tab này giúp nhìn nhanh:
- nhóm hàng nào đang dẫn đầu,
- mức độ tập trung sức mua,
- phần thị trường còn lại nằm ở nhóm nào.

---

## 2) 💸 Phân khúc giá bán
Tab này trả lời 2 câu hỏi:
> **Phân khúc giá nào tập trung nhiều sản phẩm và thu hút lượt mua lớn nhất?**  
> **Mức giảm giá tác động ra sao trong từng khoảng giá?**

### Biểu đồ sử dụng
- **Biểu đồ cột theo phân khúc giá**
  - Trục X: các khoảng giá (dưới 100K, 100K–300K, 300K–700K, ...)
  - Trục Y: tổng lượt mua
  - Một cột nổi bật được tô đậm để đánh dấu **phân khúc giá vàng**.

- **Heatmap giảm giá theo phân khúc**
  - Trục X: phân khúc giá
  - Trục Y: biên độ giảm giá
  - Màu sắc thể hiện lượt mua trung bình trên mỗi sản phẩm

### Ý nghĩa
Tab này giúp phân tích:
- phân khúc nào đang là vùng giá hấp dẫn nhất,
- ở phân khúc giá rẻ hay cao cấp, khách hàng có nhạy với giảm giá hay không,
- mức khuyến mãi nào đang hiệu quả hơn theo từng nhóm giá.

---

## 3) 🏷️ Tỉ lệ giảm giá
Tab này tập trung vào câu hỏi:
> **Giảm giá bao nhiêu là đủ để tạo ra sức mua?**  
> **Ngành hàng nào đang sử dụng giảm giá hiệu quả hơn?**

### Biểu đồ sử dụng
- **Box plot theo mức giảm giá**
  - So sánh phân phối lượt mua giữa các nhóm giảm giá: 0%, 1–10%, 11–20%, ...
  - Giúp nhìn trung vị, độ phân tán và mức độ chênh lệch giữa các band giảm giá.

- **Bubble scatter theo ngành hàng**
  - Trục X: giảm giá trung bình
  - Trục Y: lượt mua trung bình trên mỗi sản phẩm
  - Kích thước bong bóng: tổng lượt mua
  - Màu sắc: giá trung vị

### Ý nghĩa
Tab này cho biết:
- mức giảm giá nào đang đi kèm với sức mua cao hơn,
- ngành hàng nào giảm không quá sâu nhưng vẫn bán tốt,
- ngành hàng nào đang phải “đốt” giảm giá nhiều để duy trì doanh số.

---

## ⚙️ Bộ lọc và tương tác
Dashboard hiện có bộ lọc chính ở phần trên:
- **Danh mục**  
  Cho phép tick/bỏ tick từng danh mục muốn xem.

Toàn bộ biểu đồ đều là **biểu đồ tương tác**, hỗ trợ hover để xem chi tiết dữ liệu.

---

## ▶️ Cách chạy project
### 1. Cài thư viện
```bash
pip install -r requirements.txt
```

### 2. Chạy dashboard
```bash
streamlit run app.py
```

---

## 🚀 Deploy
Project có thể deploy trên **Streamlit Cloud**.

Khi deploy, cần đảm bảo repo có:
- `app.py`
- `requirements.txt`
- `data.csv`
- thư mục `tabs/`

---

## 📌 Ghi chú
- Dữ liệu có biên độ rất rộng, từ sản phẩm giá thấp đến hàng cao cấp, nên một số biểu đồ sử dụng cách chia nhóm để dễ đọc hơn.
- Một số tab có nhóm **Khác** nhằm đảm bảo giữ đúng tỷ trọng khi người dùng chỉ chọn một phần danh mục.
- Cấu trúc project đã được tách theo từng tab để dễ bảo trì, mở rộng và chỉnh sửa giao diện.

---

## 👤 Tác giả
Project phục vụ mục đích học tập / trực quan hóa dữ liệu về hành vi mua hàng trên sàn thương mại điện tử Tiki.
