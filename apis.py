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
        """ Insert campaign """
        camp.cp_check_payload(json=payload)
        if camp.cp_check_unique_id(campaign_id=int(payload['campaignid'])):
            camp.cp_insert_one(json=payload)
        """ Insert contacts in a campaign """
        valid_contacts = camp.cts_get_valid_list(contacts=payload['contact'])
        camp.cts_insert_many(contacts=valid_contacts, campaign_id=int(payload['campaignid']))
    except CampaignError as e:
        return jsonify(dict(campaignid=payload['campaignid'], code=payload['code'], status=0, error_msg=e.msg)), 400
    else:
        return jsonify(dict(campaignid=payload['campaignid'], code=payload['code'], status=1))


@app.route('/api/closeCampaign', methods=['GET'])
def close_campaign():
    args = request.args
    campaign_id = args.get('campaignid', None)
    code = args.get('code', None)
    try:
        if campaign_id is None:
            raise CampaignError('CP_MISS_PARAM')
        camp.cp_close_one(campaign_id=campaign_id)
    except CampaignError as e:
        return jsonify(dict(campaignid=campaign_id, code=code, status=0, error_msg=e.msg)), 400
    else:
        return jsonify(dict(campaignid=campaign_id, code=code, status=1))
