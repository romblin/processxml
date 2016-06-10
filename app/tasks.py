# -*- encoding: utf8 -*-

import os
from itertools import imap
import redis
from lxml import etree
from celery import Celery
from utils import digest

celery = Celery('tasks', broker='redis://redis:6379/0')

sr = redis.StrictRedis(db=1, host='redis')


class ProcessFileTask(celery.Task):

    def run(self, filepath, original_filename):
        token = digest(filepath)

        with open(filepath, 'rt') as xml_file:
            tree = etree.parse(xml_file)
            root = tree.getroot()
            sr.hset(token, 'items_cnt', len(root))
            sr.hset(token, 'status', 'processing')

            for item in root.iterchildren():
                fields_cnt = len(item)
                filled_fields_cnt = sum(imap(lambda field: bool(field.text), item))
                item_filling_percentage = filled_fields_cnt / float(fields_cnt) * 100
                sr.hincrby(token, 'processed_items')
                sr.lpush(token + 'items_filling_percentages', item_filling_percentage)

    def apply_async(self, args=None, kwargs=None, task_id=None, producer=None,
                    link=None, link_error=None, **options):
        token = digest(kwargs['filepath'])
        sr.hmset(token, {
            'filename': kwargs['original_filename'],
            'status': 'wait',
            'items_cnt': 0,
            'processed_items': 0,
        })

        super(ProcessFileTask, self).apply_async(args, kwargs, task_id,
                                                 producer, link,
                                                 link_error, **options)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        token = digest(kwargs['filepath'])
        sr.hset(token, 'status', 'failure')
        try:
            os.remove(kwargs['filepath'])
        except OSError:
            pass

    def on_success(self, retval, task_id, args, kwargs):
        token = digest(kwargs['filepath'])
        sr.hset(token, 'status', 'complete')
        try:
            os.remove(kwargs['filepath'])
        except OSError:
            pass
