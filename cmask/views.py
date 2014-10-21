from cmask.form import VoteForm
from app import db, redis, app
from flask import Blueprint, request, redirect, url_for
from flask.templating import render_template
from cmask.models import Vote, VoteOption
from settings import REDIS_CHAN

mod = Blueprint('views', __name__, template_folder='template', static_folder='static/', static_url_path='/assets')


@mod.route('/')
def index(): 
    return render_template('index.html')


@mod.route('/create', methods=['get', 'post'])
def create():

    form = VoteForm()
    print(request.method)
    if request.method == 'POST' and form.validate():
        vote = Vote()
        vote.name = request.form['name']
        p = request.form.get('personalized') if True is not None else False
        pe = False
        if type(p) == str or type(p) == unicode:
            if p == 'y':
                pe = True

        vote.personalized = pe
        db.session.add(vote)
        db.session.commit()
        if not pe:
            vTrue  = VoteOption()
            vTrue.name = 'Vrai'
            vTrue.vote = vote

            vFalse  = VoteOption()
            vFalse.name = 'Faux'
            vFalse.vote = vote

            db.session.add(vFalse)
            db.session.add(vTrue)
            db.session.commit()

        else:
            for elem in request.form:
                if 'perso' in elem and not elem == 'personalized':
                    if request.form.get(elem) != '':
                        opt = VoteOption()
                        opt.name = request.form.get(elem)
                        opt.vote = vote
                        db.session.add(opt)
                        db.session.commit()

        return redirect(url_for('.view', id=vote.id))

    
    return render_template('create.html', **locals())

@mod.route('/questions')
def questions():
    votes = Vote.query.all()
    
    return render_template('questions.html', **locals())
    

@mod.route('/<id>')
def view(id):
    vote = Vote.query.filter_by(id=id).first_or_404()

    response = app.make_response(redirect(url_for('.result', id=id)))
    cookie = ('vote-'+id) in request.cookies
    print('cookie=',request.cookies, cookie)

    if cookie:
        return redirect(url_for('.result', id=id))

    return render_template('view.html', **locals())


@mod.route('/<id>/vote/<option>')
def vote(id, option):



    db.session.flush()
    voteOption = VoteOption.query.filter_by(id=option).first_or_404()

    response = app.make_response(redirect(url_for('.result', id=id)))
    cookie = ('vote-'+id) in request.cookies
    print('cookie=',request.cookies, cookie)

    if not cookie:
        voteOption.value = voteOption.value +1
        db.session.commit()
        print(voteOption.vote.name.encode('utf-8'))
        message = {'id':str(id),'slug':str(voteOption.slug()),'value':voteOption.value}
        print(message)
        redis.publish(REDIS_CHAN, message)

        response.set_cookie('vote-' + str(id), voteOption.slug())
    return response



@mod.route('/<id>/result')
def result(id): 
    vote = Vote.query.filter_by(id=id).first_or_404()

    legendTemplate = "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<segments.length; i++){%><li><span style=\"background-color:<%=segments[i].fillColor%>\"></span><%if(segments[i].label){%><%=segments[i].label%><%}%></li><%}%></ul>"

    return render_template('result.html', **locals())