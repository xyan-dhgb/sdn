# BÁO CÁO THỰC HÀNH  
**Môn học:** Công nghệ mạng khả lập trình  
**Buổi báo cáo:** Lab 03  
**Tên chủ đề:** Lập trình mạng SDN/OpenFlow với Topology tuỳ ý trong Mininet  
**GVHD:** Phan Xuân Thiện  
**Ngày thực hiện:** 04/04/2025  

## THÔNG TIN CHUNG:

**LỚP:** NT541.P12.1  

| STT | Họ và tên           | MSSV     | Email                     |
|-----|---------------------|----------|---------------------------|
| 1   | Đinh Huỳnh Gia Bảo  | 22520101 | 22520101@gm.uit.edu.vn    |

## ĐÁNH GIÁ KHÁC:

- **Tổng thời gian thực hiện bài thực hành:** Trung bình 3 ngày (04/04/2025 – 07/04/2025)  
- **Link Video thực hiện (nếu có):**  
- **Ý kiến (nếu có):**  
  - Khó khăn  
  - Đề xuất  
- **Điểm tự đánh giá:** 10/10  

---

## BÁO CÁO CHI TIẾT

### Chuẩn bị:
-  Workstation Pro 17: Phần mềm cài đặt và quản lý máy ảo.
- Ryu Controller: Framework của mạng SDN dựa trên kiến trúc thành phần.
- Mininet: Công cụ tạo ra mạng ảo bằng cách lập trình.
- Open vSwitch: Switch ảo mã nguồn mở, được sử dụng phổ biến trong ảo hóa mạng
và mạng SDN.
- Ubuntu 20.04: Hệ điều hành Ubuntu phiên bản 20.04

### Mô hình triển khai
![Mô hình yêu cầu của lab3](/Lab/asset/lab3-topology.png)

---

### Yêu cầu 1: Tạo mạng SDN/OpenFlow với Topology tuỳ ý

#### Cài đặt Mininet

- Bước 1: Trên hệ điều hành Ubuntu 20.04, thực hiện câu lệnh sau trong Terminal để tiến hành cài đặt Mininet:
```bash
sudo apt-get update
sudo apt install mininet
```

- Bước 2: Kiểm tra mininet xem đã cài đặt thành công hay chưa
    - Kiểm tra phiên bản của mininet
    ```bash
    mn -version
    ```

    - Kiểm tra mininet xem có hỗ trợ switch và bộ điều khiển OpenFlow hay không. Đối với lượt kiểm tra này, chúng ta sẽ sử dụng VSwitch mở ở chế độ Bridge/Standalone
    ```bash
    sudo mn --switch ovsbr --test pingall
    ```
#### Tạo mạng SDN/OpenFlow

- Quan sát hình 1, chúng ta có thể thấy được cách triển khai tổng quát của sơ đồ mạng như sau:
    - 1 controller c0
    - 4 switch s1, s2, s3, s4. Trong đó:
        - s1 liên kết với s2
        - s2 liên kết với s3
        - s3 liên kết với s4
    - Mỗi switch kết nối với 4 host:
        - S1 kết nối với h1, h2, h2, h4
        - S2 kết nối với h3, h4, h5, h6
        - S3 kết nối với h7, h8, h9, h10
        - S4 kết nối với h11, h12, h13, h14

