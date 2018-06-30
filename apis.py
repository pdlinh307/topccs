# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask, request, jsonify
from klass.campaign import Campaign
from klass.asterisk import AsteriskAMI
from klass.exceptions import CampaignError, DBError
from klass import conf

""" Initial instances """
app = Flask(__name__)
camp = Campaign(config=conf.section(name='api'))
ami = AsteriskAMI(config=conf.section(name='ami'))
# Todo: basic authentication
# Todo: scheduler


@app.route('/api/sendCampaign', methods=['POST'])
def send_campaign():
    payload = request.json
    try:
        """ Insert campaign """
        camp.cp_check_payload(json=payload)
        if camp.cp_check_unique_id(campaign_id=int(payload['campaignid'])):
            camp.cp_insert_one(json=payload)
        """ Insert contacts in a campaign """
        valid_contacts = camp.cts_validate(contacts=payload['contact'])
        camp.cts_insert_many(contacts=valid_contacts, campaign_id=int(payload['campaignid']))
    except (CampaignError, DBError) as e:
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
        campaign_id = int(campaign_id)
        camp.cp_close_one(campaign_id=campaign_id)
    except (CampaignError, DBError) as e:
        return jsonify(dict(campaignid=campaign_id, code=code, status=0, error_msg=e.msg)), 400
    else:
        return jsonify(dict(campaignid=campaign_id, code=code, status=1))


@app.route('/api/getCampaign/<int:campaignid>', methods=['GET'])
def get_campaign(campaignid):
    try:
        campaign = camp.cp_select_one(campaign_id=campaignid)
    except (CampaignError, DBError) as e:
        return jsonify(dict(error_msg=e.msg)), 400
    else:
        for k, v in campaign.items():
            if isinstance(v, datetime):
                campaign[k] = v.strftime(conf.section(name='api')['datetime_format'])
        return jsonify(campaign)


@app.route('/api/getCdr/<int:campaignid>/<int:contactid>', methods=['GET'])
def get_cdr(campaignid, contactid):
    try:
        cdr = camp.cdr_select_one(campaign_id=campaignid, contact_id=contactid)
    except (CampaignError, DBError) as e:
        return jsonify(dict(error_msg=e.msg)), 400
    else:
        for k, v in cdr.items():
            if isinstance(v, datetime):
                cdr[k] = v.strftime(conf.section(name='api')['datetime_format'])
        return jsonify(cdr)
