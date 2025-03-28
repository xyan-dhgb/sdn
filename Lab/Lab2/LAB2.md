# BÁO CÁO THỰC HÀNH  

**Môn học:** Công nghệ mạng khả lập trình  

**Buổi báo cáo:** Lab 02  

**Tên chủ đề:** Cài đặt OpenvSwitch và thực hiện đánh giá hiệu suất  

**GVHD:** Phan Xuân Thiện  

**Ngày thực hiện:** 24/03/2025  

## THÔNG TIN CHUNG:  

**LỚP:** NT541.P12.1  

| STT | Họ và tên            | MSSV     | Email                        |
|-----|------------------|---------|-----------------------------|
| 1   | Đinh Huỳnh Gia Bảo | 22520101 | 22520101@gm.uit.edu.vn |

## ĐÁNH GIÁ KHÁC:

| Nội dung | Kết quả |
|----------|---------|
| Tổng thời gian thực hiện bài thực hành trung bình | 2 ngày (24/03/2025 – 25/03/2025) |
| Link Video thực hiện (nếu có) | [https://drive.google.com/file/d/11SJxWobjyU_xOLitVYYCHE_LPq4E4AYg/view?usp=sharing](https://drive.google.com/file/d/11SJxWobjyU_xOLitVYYCHE_LPq4E4AYg/view?usp=sharing) |
| Ý kiến (nếu có) | |
| + Khó khăn | |
| + Đề xuất | |
| Điểm tự đánh giá | 10/10 |

---

# BÁO CÁO CHI TIẾT

## Chuẩn bị:

- VMware Workstation Pro 17: Phần mềm cài đặt và quản lý máy ảo.
- Ryu Controller: Framework của mạng SDN dựa trên kiến trúc thành phần
- Mininet: Công cụ tạo ra mạng ảo bằng cách lập trình.
- Open vSwitch: Switch ảo mã nguồn mở, được sử dụng phổ biến trong ảo hóa mạng và Software-Defined Networking (SDN).
- Ubuntu 20.04: Hệ điều hành Ubuntu phiên bản 20.04.

## Thực hiện:

### 1. Tiến hành cài đặt Open vSwitch

**Bước 1:** Trước khi cài đặt, chúng ta cần đảm bảo hệ thống được cập nhật và áp dụng các bản vá bảo mật:
```bash
sudo apt update  
sudo apt upgrade  
```

**Bước 2:** Cài đặt các gói phụ thuộc cần thiết cho Open vSwitch:
```bash
sudo apt install -y libssl-dev build-essential bridge-utils  
```

**Bước 3:** Truy cập trang web [sau đây](https://docs.openvswitch.org/en/latest/intro/install/distributions/#debian-ubuntu) của Open vSwitch để biết thông tin của các gói tải. Sau đó, dùng câu lệnh dưới đây để tiến hành tải về:
```bash
sudo apt install -y openvswitch-switch openvswitch-common  
```

**Bước 4:** Sau khi cài đặt xong, kiểm tra phiên bản Open vSwitch:
```bash
ovs-vsctl --version  
```
- Nếu xuất hiện định dạng như ở output bên dưới thì có nghĩa là đã cài đặt thành công:
![Kiểm tra phiên bản của Open vSwitch](/Lab/asset/ovs-version.png)

**Bước 5:** Kiểm tra trạng thái của dịch vụ Open vSwitch:
```bash
sudo systemctl status openvswitch-switch  
```
- Một số trường hợp sẽ thấy dòng lỗi có thông báo là “Dependency failed for Open vSwitch”. Đây là lỗi xảy ra khi một hoặc nhiều dịch vụ mà Open vSwitch phụ thuộc vào không khởi động được, khiến hệ thống không thể khởi chạy openvswitchswitch.service.
- Nguyên nhân:
    - *Dịch vụ phụ thuộc không hoạt động*: Open vSwitch phụ thuộc và cần ovsdbserver hoạt động trước khi openvswitch-switch có thể khởi động
    - *Xung đột giữa các phiên bản OVS*: Cài đặt OVS từ mã nguồn và từ APT cùng lúc, có thể có xung đột đường dẫn.

**Bước 6:** Nếu gặp sự cố khi chạy Open vSwitch, có thể thực hiện kiểm tra đường dẫn của `ovsdb-server` bằng lệnh:
```bash
which ovsdb-server  
```
-  Nếu kết quả trả về là `/usr/local/sbin/ovsdb-server`, điều này có nghĩa là hệ thống đang dùng phiên bản OVS từ mã nguồn thay vì từ APT
- Thực hiện thao tác dưới đây để tiến hành xóa các file OVS cài đặt từ mã nguồn.

**Dừng dịch vụ Open vSwitch**:
```bash
 sudo systemctl stop openvswitch-switch
```

**Dừng tiến trình ovsdb-server**
```bash
sudo pkill -f ovsdb-server
```
**Xóa thư mục cấu hình OVS (phiên bản cài từ mã nguồn)**
```bash
sudo rm -rf /usr/local/etc/openvswitch
```

**Xóa thư mục chứa tệp chạy của OVS**
```bash
sudo rm -rf /usr/local/var/run/openvswitch
```

**Xóa nhật ký OVS**
```bash
sudo rm -rf /usr/local/var/log/openvswitch
```

**Xóa các tệp thực thi OVS trong /usr/local/bin/**
```bash
sudo rm -rf /usr/local/sbin/ovs-*
```

**Xóa các tệp thực thi OVS trong /usr/local/bin**
```bash
 sudo rm -rf /usr/local/bin/ovs-*
 ```

**Xóa các tệp tài nguyên chia sẻ của OVS**
```bash
sudo rm -rf /usr/local/share/openvswitch
```

-  Sau đó, kiểm tra lại đường dẫn, kết quả mong muốn là: /usr/sbin ovsdb-server
![Kiểm tra đường dẫn ovsdb-server](/Lab/asset/ovsdb-server-datapath.png)

**Bước 7:** Cập nhật biến môi trường `$PATH` để đảm bảo hệ thống nhận diện đúng thư mục chứa Open vSwitch:
```bash
echo 'export PATH=/usr/sbin:$PATH' >> ~/.bashrc  
source ~/.bashrc  
```

### 2. Kết nối switch đã cài đặt với một Ryu controller và một số Host (>= 2 Host)

**Bước 1:** Tạo một folder mang tên ryu_controller, sau đó di chuyển vào folder đó và tạo file simple_switch_13.py
```bash
mkdir ryu_controller && cd ryu_controller  
touch simple_switch_13.py  
```

**Bước 2:** Tạo nội dung cho file 'simple_switch_13.py'. Truy cập vào đường link sau để xem nội dung của file: [Nội dung file simple_switch_13.py](https://github.com/xyan-dhgb/sdn/blob/main/Lab/Lab2/ryu-controller/simple-switch-13.py)

**Bước 3:** Mở terminal đầu tiên và khởi động Ryu controller với ứng dụng đã tạo:
``` bash
ryu-manager simple_switch_13.py --verbose
```
- Chúng ta sẽ thấy đầu ra tương tự như sau
![Thực hiện Ryu controller](/Lab/asset/starting-ryu-controller.png)

**Bước 4:** Mở terminal thứ 2, chạy lệnh sau để tạo topology với 3 host kết nối qua Open vSwitch, và kết nối controller qua protocol OpenFlow 1.3
```bash
sudo mn --controller=remote,ip=127.0.0.1,port=6653 -- topo=single,3 --switch=ovsk,protocols=OpenFlow13 –mac
```
- Giải thích:
    -  --controller=remote,ip=127.0.0.1,port=6653: Thiết lập bộ điều khiển (controller) từ xa:
        -  remote: Mininet không sử dụng controller mặc định mà kết nối với một controller (Ryu controller) bên ngoài.
        - ip=127.0.0.1: Controller chạy trên máy cục bộ.
        - port=6653: Cổng controller có giao thức OpenFlow đang lắng nghe
    - --topo=single,3: Tạo một topology với 1 switch và 3 host
    - --switch=ovsk,protocols=OpenFlow13: Cấu hình switch sử dụng Open vSwitch (OVS):
        - Ovsk: Sử dụng Open vSwitch kernel-mode.
        - protocols=OpenFlow13: Bật giao thức OpenFlow 1.3.
    -  --mac: Gán địa chỉ MAC tự động theo thứ tự.
- Kết quả như ảnh dưới:

![Kết quả khi tạo topology](/Lab/asset/topology-creation.png)

- Tại giao diện Mininet, kiểm tra các kết nối:
```bash
mininet> net
```
- Kiểm tra cấu hình OVS:
```bash
mininet> sh sudo ovs-vsctl show
```
- Kiểm tra flow entries:
```bash
mininet> sh sudo ovs-ofctl -O OpenFlow13 dump-flows s1
```

### 3. Cài Wireshark và tiến hành các bước bắt gói tin
Lọc gói tin theo OpenFlow:
```bash
openflow_v4.type==0  # OFP Hello
openflow_v4.type==5  # OFP Features Request
openflow_v4.type==6  # OFP Features Reply
openflow_v4.type==2  # OFP Echo Request
openflow_v4.type==3  # OFP Echo Reply
openflow_v4.type==10 # OFP Packet In
openflow_v4.type==14 # OFP FlowMod
```

### 4. Test hiệu suất mạng với Iperf

**Bước 1:** Khởi động Iperf server trên `h2`
```bash
mininet> h2 iperf -s &  
```

**Bước 2:** Chạy Iperf client từ `h1` đến `h2` để kiểm tra băng thông TCP
```bash
mininet> h1 iperf -c h2 -t 30  
```

**Bước 3:** Thực hiện kiểm tra với các kịch bản khác nhau:
   - Kiểm tra băng thông UDP
```bash
mininet> h1 iperf -c h2 -u -b 100M  
```
   - Kiểm tra TCP với nhiều kết nối song song
```bash
mininet> h1 iperf -c h2 -P 4  
```
