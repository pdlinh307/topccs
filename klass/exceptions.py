# -*- coding: utf-8 -*-


class CampaignError(Exception):
    table_mapping_errors = dict(
        PAYLOAD_EMPTY='Kiểu dữ liệu đầu vào không hợp lệ, kiểm tra "Content-Type" của HTTP Request Header.',
        PARAM_INVALID="Tham số đầu vào không hợp lệ.",
        PARAM_MISS='Dữ liệu đầu vào thiếu thông tin bắt buộc.',
        ID_EXISTED='CampaignId đã tồn tại. Không thể tạo campaign mới trùng với ID của campaign cũ.',
        ID_NOT_EXISTED="CampaignId không tồn tại.",
        DATETIME_FORMAT="Sử dụng sai format các trường dữ liệu kiểu DATETIME."
    )

    def __init__(self, code):
        self.msg = self.table_mapping_errors[code]

    def __str__(self):
        return repr(self.msg)


class DBError(Exception):
    table_mapping_errors = dict(
        ERROR='Lỗi xảy ra trong quá trình thao tác với cơ sở dữ liệu.',
        CONNECT_ERROR='Lỗi kết nối tới cơ sở dữ liệu.'
    )

    def __init__(self, code):
        self.msg = self.table_mapping_errors[code]

    def __str__(self):
        return repr(self.msg)
