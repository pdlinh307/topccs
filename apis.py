# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from klass.campaign import Campaign
from klass.exceptions import CampaignError

""" Initial instances """
app = Flask(__name__)
camp = Campaign.get_instance()
camp.db_connect(config='config/mysql.conf')


@app.route('/api/sendCampaign', methods=['POST'])
def send_campaign():
    payload = request.json
    try:
        camp.check_payload(json=payload)
        if camp.check_unique_id(payload['campaignid']):
            camp.insert_one()
    except CampaignError as e:
        return jsonify({'status': 0, 'error_msg': e.msg}), 400

    # contacts = payload['contact']
    # valid_contacts = list()
    # for c in contacts:
    #     if 'phonenumber' in c:
    #         valid_contacts.append(c)
    #
    # # todo: gui lenh chay kich ban cho call center
    # callcenter_status = 0
    # return jsonify({
    #     'campaignid': payload['campaignid'],
    #     'code': payload['code'],
    #     'status': callcenter_status,
    #     'description': '%s/%s contacts are valid' % (len(valid_contacts), len(contacts))
    # })
