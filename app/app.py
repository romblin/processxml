# -*- encoding: utf8 -*-

import os
import tempfile
import redis
from flask import (Flask, render_template, url_for,
                   jsonify, request, redirect, flash)
from tasks import ProcessFileTask
from utils import digest


app = Flask(__name__)
app.secret_key = 'secret_key'

sr = redis.StrictRedis(db=1, host='redis')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload/', methods=['POST'])
def upload():
    file = request.files['file']

    if not file.filename:
        flash(u'Не выбран файл')
        return redirect('/')

    if not file.filename.endswith('.xml'):
        flash(u'Неподдерживаемый формат файла')
        return redirect('/')

    token = ''
    tmp_file_args = {'prefix': str(os.getpid()),
                     'suffix': '.xml',
                     'delete': False,
                     'dir': '/tmp'}
    with tempfile.NamedTemporaryFile(**tmp_file_args) as pers_file:
        file.save(pers_file)
        ProcessFileTask().delay(filepath=pers_file.name,
                                original_filename=file.filename)
        token = digest(pers_file.name)

    return redirect(url_for('uploaded', token=token, _external=True))


@app.route('/uploaded/')
def uploaded():
    token = request.args.get('token')
    if not token:
        return redirect('/')
    return render_template('uploaded.html', token=token)


@app.route('/status/', methods=['GET'])
def status():
    token = request.args.get('token')

    if not sr.exists(token):
        return jsonify(error='unknown_token')

    info = sr.hgetall(token)

    if info['status'] == 'wait':
        return jsonify(status='wait')

    if info['status'] == 'processing':
        return jsonify(status='processing',
                       filename=info['filename'],
                       total_items_cnt=info['items_cnt'],
                       processed_items_cnt=info['processed_items'])

    if info['status'] == 'complete':
        key = token + 'items_filling_percentages'
        percentages = map(float, sr.lrange(key, 0, -1))
        items_cnt = int(info['items_cnt'])
        average = round(sum(percentages) / items_cnt)
        sr.delete(token, token + 'items_filling_percentages')
        return jsonify(status='complete',
                       filename=info['filename'],
                       total_items_cnt=items_cnt,
                       average_filling_percentage=average)

    sr.delete(token, token + 'items_filling_percentages')
    return jsonify(status='failure')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
