# Ý TƯỞNG ĐỒ ÁN CỦA MÔN HỌC CÔNG NGHỆ MẠNG KHẢ LẬP TRÌNH - NT541.P21

## Ứng dụng mạng SDN và ảo hóa mạng trong Trường Đại học thông minh (Smart Campus)

**Tình huống:**

- Một trường đại học muốn xây dựng mạng ảo hóa thông minh để phân chia luồng dữ liệu giữa sinh viên, giảng viên, và hệ thống nghiên cứu.
Cần đảm bảo băng thông cao cho hệ thống e-learning, phòng lab ảo, và bảo vệ dữ liệu nghiên cứu.

**Giải pháp:**

- Dùng SDN để kiểm soát mạng theo nhóm người dùng (e.g., sinh viên, giảng viên, quản lý).

- Dùng Network Virtualization để cô lập tài nguyên mạng giữa các khoa (e.g., khoa CNTT có quyền truy cập lab riêng).

- Dùng IDS (Intrusion Detection System) tích hợp với SDN để phát hiện tấn công mạng trong trường (tùy chọn).

**Công nghệ:** Ryu Controller, VXLAN, OpenFlow, Mininet, Suricata.
