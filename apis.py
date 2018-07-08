# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from klass.campaign import Campaign
from klass.exceptions import CampaignError, DBError
from klass import conf, scheduler


""" Initial instances """
app = Flask(__name__)
camp = Campaign(config=conf.section(name='api'))
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
        campaign = camp.cp_select_one(campaign_id=int(payload['campaignid']))
        scheduler.add_job(_create_job, 'date', run_date=campaign['time_start'], args=[campaign['campaign_id']])
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
        # cworker.cancel_schedule.delay(campaign_id=campaign_id)
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


@app.route('/api/getCdr/<int:campaign_id>/<int:contact_id>', methods=['GET'])
def get_cdr(campaign_id, contact_id):
    try:
        cdr = camp.cts_select_one(where=dict(campaign_id=campaign_id, contact_id=contact_id))
    except (CampaignError, DBError) as e:
        return jsonify(dict(error_msg=e.msg)), 400
    else:
        for k, v in cdr.items():
            if isinstance(v, datetime):
                cdr[k] = v.strftime(conf.section(name='api')['datetime_format'])
        return jsonify(cdr)


def _create_job(campaign_id):
    camp.cp_update(data=dict(status_scheduled=True), where=dict(campaign_id=campaign_id))
    contacts = camp.cts_select_many(where=dict(campaign_id=campaign_id))
    now = datetime.now()
    for cts in contacts:
        scheduler.add_job(send_originate, 'date', run_date=now + timedelta(seconds=5),
                          args=[cts['phone_number']], id='{0}.{1}'.format(campaign_id, cts['phone_number']))
        now = now + timedelta(seconds=20)
    return True


def send_originate(phone):
    exec(open("originate.py").read())
