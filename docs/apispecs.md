# Tổng quan

Tài liệu này được sử dụng tham chiếu cho quá trình tích hợp giữa Call Center Service (CCS) và phần mềm CRM.

## Chú thích

* `api_hostname`: địa chỉ của server hosting api
* `api_port`: cổng được sử dụng để hosting api
* `crm_hostname`: địa chỉ của server CRM API
* `crm_port`: cổng của CRM API.

## Nội dung

- [Tổng quan](#t%E1%BB%95ng-quan)
    - [Chú thích](#ch%C3%BA-th%C3%ADch)
    - [Nội dung](#n%E1%BB%99i-dung)
- [Mô tả các API](#m%C3%B4-t%E1%BA%A3-c%C3%A1c-api)
    - [CCS APIs](#ccs-apis)
        - [1. SEND CAMPAIGN](#1-send-campaign)
            - [Direction](#direction)
            - [INPUT](#input)
                - [URL](#url)
                - [Method](#method)
                - [Headers](#headers)
                - [Data](#data)
            - [OUTPUT](#output)
        - [2. CLOSE CAMPAIGN](#2-close-campaign)
            - [Direction](#direction)
            - [INPUT](#input)
                - [URL](#url)
                - [Method](#method)
                - [Headers](#headers)
                - [Tham số URI](#tham-s%E1%BB%91-uri)
            - [OUTPUT](#output)
    - [CRM APIs](#crm-apis)
        - [1. FINISH CAMPAIGN](#1-finish-campaign)
            - [Direction](#direction)
            - [INPUT](#input)
                - [URL](#url)
                - [Method](#method)
                - [Headers](#headers)
                - [Data](#data)
            - [OUTPUT](#output)
        - [2. UPDATE CAMPAIGN](#2-update-campaign)
            - [Direction](#direction)
            - [INPUT](#input)
                - [URL](#url)
                - [Method](#method)
                - [Headers](#headers)
                - [Data](#data)
            - [OUTPUT](#output)

# Mô tả các API

## CCS APIs

Các API do CCS cung cấp.

### 1. SEND CAMPAIGN

> CRM gửi gói campaign (chiến dịch) gọi ra lên CCS.

#### Direction

> CRM --> CCS

#### INPUT

##### URL

* http://`api_hostname`:`api_port`/api/sendCampaign

##### Method

* POST

##### Headers

* Content-Type: application/json

##### Data

* Định dạng JSON
* Các trường dữ liệu bắt buộc: 
    * `campaignid`: **integer**, id của campaign (được sinh bởi CRM)))
    * `starttime`: **datetime**, thời gian bắt đầu của campaign
    * `endtime`: **datetime**, thời gian kết thúc của campaign
    * `contact`: **array_of_dict**, mảng danh sách các contacts cần gọi
* Định dạng trường thời gian: `%Y-%m-%d %H:%M:%S`
* Ví dụ:

```json
{
    "campaignid": 1,
    "starttime": "2018-07-10 00:24:00",
    "endtime": "2018-07-20 23:40:00",
    "typeid": 2,
    "contact": [
        {
            "id": 1,
            "phonenumber": "0987654321",
            "linkedit": "http://crm.vn/admin/ContactLevelInfo/EditL3/1"
        },
        {
            "id": 2,
            "phonenumber": "0897654123",
            "linkedit": "http://crm.vn/admin/ContactLevelInfo/EditL3/2"
        }
    ]
}
```

#### OUTPUT

Trả về kết quả nhận yêu cầu của CCS (không phải kết quả thực hiện).

* Định dạng `JSON`
* HTTP status code: `200` nếu không gặp lỗi và `400` nếu ngược lại
* Nếu có lỗi xảy ra, trả về mô tả lỗi trong trường `error_msg`.
* Ví dụ:

```json
{
    "campaignid": 1,
    "status": 1
}
```

hoặc trong trường hợp xảy ra lỗi

```json
{
    "campaignid": 1,
    "status": 0,
    "error_msg": "Tham số đầu vào không hợp lệ."
}
```

### 2. CLOSE CAMPAIGN

> CRM gọi khi muốn kết thúc campaign trước thời hạn.

#### Direction

> CRM --> CCS

#### INPUT

##### URL

* http://`api_hostname`:`api_port`/api/closeCampaign/`<int:campaignid>`

##### Method

* GET

##### Headers

* N/A

##### Tham số URI

* `campaignid`: **integer**, id của campaign muốn thực hiện kết thúc sớm trước thời hạn

#### OUTPUT

Trả về kết quả thực hiện yêu cầu của CCS.

* Định dạng `JSON`
* HTTP status code: `200` nếu không gặp lỗi và `400` nếu ngược lại
* Nếu có lỗi xảy ra, trả về mô tả lỗi trong trường `error_msg`.
* Ví dụ:

```json
{
    "campaignid": 1,
    "status": 1
}
```

hoặc trong trường hợp xảy ra lỗi

```json
{
    "campaignid": 1,
    "status": 0,
    "error_msg": "Tham số đầu vào không hợp lệ."
}
```

## CRM APIs

Các API do CRM cung cấp để nhận kết quả thực hiện campaign của CCS (callback api)

### 1. FINISH CAMPAIGN

> Nhận kết quả cuối cùng của campaign sau khi CCS thực hiện.

#### Direction

> CCS --> CRM

#### INPUT

##### URL

* http://`crm_hostname`:`crm_port`/api/finishCampaign

##### Method

* POST

##### Headers

* Content-Type: application/json

##### Data

* Định dạng `JSON`
* Các trường dữ liệu:
    * `campaignid`: **integer**, id của campaign
    * `status`: **string**, kết quả thực hiện của CCS
    * `contact_total`: **integer**, tổng số contact trong chiến dịch
    * `contact_success`: **integer**, tổng số contact đã gọi thành công

* Ví dụ

```json
{
    "campaignid": 1,
    "status": "completed",
    "contact_total": 10,
    "contact_success": 7
}
```

#### OUTPUT

* N/A

### 2. UPDATE CAMPAIGN

> CRM hứng thông tin sau khi CCS thực hiện xong cuộc gọi.

#### Direction

> CCS --> CRM

#### INPUT

##### URL

* http://`crm_hostname`:`crm_port`/api/updateCampaign

##### Method

* POST

##### Headers

* Content-Type: application/json

##### Data

* Định dạng `JSON`
* Các trường dữ liệu:
    * `campaignid`: **integer**, id của campaign
    * `contact_id`: **integer**, id của contact (do CRM quản lý))
    * `phonenumber`: **string**, số điện thoại của contact
    * `agentcode`: **string**, tên số máy lẻ đã gọi
    * `station_id`: **string**, máy lẻ đã gọi
    * `starttime`: **datetime**, thời gian bắt đầu cuộc gọi
    * `answertime`: **datetime**, thời gian trả lời (nếu gọi thành công)
    * `endtime`: **datetime**, thời gian kết thúc cuộc gọi
    * `duration`: **integer**, thời lượng cuộc gọi (giây)
    * `ringtime`: **integer**, thời lượng đổ chuông (giây)
    * `link_down_record`: **string**, đường dẫn download file ghi âm
    * `status`: **string**, trạng thái cuộc gọi
    * `callid`: **string**, id của cuộc gọi
* Ví dụ:

```json
{
    "campaignid": 1,
    "contact_id": 10,
    "phonenumber": "012345679",
    "agentcode": "Agent/9999",
    "station_id": "9999",
    "starttime": "2018-07-05 09:24:00",
    "answertime": "2018-07-05 09:24:05",
    "endtime": "2018-07-05 09:26:42",
    "duration": 162,
    "ringtime": 10,
    "link_down_record": "http://recording.com/path_to_file",
    "status": "ANSWERED",
    "callid": "1234.5678.90"
}
```

#### OUTPUT

* N/A