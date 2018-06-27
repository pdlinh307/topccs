class CampaignError(Exception):
    table_mapping_errors = dict(
        CP_NO_PAYLOAD='Payload is not available, please check "Content-Type" header in request',
        CP_MISS_PARAM='Missing parameter',
        CP_ID_EXIST='CampaignId has already exists',
        CP_SINGLETON_CLASS="Use get_instance() method to initial object",
        CP_DATA_INVALID="Input data is not valid",
        CP_DATETIME_FORMAT="Datetime fields is wrong format",
        CTS_EMPTY="Contact list is empty",
        DB_ERROR='Database error',
        DB_CONNECT_ERROR='Database connect error'
    )

    def __init__(self, code):
        self.msg = self.table_mapping_errors[code]

    def __str__(self):
        return repr(self.msg)
