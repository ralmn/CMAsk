import ast
import gevent
from app import sockets, redis, vote_backend
from settings import REDIS_CHAN

@sockets.route('/ws/i')
def inbox(ws):
    while ws.socket is not None:
        gevent.sleep()
        message = ws.receive()

        if message:
            redis.publish(REDIS_CHAN, message)

@sockets.route('/ws/<id>')
def outbox(ws, id):
    vote_backend.register(ws, id)
    print(ws)
    while not ws.closed:
        gevent.sleep()
