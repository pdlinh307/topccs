# -*- coding: utf-8 -*-


class CampaignError(Exception):
    table_mapping_errors = dict(
        DB_ERROR='Lỗi xảy ra trong quá trình thao tác với cơ sở dữ liệu.',
        DB_CONNECT_ERROR='Lỗi kết nối tới cơ sở dữ liệu.',
        CP_INVALID_PAYLOAD='Kiểu dữ liệu đầu vào không hợp lệ, kiểm tra "Content-Type" của HTTP Request Header.',
        CP_INVALID_PARAM="Tham số đầu vào không hợp lệ.",
        CP_MISS_PARAM='Dữ liệu đầu vào thiếu thông tin bắt buộc.',
        CP_ID_EXISTED='CampaignId đã tồn tại. Không thể tạo campaign mới trùng với ID của campaign cũ.',
        CP_ID_NOT_EXISTED="CampaignId không tồn tại.",
        CP_SINGLETON_CLASS="Hãy sử dụng phương thức get_instance() để khởi tạo đối tượng của lớp singleton.",
        CP_DATETIME_FORMAT="Sử dụng sai format các trường dữ liệu kiểu DATETIME.",
        CTS_EMPTY="Danh sách contact cần gọi (hợp lệ) rỗng."
    )

    def __init__(self, code):
        self.msg = self.table_mapping_errors[code]

    def __str__(self):
        return repr(self.msg)