- Bước 1: Khởi động Ryu Controller với đoạn mã được tùy chỉnh theo nhu cầu:
    - Trước tiên, hãy tạo hoặc chỉnh sửa tập tin điều khiển bằng lệnh:
    ```bash
    nano simple-switch-13.py
    ```
    - Nội dung của tập tin được truy cập qua đường dẫn dưới đây:  [simple-switch-13](https://github.com/xyan-dhgb/sdn/blob/main/Lab/Lab3/ryu-controller/simple-switch-13.py)
    - Sau khi hoàn tất, khởi chạy Ryu Controller với tập tin simple-switch-13.py và bật tính năng quan sát liên kết bằng lệnh:
    ```bash
    ryu-manager simple-switch-13.py --observe-links
    ```

- Bước 2: Tạo topology tùy chỉnh trên Mininet
    - Tiếp theo, tạo hoặc chỉnh sửa tập tin định nghĩa topology bằng lệnh bên dưới. Nội dung của tập tin được truy cập qua đường dẫn: [mininet-custom-topology](https://github.com/xyan-dhgb/sdn/blob/main/Lab/Lab3/topology/mininet-topoloy-custom.py)
    ```bash
    nano custom-topology.py
    ```
    - Cấp quyền thực thi cho tệp tin:
    ```bash
    chmod +x custom-topology.py
    ```
    - Khi đã hoàn thiện tập tin, khởi chạy topology tùy chỉnh này trên Mininet bằng lệnh (dùng python2):
    ```bash
    sudo python custom-topology.py
    ```

### Yêu cầu 2: Test mạng SDN/OpenFlow được tạo ra, gồm: test kết nối, test hiệu suất của liên kết giữa hai host bất kỳ trong mạng.

- Sau khi triển khai thành công mô hình mạng SDN theo yêu cầu với Mininet và Ryu Controller, bước tiếp theo là kiểm tra hoạt động của mạng để đảm bảo các thành phần được cấu hình đúng cách. Việc kiểm tra bao gồm hai phần chính:
    - *Kiểm tra kết nố*i: Sử dụng lệnh **pingall** để kiểm tra kết nối giữa các host để xác minh rằng kết nối trong mạng hoạt động bình thường.
    ```bash
    mininet > pingall
    ```
    - *Kiểm tra hiệu suất*: Đánh giá băng thông giữa 2 hosts (h1 và h2) bằng công cụ **iperf**, giúp xác định hiệu suất truyền tải dữ liệu trong mạng. Trong đó:
        - h1 đóng vai trò là server đang “lắng nghe” kết nối từ các host khác.
        -  h2 gửi dữ liệu đến h1
        ```bash
        mininet > h1 iperf -s &
        mininet > h2 iperf -c h1
        ```
### Yêu cầu 3: Mở Wireshark, tiến hành bắt các gói tin OpenFlow trao đổi giữa Controller và các Switch trong 2 trường hợp

#### Ping từ H1 đến H4

- Khi tiến hành quan sát các gói tin OpenFlow trong Wireshark, chúng ta sẽ thấy các gói tin:
    - OFPT_PACKET_IN: Gửi từ switch đến controller khi switch không biết cách xử lý gói tin.
    - OFPT_FLOW_MOD: Gửi từ controller đến switch để thêm entry vào flow table.
    - OFPT_PACKET_OUT: Gửi từ controller đến switch để chỉ dẫn switch chuyển tiếp gói tin.

- Quá trình di chuyển: Khi h1 ping đến h4 (cùng kết nối vào switch s1), quá trình diễn ra như sau:
    - h1 khởi tạo quá trình bằng cách gửi một gói tin ARP Request để tìm địa chỉ MAC của h4.
    - Switch s1 khi chưa có flow xử lý gói ARP này, liền lập tức gửi gói PACKET_IN lên controller c0.
    - Controller c0 xử lý và gửi lại một gói PACKET_OUT, yêu cầu s1 flood gói ARP Request đến tất cả các cổng còn lại.
    - h4 nhận được gói ARP và trả lời bằng gói tin ARP Reply để cung cấp địa chỉ MAC của nó.
    - Switch s1, một lần nữa chưa có flow cho gói ARP Reply này, nên gửi PACKET_IN lên controller c0.
    - Controller sau đó cập nhật thông tin địa chỉ MAC và cổng tương ứng, rồi gửi gói FLOW_MOD để cài đặt flow rule trên s1 cho cả chiều đi và chiều về.
    - Từ thời điểm này, các gói tin ICMP (ping và reply) giữa H1 và H4 sẽ đi trực tiếp qua S1 mà không cần thông qua controller nữa.

#### Ping từ H1 đến H16

- Quan sát trong Wireshark, chúng ta sẽ thấy nhiều gói tin OpenFlow hơn so với trường hợp a, vì gói tin phải đi qua nhiều switch (S1 → S2 → S3 → S4) nên sẽ có nhiều gói tin PACKET_IN và FLOW_MOD hơn.

- Quá trình di chuyển: Khi h1 ping đến h16, quá trình khởi đầu bằng việc h1 gửi một gói tin ARP Request để tìm địa chỉ MAC tương ứng với IP của h16.
    - Switch s1 nhận được gói tin này, nhưng chưa có flow xử lý phù hợp, nên gửi gói PACKET_IN lên controller c0.
    -  Controller c0 xử lý và phản hồi bằng gói PACKET_OUT, yêu cầu s1 chuyển tiếp gói tin ARP đến các cổng liên kết.
    - Gói tin được tiếp tục truyền đến s2, nhưng do s2 cũng chưa có flow phù hợp, nó gửi PACKET_IN về controller.
    - Tương tự, controller c0 phản hồi bằng PACKET_OUT, yêu cầu chuyển tiếp đến s3, rồi đến s4.
    - Khi gói ARP Request đến s4, switch này tiếp tục gửi PACKET_IN đến controller c0.
    - Controller c0 một lần nữa phản hồi bằng PACKET_OUT, yêu cầu S4 flood gói tin ARP đến tất cả các host, trong đó có H16.
    - Đối với h16, sau khi nhận được gói tin ARP Request, trả lời bằng một gói ARP Reply gửi ngược về h1.
    - Quá trình tương tự xảy ra theo chiều ngược lại: các switch gửi PACKET_IN khi chưa có flow, và controller gửi PACKET_OUT để gói tin quay về h1.
    - Sau khi hoàn tất trao đổi ARP, controller thiết lập các flow rule trên toàn bộ các switch dọc đường đi để các gói tin ping ICMP sau đó được chuyển tiếp trực tiếp mà không cần hỏi controller nữa.

- Sự khác biệt chính là số lượng gói tin PACKET_IN và FLOW_MOD trong trường hợp b nhiều hơn trường hợp a, vì có nhiều switch tham gia vào quá trình chuyển tiếp gói tin
hơn.

### Yêu cầu 4: Cài đặt OpenvSwitch và chạy thử mạng SDN/OpenFlow với OpenvSwitch

- Bước 1: Tạo topology tùy chỉnh trên Mininet và OpenvSwitch bằng lệnh bên dưới. Nội dung của tập tin được truy cập qua đường dẫn: [ovs-topology](https://github.com/xyan-dhgb/sdn/blob/main/Lab/Lab3/topology/ovs-topology.py)
```bash
nano ovs-topology.py
```

- Bước 2: Khởi động Ryu Controller
```bash
ryu-manager simple-switch-13.py --observe-link
```

- Bước 3: Mở terminal mới và cấp quyền thực thi cho tập tin Mininet:
```bash
chmod +x ovs-topology.py
```

- Bước 4: Triển khai mạng SDN/OpenFlow với OpenvSwitch
```bash
sudo python ovs-topology.py
```

- Bước 5: Kiểm tra:
    - Kiểm tra trạng thái của các OpenvSwitch bridge:
    ```bash
     sudo ovs-vsctl show
    ```
    - Kiểm tra flow table của các switch:
    ```bash
    sudo ovs-ofctl dump-flows s1
    sudo ovs-ofctl dump-flows s2
    sudo ovs-ofctl dump-flows s3
    sudo ovs-ofctl dump-flows s4
    ```