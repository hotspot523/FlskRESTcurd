from flask import Flask, request, jsonify
import random
import string
import time
# from flask_sqlalchemy import SQLAlchemy
from flaskext.mysql import MySQL

app = Flask(__name__)

import json

#
# db = SQLAlchemy(app)
# SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/campaign'

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'campaign'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def hello_world():
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from campaign_ad");
    data = cursor.fetchall()

    if data:
        return "JSON Message: " + json.dumps(data)
    else:
        return "no record found"


@app.route('/ad', methods=['POST'])
def ad_campaign():
    partner_id = ''.join(random.choice(string.ascii_letters) for x in range(6))
    d = request.data
    data = {
        "partner_id": partner_id,
        "duration": int(time.time()) + json.loads(d)['duration'],
        "ad_content": json.loads(d)['ad_content']
    }
    duration = int(time.time()) + json.loads(d)['duration']

    if request.headers['Content-Type'] == 'application/json':
        db = mysql.connect()
        cursor = db.cursor()
        cursor.execute("SELECT * from campaign_ad where partner_id='" + partner_id + "'");
        ad_data = cursor.fetchone()
        if not ad_data:
            cursor.execute("""INSERT INTO campaign_ad VALUES (%s,%s,%s)""",
                           (partner_id, duration, json.loads(d)['ad_content']));
            db.commit()
            return "JSON Message: " + json.dumps(data)
        else:
            return "JSON Message: already exist"
    else:
        return "415 Unsupported Media Type ;)"


@app.route('/ad/<partner_id>', methods=['GET'])
def get_ad_campaign(partner_id):
    current_time = int(time.time())

    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from campaign_ad where partner_id='" + partner_id + "'");
    data = cursor.fetchone()

    if data:
        if current_time < int(data[1]):
            return "JSON Message: " + json.dumps(data)
        else:
            return "MESSAGE: no active ad campaigns exist for the specified partner."
    else:
        return "no record found"


if __name__ == '__main__':
    app.run()
