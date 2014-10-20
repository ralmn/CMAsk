import ast
import gevent
from app import sockets, redis, vote_backend
from settings import REDIS_CHAN

print('yolo')
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


# socket_users = {0:[]}

# @sockets.route('/ws/r')
# def result_sock(ws):
#     print('init')
#     from cmask.models import Vote
#     while True:
#         message = ws.receive()
#         message = ast.literal_eval(message)
#         id = message.get('id')
#         sock = []
#         if id in socket_users:
#             sock = socket_users.get(id)
#         sock.append(ws)
#         vote = Vote.query.filter_by(id=message.get('id')).first_or_404()
#         data = {'vote_name':vote.name}
#         opts = {}
#         for opt in vote.options:
#             opts[opt.name] = opt.value
#
#         data['options'] = opts
#         id = getSocketIdProject().AsyncResult().get(timeout=1.0)
#
#         ws.send(str(data))
#
#
#
# def sendData(id):
#     vote = Vote.query.filter_by(id=id).first_or_404()
#     for w in socket_users.get(id):
#         data = {'vote_name':vote.name}
#         opts = {}
#         for opt in vote.options:
#             opts[opt.name] = opt.value
#         data['options'] = opts
#         w.send(str(data))
