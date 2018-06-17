# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import datetime
from campaign import Campaign
from exceptions import CampaignError

app = Flask(__name__)
camp = Campaign()


@app.route('/api/sendCampaign', methods=['POST'])
def send_campaign():
    payload = request.json
    try:
        # Check payload
        camp.check_payload(json=payload)
        # Check unique id
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


if __name__ == '__main__':
    app.run()
