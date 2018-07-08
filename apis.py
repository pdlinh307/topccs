# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from klass.exceptions import CampaignError, DBError
from klass import camp, conf, scheduler, ami
import cworker

""" Initial Flask """
app = Flask(__name__)
# Todo: basic authentication


@app.route('/api/sendCampaign', methods=['POST'])
def send_campaign():
    payload = request.json
    try:
        """ Insert campaign """
        camp.insert(data=payload)
        """ Create schedule """
        cid = int(payload['campaignid'])
        campaign = camp.select_one(table='campaigns', where=dict(campaign_id=cid))
        scheduler.add_job(func=create_jobs,
                          trigger='date',
                          run_date=campaign['time_start'],
                          args=[cid])
        camp.update(table='campaigns', where=['campaign_id'], data=dict(campaign_id=cid, status_scheduled=True))
    except (CampaignError, DBError) as e:
        return jsonify(dict(campaignid=int(payload['campaignid']), status=0, error_msg=e.msg)), 400
    else:
        return jsonify(dict(campaignid=int(payload['campaignid']), status=1))


@app.route('/api/closeCampaign/<int:cid>', methods=['GET'])
def close_campaign(cid):
    try:
        """ Update campaign """
        camp.update(table='campaigns', where=['campaign_id'], data=dict(campaign_id=cid, status_closed=True))
        """ Cancel schedules """
        jobs = scheduler.get_jobs()
        jobs = list(filter(lambda j: int(j.id.split(".")[0]) == cid, jobs))
        for job in jobs:
            scheduler.remove_job(job_id=job.id)
    except DBError as e:
        return jsonify(dict(campaignid=cid, status=0, error_msg=e.msg)), 400
    else:
        return jsonify(dict(campaignid=cid, status=1))


def create_jobs(cid):
    # config = conf.section(name='scheduler')
    contacts = camp.select_many(table='cdr', where=dict(campaign_id=cid))
    contacts = list(filter(lambda c: c['disposition'] != 'ANSWERED', contacts))
    if len(contacts) > 0:
        now = datetime.now()
        for cts in contacts:
            scheduler.add_job(func=send_originate,
                              trigger='date',
                              run_date=now + timedelta(seconds=5),
                              args=[cts['phone_number']],
                              id='{0}.{1}'.format(cid, cts['phone_number']))
            now = now + timedelta(seconds=20)
    return True


def send_originate(phone):
    ami.queue_summary()
