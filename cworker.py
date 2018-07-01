import requests
import sched
import datetime
import time
from celery import Celery
from celery.utils.log import get_task_logger
from klass.campaign import Campaign
from klass.exceptions import DBError, CampaignError
from klass import conf

celery_app = Celery('cworker', broker='redis://localhost:6379/1', backend='redis://localhost:6379/1')
celery_app.config_from_object(dict(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Ho_Chi_Minh')
)
logger = get_task_logger(__name__)
scheduler = sched.scheduler(timefunc=datetime.datetime, delayfunc=time.sleep)
conf_callback = conf.section(name='callback')


@celery_app.task()
def finish_campaign(campaign_id):
    crm_callback = conf_callback['finish_campaign']
    try:
        campaign = Campaign.cp_select_one(campaign_id=campaign_id)
        # Todo: check lai doan status nay cho chinh xac
        campaign_status = 'completed' if campaign['status_completed'] else 'cancel'
    except DBError as e:
        logger.error("UPDATE:campaignid={0}|{1}".format(campaign_id, e.msg))
    else:
        payload = dict(
            campaignid=campaign_id,
            typeid=campaign['type_id'],
            status=campaign_status,
            retry=campaign['round'],
            contact_total=campaign['number_contacts'],
            contact_answered=campaign['number_contacts_success']
        )
        try:
            response = requests.post(url=crm_callback, json=payload, timeout=int(conf_callback['timeout']))
            logger.info("FINISH:campaignid={0}|{1}".format(campaign_id, response.status_code))
        except:
            logger.error("FINISH:campaignid={0}|failed".format(campaign_id))


@celery_app.task()
def update_campaign(campaign_id, contact_id):
    crm_callback = conf_callback['update_campaign']
    try:
        cdr = Campaign.cts_select_one(campaign_id=campaign_id, contact_id=contact_id)
    except DBError as e:
        logger.error("UPDATE:campaignid={0},contactid={1}|{2}".format(campaign_id, contact_id, e.msg))
    else:
        payload = dict(
            campaignid=campaign_id,
            contact_id=contact_id,
            phonenumber=cdr['phone_number'],
            agentcode=cdr['agent'],
            station_id=cdr['station_id'],
            starttime=cdr['time_start'],
            answertime=cdr['time_answer'],
            endtime=cdr['time_end'],
            duration=cdr['duration'],
            ringtime=cdr['duration'] - cdr['billsec'],
            link_down_record=cdr['record_url'],
            status=cdr['disposition'],
            callid=cdr['uniqueid']
        )
        try:
            response = requests.post(url=crm_callback, json=payload, timeout=int(conf_callback['timeout']))
            logger.info("UPDATE:campaignid={0},contactid={1}|{2}".format(campaign_id, contact_id, response.status_code))
        except:
            logger.error("UPDATE:campaignid={0},contactid={1}|failed".format(campaign_id, contact_id))


@celery_app.task()
def update_cdr(campaign_id, contact_id, event):
    try:
        result = Campaign.cts_update_one(campaign_id, contact_id, event)
        logger.info("UPDATE_CDR:campaignid={0},contactid={1}|{2}".format(campaign_id, contact_id, bool(result)))
    except (CampaignError, DBError) as e:
        logger.error("UPDATE_CDR:campaignid={0},contactid={1}|{2}".format(campaign_id, contact_id, e.msg))


@celery_app.task()
def create_schedule(campaign_id):
    campaign = Campaign.cp_select_one(campaign_id=campaign_id)
    contacts = Campaign.cts_select_many(filter=dict(campaign_id=campaign_id))
    for cts in contacts:
        scheduler.enterabs(campaign['time_start'], abc, cts)
    logger.info("SCHEDULER:campaignid={0}".format(campaign_id))


@celery_app.task()
def cancel_schedule(campaign_id):
    pass

def abc(data):
    logger.info(str(data))

