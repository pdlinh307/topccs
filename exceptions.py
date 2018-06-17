class CampaignError(Exception):
    table_mapping_errors = dict(
        CP_NO_PAYLOAD='Payload is not available, please check "Content-Type" header in request',
        CP_MISS_PARAM='Missing parameter',
        CP_ID_EXIST='CampaignId was exists',
        CP_DB_ERROR='Database error'
    )

    def __init__(self, code):
        self.msg = self.table_mapping_errors[code]

    def __str__(self):
        return repr(self.msg)
