#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging.config
import os
import configs.config

import opentracing
import yaml
from aoiklivereload import LiveReloader
from utils import *
from basictracer import BasicTracer
from loggers import AioReporter
from sanic import Sanic
from sanic.config import Config
from configs.db import ConnectionPool
from sanic.exceptions import RequestTimeout, NotFound
from sanic.response import json, text, HTTPResponse
from sanic_cors import CORS
from crud import crud_bp, db, ShanghaiPersonInfo, LOGO


import doc
# How is Support hot reload in Sanic?
# Just do it !
reloader = LiveReloader()
reloader.start_watcher_thread()

from openapi import blueprint as openapi_blueprint

with open(os.path.join(os.path.dirname(__file__), 'logging.yml'), 'r') as f:
    logging.config.dictConfig(yaml.load(f))

app = Sanic(__name__,error_handler=CustomHandler())

CORS(app, automatic_options=True)  # resolve pre-flight request problem (https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request)

app.config = configs.load_config() #app.config.from_object(config)
print('DB_CONFIG=',app.config['DB_CONFIG'])
# add blueprint
app.blueprint(openapi_blueprint)
# app.blueprint(crud_bp)

# but due to not support http `options` method in sanic core (https://github.com/channelcat/sanic/issues/251).
# So have to use third package extension for Sanic-Cors. Thank you @ashleysommer!

_logger = logging.getLogger('sanic')

@app.listener('before_server_start')
async def before_srver_start(app, loop):
    queue = asyncio.Queue()
    app.queue = queue
    loop.create_task(consume(queue, app.config['ZIPKIN_SERVER']))
    print('loop: ' , loop)
    reporter = AioReporter(queue=queue)
    tracer = BasicTracer(recorder=reporter)
    tracer.register_required_propagators()
    opentracing.tracer = tracer
    # app.db = await ConnectionPool(loop=loop).init(app.config['DB_CONFIG'])
    app.db = ConnectionPool(loop=loop).init(app.config['DB_CONFIG'])


@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    app.queue.join()


@app.middleware('request')
async def cros(request):
    config = request.app.config
    if request.method == 'OPTIONS':
        headers = {'Access-Control-Allow-Origin': config['ACCESS_CONTROL_ALLOW_ORIGIN'],
                   'Access-Control-Allow-Headers': config['ACCESS_CONTROL_ALLOW_HEADERS'],
                   'Access-Control-Allow-Methods': config['ACCESS_CONTROL_ALLOW_METHODS']}
        return json({'code': 0}, headers=headers)
    if request.method == 'POST' or request.method == 'PUT':
        request['data'] = request.json
    span = before_request(request)
    request['span'] = span


@app.middleware('response')
async def cors_res(request, response):
    config = request.app.config
    span = request['span'] if 'span' in request else None
    if response is None:
        return response
    result = {'code': 0}
    if not isinstance(response, HTTPResponse):
        if isinstance(response, tuple) and len(response) == 2:
            result.update({
                'data': response[0],
                'pagination': response[1]
            })
        else:
            result.update({'data': response})
        response = json(result)
        if span:
            span.set_tag('http.status_code', "200")
    if span:
        span.set_tag('component', request.app.name)
        span.finish()
    response.headers["Access-Control-Allow-Origin"] = config['ACCESS_CONTROL_ALLOW_ORIGIN']
    response.headers["Access-Control-Allow-Headers"] = config['ACCESS_CONTROL_ALLOW_HEADERS']
    response.headers["Access-Control-Allow-Methods"] = config['ACCESS_CONTROL_ALLOW_METHODS']
    return response


@app.exception(RequestTimeout)
def timeout(request, exception):
    return json({'message': 'Request Timeout'}, 408)


@app.exception(NotFound)
def notfound(request, exception):
    return json(
        {'message': 'Requested URL {} not found'.format(request.url)}, 404)


@app.middleware('response')
async def custom_banner(request, response):
    response.headers["content-type"] = "application/json"


@doc.summary('create test')
@doc.description('create test')
@doc.produces({'id': int})
# @logger()
@app.route("/")
async def test(request):
    _logger.info("this is a test()!")
    return text("hello world")

# app.add_route(test, '/')

@app.websocket('/feed')
async def feed(request, ws):
    while True:
        data = 'hello!'
        print('Sending: ' + data)
        await ws.send(data)
        data = await ws.recv()
        print('Received: ' + data)

# app.add_websocket_route(feed, '/feed')

# server = websocket_server(7001)
# server.start()
_logger.info("server start ....!")
app.run(host='0.0.0.0', port=7000, debug=True)

