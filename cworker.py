import requests
from celery import Celery
from celery.utils.log import get_task_logger
from klass.exceptions import DBError, CampaignError
from klass import conf, camp

celery_app = Celery('cworker', broker='redis://localhost:6379/1', backend='redis://localhost:6379/1')
celery_app.config_from_object(dict(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Ho_Chi_Minh')
)
logger = get_task_logger(__name__)
conf_callback = conf.section(name='callback')


@celery_app.task()
def callback_campaign(campaign_id):
    crm_callback = conf_callback['finish_campaign']
    try:
        campaign = camp.select_one(table='campaigns', where=dict(campaign_id=campaign_id))
    except DBError as e:
        logger.error("CALLBACK_FINISH: campaignid={0}|{1}".format(campaign_id, e.msg))
    else:
        status = 'RECEIVED'
        if campaign['status_completed']:
            status = 'COMPLETED'
        elif campaign['status_closed']:
            status = 'CANCELED'
        elif campaign['status_scheduled']:
            status = 'SCHEDULED'
        data = dict(
            campaignid=campaign_id,
            status=status,
            contact_total=campaign['number_contacts'],
            contact_success=campaign['number_contacts_success']
        )
        try:
            response = requests.post(url=crm_callback, json=data, timeout=int(conf_callback['timeout']))
            logger.info("CALLBACK_CAMPAIGN: campaignid={0}|{1}".format(campaign_id, response.status_code))
        except Exception:
            logger.error("CALLBACK_CAMPAIGN: campaignid={0}|failed".format(campaign_id))


@celery_app.task()
def callback_cdr(campaign_id, contact_id):
    crm_callback = conf_callback['update_campaign']
    try:
        cdr = camp.select_one(table='cdr', where=dict(campaign_id=campaign_id, contact_id=contact_id))
    except (CampaignError, DBError) as e:
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
            logger.info("CALLBACK_CDR: uniqueid={0}|{1}".format(cdr['uniqueid'], response.status_code))
        except Exception:
            logger.error("CALLBACK_CDR: uniqueid={0}|failed".format(cdr['uniqueid']))
