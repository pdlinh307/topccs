# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import mysql.connector
import datetime
import sys
import os

app = Flask(__name__)

try:
    cnx = mysql.connector.connect(option_files=os.path.abspath('./config/mysql.conf'))
except:
    sys.exit(2)


@app.route('/api/sendCampaign', methods=['POST'])
def send_campaign():
    # Check payload
    payload = request.json
    if payload is None:
        return jsonify({
            'status': 0,
            'description': 'Payload is not available, please check "Content-Type" header in request.'
        }), 400

    # Check required fields
    required_fields = ['campaignid', 'typeid', 'contact', 'code']
    for f in required_fields:
        if f not in payload:
            return jsonify({
                'status': 0,
                'description': 'missing parameter: %s' % f
            }), 400

    # Check unique campaign
    try:
        cursor_exists_cp = cnx.cursor(dictionary=True)
        cursor_exists_cp.execute("SELECT * FROM `campaign` WHERE `id` = %s", (payload['campaignid'],))
        rows = cursor_exists_cp.fetchall()
        if rows.__len__() > 0:
            return jsonify({'status': 0, 'description': 'CampaignId was exists'})
        else:
            cursor_exists_cp.execute("INSERT INTO `campaign`"
                                     "(`id`, `name`, `start`, `end`, `type_id`, `code`, `receive_status`) "
                                     "VALUES (%s, %s, %s, %s, %s, %s)",
                                     (payload['campaignid'], '', datetime.datetime(2018, 6, 6, 14, 0, 0)),
                                     datetime.datetime(2018, 6, 10, 20, 0, 12), payload['type_id'], payload['code'])
    except:
        return jsonify({'status': 0, 'description': 'database error'})

    # cursor_insert = cnx.cursor(buffered=True)
    # cursor_insert.execute("INSERT INTO `article` (`name`, `content`) "
    #                       "VALUES (%s, %s)", (name, content))

    contacts = payload['contact']
    valid_contacts = list()
    for c in contacts:
        if 'phonenumber' in c:
            valid_contacts.append(c)

    # todo: gui lenh chay kich ban cho call center
    callcenter_status = 0
    return jsonify({
        'campaignid': payload['campaignid'],
        'code': payload['code'],
        'status': callcenter_status,
        'description': '%s/%s contacts are valid' % (len(valid_contacts), len(contacts))
    })


if __name__ == '__main__':
    app.run()
