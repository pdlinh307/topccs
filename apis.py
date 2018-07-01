# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask, request, jsonify
from klass.campaign import Campaign
# from klass.asterisk import AsteriskAMI
from klass.exceptions import CampaignError, DBError
from klass import conf
import cworker


""" Initial instances """
app = Flask(__name__)
camp = Campaign(config=conf.section(name='api'))
# ami = AsteriskAMI(config=conf.section(name='ami'))
# Todo: basic authentication
# Todo: scheduler


@app.route('/api/sendCampaign', methods=['POST'])
def send_campaign():
    """
    Create a new campaign.
    """
    payload = request.json
    try:
        """ Insert campaign """
        camp.cp_check_payload(json=payload)
        if camp.cp_check_unique_id(campaign_id=int(payload['campaignid'])):
            camp.cp_insert_one(json=payload)

        """ Insert contacts in a campaign """
        valid_contacts = camp.cts_validate(contacts=payload['contact'])
        camp.cts_insert_many(contacts=valid_contacts, campaign_id=int(payload['campaignid']))

        """ Create scheduler """
        cworker.create_schedule.delay(campaign_id=int(payload['campaignid']))
    except (CampaignError, DBError) as e:
        return jsonify(dict(campaignid=payload['campaignid'], code=payload['code'], status=0, error_msg=e.msg)), 400
    else:
        return jsonify(dict(campaignid=payload['campaignid'], code=payload['code'], status=1))


@app.route('/api/closeCampaign/<int:campaign_id>', methods=['GET'])
def close_campaign(campaign_id):
    """
    Cancel a campaign.
    """
    try:
        """ Close campaign """
        camp.cp_close_one(campaign_id=campaign_id)

        """ Cancel scheduler """
        cworker.cancel_schedule.delay(campaign_id=campaign_id)
    except (CampaignError, DBError) as e:
        return jsonify(dict(campaignid=campaign_id, status=0, error_msg=e.msg)), 400
    else:
        return jsonify(dict(campaignid=campaign_id, status=1))


@app.route('/api/getCampaign/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    try:
        campaign = camp.cp_select_one(campaign_id=campaign_id)
    except (CampaignError, DBError) as e:
        return jsonify(dict(error_msg=e.msg)), 400
    else:
        for k, v in campaign.items():
            if isinstance(v, datetime):
                campaign[k] = v.strftime(conf.section(name='api')['datetime_format'])
        return jsonify(campaign)


@app.route('/api/getCdr/<int:campaign_id>/<int:contactid>', methods=['GET'])
def get_cdr(campaign_id, contactid):
    try:
        cdr = camp.cts_select_one(campaign_id=campaign_id, contact_id=contactid)
    except (CampaignError, DBError) as e:
        return jsonify(dict(error_msg=e.msg)), 400
    else:
        for k, v in cdr.items():
            if isinstance(v, datetime):
                cdr[k] = v.strftime(conf.section(name='api')['datetime_format'])
        return jsonify(cdr)
