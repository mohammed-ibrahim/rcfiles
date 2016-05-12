from flask import Flask, request
import MySQLdb
import os

"""
Input Configuration
"""
host = os.environ['PERF_MYSQL_HOST']
user = os.environ['PERF_MYSQL_USER']
password = os.environ['PERF_MYSQL_PASSWORD']
db = os.environ['PERF_MYSQL_DB']
"""
End of Input Configuration
"""

"""
Table Deployment

    create database report;

    use report;

    create table trace (
        tag text NOT NULL,
        time_taken int(10) NOT NULL,
        request_id int(10) NOT NULL,
        entry_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

    select avg(time_taken), tag from trace group by tag;
"""

app = Flask('smprf')

db = MySQLdb.connect(host, user, password, db)
cursor = db.cursor()

def wrap(text):
    return '\'' + text + '\''

def insert_values(request_id, tag, time_taken):
    sql = 'insert into trace (tag, time_taken, request_id, entry_time) values (%s, %s, %s, %s)'
    value = sql % (wrap(tag), wrap(time_taken), wrap(request_id), 'now()')
    print(value)
    cursor.execute(value)
    db.commit()

@app.route('/add',methods=['GET'])
def main():
    tag = request.args.get('tag')
    time_taken = request.args.get('time_taken')
    request_id = request.args.get('request_id')

    if (tag == None):
        return "Tag is none", 403
    if (time_taken == None):
        return "Time taken is none", 403
    if (request_id == None):
        return "Request_id is none", 403

    insert_values(request_id, tag, time_taken)
    return "", 201

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=int("9595"), debug=True)
