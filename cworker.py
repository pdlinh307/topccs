import requests
from celery import Celery
from celery.utils.log import get_task_logger
from klass import conf
from klass.campaign import Campaign
from klass.exceptions import DBError

celery_app = Celery('cworker')
celery_app.conf.update(
    broker='redis://localhost:6379/1',
    backend='redis://localhost:6379/1',
    task_serializer='json',
    result_serializer='json',
    timezone='Asia/Ho_Chi_Minh',
)
logger = get_task_logger(__name__)
conf_callback = conf.get_section(name='callback')


@celery_app.task(max_retry=3)
def finish_campaign(campaign_id):
    crm_callback = conf_callback['finish_campaign']
    try:
        campaign = Campaign.cp_select_one(campaign_id=campaign_id)
        # Todo: check lai doan status nay cho chinh xac
        campaign_status = 'completed' if campaign['status_completed'] else 'cancel'
    except DBError as err:
        logger.error("UPDATE:campaignid={0}|{1}".format(campaign_id, err.msg))
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
            logger.warning("FINISH:campaignid={0}|failed".format(campaign_id))


@celery_app.task()
def update_campaign(campaign_id, contact_id):
    crm_callback = conf_callback['update_campaign']
    try:
        cdr = Campaign.cdr_select_one(campaign_id=campaign_id, contact_id=contact_id)
    except DBError as err:
        logger.error("UPDATE:campaignid={0},contactid={1}|{2}".format(campaign_id, contact_id, err.msg))
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
            ringtime=cdr['duration']-cdr['billsec'],
            link_down_record=cdr['record_url'],
            status=cdr['disposition'],
            callid=cdr['uniqueid']
        )
        try:
            response = requests.post(url=crm_callback, json=payload, timeout=int(conf_callback['timeout']))
            logger.info("UPDATE:campaignid={0},contactid={1}|{2}".format(campaign_id, contact_id, response.status_code))
        except:
            logger.warning("UPDATE:campaignid={0},contactid={1}|failed".format(campaign_id, contact_id))
