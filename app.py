from datetime import datetime
from flask import Flask, render_template, url_for, request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import func
from sqlalchemy import text
from random import shuffle

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tournaments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'True'
app.secret_key = 'queijo'
db = SQLAlchemy(app)

class Tournaments(db.Model):
    __tablename__ = 'tournaments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Tournament %r>' % self.id


class Matchs(db.Model):
    __tablename__ = 'matchs'
    id = db.Column(db.Integer, primary_key =True)
    match_number =  db.Column(db.Integer)
    Tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'),nullable = False)
    tournaments = db.relationship("Tournaments", backref = db.backref("tournaments",uselist = False))
    challenger_1 = db.Column(db.String(200),nullable = False)
    challenger_2 = db.Column(db.String(200),nullable = False)
    score_1 = db.Column(db.Integer)
    score_2 = db.Column(db.Integer)
    status = db.Column(db.String(10), nullable = False)

    def __repr__(self):
        return '<Match %r>' % self.id

class Challengers(db.Model):
    __tablename__ = 'challengers'
    id = db.Column(db.Integer, primary_key =True)
    name = db.Column(db.String(200),nullable = False)
    Tournament_id = db.Column(db.Integer, db.ForeignKey('tournaments.id'),nullable = False)
    tournaments2 = db.relationship("Tournaments", backref = db.backref("tournaments2",uselist = False))
   # matchs = db.relationship("Matchs", backref = db.backref("matchs",uselist = False))
   # Match_id = db.Column(db.Integer, db.ForeignKey('matchs.id'),nullable = False)
   # matchs = db.relationship("matchs", backref = db.backref("matchs",uselist = False))

    def __repr__(self):
        return '<Challenger %r>' % self.id

@app.route('/',methods=['POST','GET'])
def index():
    return render_template('index.html')


@app.route('/tournaments/', methods=['POST','GET'])
def tournaments():
    if request.method == 'POST':
        task_content = request.form.get('tournament')
        search = Tournaments.query.filter_by(name=str(task_content)).first()
        if search == None:  
            new_task = Tournaments(name=str(task_content)) 
            try:
                db.session.add(new_task)
                db.session.commit()
                flash('Tournament created')
                return redirect('/tournaments/')
            except:
                return flash('There was an issue adding your task')
        else:
             return flash('Already exists')
    else:
            tasks = Tournaments.query.order_by(Tournaments.date_created).all()
            return  render_template('tournaments.html', Tournaments = tasks) 

@app.route('/tournaments/<int:id>', methods = ['POST','GET'])
def tournament(id): 
    if request.method == "GET":
        tasks = Matchs.query.filter_by(Tournament_id = id).all()
        if tasks != []:
            return render_template('tournament.html', Matchs = tasks)
        else:
            return flash("There are no matches yet")

@app.route('/tournaments/update/<int:id>')
def update_tournament(id): 
    task = request.form.get("form")
    print(task)
    try:
        update_data = Tournaments.query.filter_by(id = id).all()
        db.session.commit()
        return redirect('/tournaments/')
    except:
        return flash("There was a problem deleting the tournament" )

@app.route('/tournaments/delete/<int:id>')
def delete_tournament(id): 
    try:
        db.session.delete(Tournaments.query.get_or_404(id))
        db.session.commit()
        return redirect('/tournaments/')
    except:
        return flash("there was a problem deleting the tournament" )

