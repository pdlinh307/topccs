# -*- coding: utf-8 -*-
import subprocess
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from klass.exceptions import CampaignError, DBError
from klass.campaign import Campaign
from klass import conf, scheduler, db

""" Initial Flask """
app = Flask(__name__)
""" Initial Campaign """
camp = Campaign(conf.section(name='api'))


@app.route('/api/sendCampaign', methods=['POST'])
def send_campaign():
    payload = request.json
    try:
        """ Insert campaign """
        camp.insert(data=payload)
        """ Create schedule """
        cid = int(payload['campaignid'])
        campaign = db.select_one(table='campaigns', where=dict(campaign_id=cid))
        conf_sched = conf.section(name='scheduler')
        retries = int(conf_sched['retries'])
        interval = int(conf_sched['interval'])
        for i in range(retries):
            scheduler.add_job(func=create_jobs,
                              trigger='date',
                              run_date=campaign['time_start'] + timedelta(seconds=(i*interval)),
                              args=[cid],
                              id='{0}.p{1}'.format(cid, i))
        db.update(table='campaigns', where=['campaign_id'], data=dict(campaign_id=cid, status_scheduled=True))
    except (CampaignError, DBError) as e:
        return jsonify(dict(campaignid=int(payload['campaignid']), status=0, error_msg=e.msg)), 400
    else:
        return jsonify(dict(campaignid=int(payload['campaignid']), status=1))


@app.route('/api/closeCampaign/<int:cid>', methods=['GET'])
def close_campaign(cid):
    try:
        """ Cancel schedules """
        jobs = scheduler.get_jobs()
        jobs = list(filter(lambda j: int(j.id.split(".")[0]) == cid, jobs))
        for job in jobs:
            scheduler.remove_job(job_id=job.id)
        """ Update campaign """
        db.update(table='campaigns', where=['campaign_id'], data=dict(campaign_id=cid, status_closed=True))
    except DBError as e:
        return jsonify(dict(campaignid=cid, status=0, error_msg=e.msg)), 400
    else:
        return jsonify(dict(campaignid=cid, status=1))


def create_jobs(cid):
    # conf_sched = conf.section(name='scheduler')
    contacts = db.select_many(table='cdr', where=dict(campaign_id=cid))
    contacts = list(filter(lambda c: c['disposition'] != 'ANSWERED', contacts))
    if len(contacts) > 0:
        now = datetime.now() + timedelta(seconds=10)
        for cts in contacts:
            scheduler.add_job(func=send_originate,
                              trigger='date',
                              run_date=now,
                              args=[cts['id']],
                              id='{0}.s{1}'.format(cid, cts['phone_number']))
            now = now + timedelta(seconds=30)
    return True


def send_originate(rid):
    result = subprocess.check_output('python3.6 originate.py {0}'.format(rid), shell=True).strip()
    uniqueid = result.decode('utf-8')
    db.update(table='cdr', where=['id'], data=dict(id=rid, uniqueid=uniqueid))