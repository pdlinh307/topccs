# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from klass.campaign import Campaign
from klass.exceptions import CampaignError

""" Initial instances """
app = Flask(__name__)
camp = Campaign.get_instance(config='config/campaign.conf')
camp.db_connect(dbconfig='config/mysql.conf')


@app.route('/api/sendCampaign', methods=['POST'])
def send_campaign():
    payload = request.json
    try:
        camp.cp_check_payload(json=payload)
        if camp.cp_check_unique_id(int(payload['campaignid'])):
            camp.cp_insert_one(payload)

        valid_contacts = camp.cts_get_valid_list(payload['contact'])
        camp.cts_insert_many(contacts=valid_contacts, campaign_id=int(payload['campaignid']))
    except CampaignError as e:
        return jsonify(dict(campaignid=payload['campaignid'], code=payload['code'], status=0, error_msg=e.msg)), 400
    else:
        return jsonify(dict(campaignid=payload['campaignid'], code=payload['code'], status=1))