@app.route('/matchs/', methods= ['POST','GET'])
def matchs():
    if request.method == 'GET':  
        arc = Challengers.query.order_by(Challengers.Tournament_id).all()
        arm = Matchs.query.order_by(Matchs.match_number)
        sumc = 0
        summ = 0
        for item in arc:
            sumc += 1
        for item in arm:
            summ += 1
        if (sumc - summ) > 0:
            idt = Challengers.query.distinct(Challengers.Tournament_id)

            for id in idt:
                challengers  = Challengers.query.filter_by(Tournament_id = id.Tournament_id).all()
                if (sumc % 2) == 0:
                    cont = 1
                    while challengers != []:
                        shuffle(challengers)

                        number_1 = challengers[0].name
                        number_2 = challengers[1].name
                        
                        check_1 = Matchs.query.filter_by(Tournament_id = id.Tournament_id, challenger_1 = number_1, challenger_2 = number_2).all()
                        check_2 = Matchs.query.filter_by(Tournament_id = id.Tournament_id, challenger_1 = number_2, challenger_2 = number_1).all()
                        
                        if check_1 == [] and check_2 == []:
                            new_task = Matchs(match_number = cont,Tournament_id = id.Tournament_id, challenger_1 = number_1, challenger_2 = number_2, score_1 = 0, score_2 = 0, status = "on game")
                            try:
                                db.session.add(new_task)
                                db.session.commit()
                            except:
                                return flash("Error on matchmaking")
                        challengers.pop(0)
                        challengers.pop(0)
                        
                        
                        cont += 1
                    tasks = Matchs.query.order_by(Matchs.Tournament_id).all()
                    return render_template('matchs.html',Matchs = tasks)
                else:
                    if (sumc % 2) == 0:
                        cont = 1
                        while len(challengers) != 1:
                            shuffle(challengers)

                            number_1 = challengers[0].name
                            number_2 = challengers[1].name
                            
                            check_1 = Matchs.query.filter_by(Tournament_id = id.Tournament_id, challenger_1 = number_1, challenger_2 = number_2).all()
                            check_2 = Matchs.query.filter_by(Tournament_id = id.Tournament_id, challenger_1 = number_2, challenger_2 = number_1).all()
                            
                            if check_1 == [] and check_2 == []:
                                new_task = Matchs(match_number = cont,Tournament_id = id.Tournament_id, challenger_1 = number_1, challenger_2 = number_2, score_1 = 0, score_2 = 0, status = "on game")
                                try:
                                    db.session.add(new_task)
                                    db.session.commit()
                                except:
                                    return flash("Error on matchmaking")
                            challengers.pop(0)
                            challengers.pop(0)
                            cont += 1

                    tasks = Matchs.query.order_by(Matchs.Tournament_id).all()
                    return render_template('matchs.html',Matchs = tasks)
                    
        else:
            tasks = Matchs.query.order_by(Matchs.Tournament_id).all()
            return render_template('matchs.html',Matchs = tasks)

@app.route('/tournaments/match/update/<int:id>')
def update_match(id): 
    try:
        db.session.delete(Matchs.query.get_or_404(id))
        db.session.commit()
        return redirect('/matchs/')
    except:
        return flash("there was a problem deleting the match" )

@app.route('/tournaments/match/delete/<int:id>')
def delete_match(id): 
    try:
        db.session.delete(Matchs.query.get_or_404(id))
        db.session.commit()
        return redirect('/matchs/')
    except:
        return flash("there was a problem deleting the match" )







@app.route('/challengers/', methods= ['POST','GET'])
def challenger():
    if request.method == 'POST':
        task_content = request.form.get('match')    
    else:
        tasks = Challengers.query.order_by(Challengers.name).all()
        return render_template('challengers.html', Challengers = tasks)

@app.route('/tournaments/<int:id>/challenger/create', methods=['POST','GET'])
def join_tournament(id):
    if request.method == 'POST':
        task_content = request.form.get('challenger')
        print(task_content)
        search = Challengers.query.filter_by(name=str(task_content)).first()
        if search == None:   
            new_task = Challengers(name=str(task_content),Tournament_id = id) 
            try:
                db.session.add(new_task)
                db.session.commit()
                flash('Joined with sucess')
                return redirect('/tournaments/' )
            except:
                flash('There was an issue adding your task')
                return redirect('/tournaments/' )
        else:
             flash('Already exists')
             return redirect('/tournaments/' )
    else:
            tasks = Tournaments.query.order_by(Tournaments.date_created).all()
            return  render_template('tournaments.html', Tournaments = tasks)




if __name__ == "__main__": 
    app.run(debug=True)