# BÁO CÁO THỰC HÀNH
**Môn học:** Công nghệ mạng khả lập trình  
**Buổi báo cáo:** Lab 03  
**Chủ đề:** Lập trình mạng SDN/OpenFlow với Topology tuỳ ý trong Mininet  
**GVHD:** Phan Xuân Thiện  
**Ngày thực hiện:** 04/04/2025  

---

## THÔNG TIN CHUNG

- **Lớp:** NT541.P12.1  
- **Họ và tên:** Đinh Huỳnh Gia Bảo  
- **MSSV:** 22520101  
- **Email:** 22520101@gm.uit.edu.vn  

### Đánh giá khác:

| Nội dung                         | Kết quả                                |
|----------------------------------|----------------------------------------|
| Tổng thời gian thực hiện        | Trung bình 3 ngày (04/04 – 07/04/2025) |
| Link Video (nếu có)             | _Chưa cung cấp_                        |
| Ý kiến (nếu có)                 | - Khó khăn: _(bổ sung sau nếu có)_ <br> - Đề xuất: _(bổ sung sau nếu có)_ |
| Điểm tự đánh giá                | **10/10**                              |

---

## BÁO CÁO CHI TIẾT

### Chuẩn bị

- **VMware Workstation Pro 17** – Phần mềm tạo và quản lý máy ảo.  
- **Ryu Controller** – Framework dùng để lập trình SDN.  
- **Mininet** – Công cụ tạo mô phỏng mạng ảo.  
- **Open vSwitch (OVS)** – Switch ảo dùng phổ biến trong ảo hóa mạng và SDN.  
- **Ubuntu 20.04** – Hệ điều hành chính.

---

### Yêu cầu 1: Tạo mạng SDN/OpenFlow với Topology tuỳ ý

#### Cài đặt Mininet
```bash
sudo apt install mininet
mn --version
sudo mn --switch ovsbr --test pingall
