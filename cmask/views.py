from cmask.form import VoteForm
from app import db, redis, app
from flask import Blueprint, request, redirect, url_for, flash
from flask.ext.login import current_user, current_app
from flask.templating import render_template
from cmask.models import Vote, VoteOption
from settings import REDIS_CHAN

mod = Blueprint('views', __name__, template_folder='template', static_folder='static/', static_url_path='/assets')


@mod.route('/')
def index():
    return render_template('index.html')


@mod.route('/create', methods=['get', 'post'])
def create():
    if (not current_user.is_authenticated() or not current_user.can_create()) and app.config['ALLOW_CREATE_ALL'] == False:
        return redirect(url_for('.questions'))

    form = VoteForm()
    if request.method == 'POST' and form.validate():
        if request.form['name'] =='':
            flash('Vous devez indiquer le nom ', 'error')
            return render_template('create.html', **locals())
        vote = Vote()
        vote.name = request.form['name']
        p = request.form.get('personalized') if True is not None else False
        pe = False
        if type(p) == str or type(p) == unicode:
            if p == 'y':
                pe = True

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
            count = 0
            for elem in request.form:
                if 'perso' in elem and not elem == 'personalized':
                    if request.form.get(elem) != '':
                        count += 1
                        opt = VoteOption()
                        opt.name = request.form.get(elem)
                        opt.vote = vote
                        db.session.add(opt)

            if count >= 2:
                db.session.commit()
            else:
                db.session.rollback()
                db.session.delete(vote)
                db.session.commit()
                flash('Minimum 2 choix a indiquer ! ', 'error')
                return render_template('create.html', **locals())


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
    if cookie:
        return redirect(url_for('.result', id=id))

    return render_template('view.html', **locals())


@mod.route('/<id>/vote/<option>')
def vote(id, option):

    db.session.flush()
    voteOption = VoteOption.query.filter_by(id=option).first_or_404()

    response = app.make_response(redirect(url_for('.result', id=id)))
    cookie = ('vote-'+id) in request.cookies

    if not cookie:
        voteOption.value = voteOption.value +1
        db.session.commit()
        message = {"id":str(id),"slug":str(voteOption.slug()),"value":int(voteOption.value), 'did':int(voteOption.id)}
        redis.publish(REDIS_CHAN, message)

        response.set_cookie('vote-' + str(id), voteOption.slug())
    return response



@mod.route('/<id>/result')
def result(id):
    vote = Vote.query.filter_by(id=id).first_or_404()
    socket_url = app.config['SOCKET_HOST']
    legendTemplate = "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<segments.length; i++){%><li><span style=\"background-color:<%=segments[i].fillColor%>\"></span><%if(segments[i].label){%><%=segments[i].label%><%}%></li><%}%></ul>"


    return render_template('result.html', **locals())