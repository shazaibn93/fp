from app import app
from .forms import PlayerForm, CompareForm, LoginForm, RegisterForm, EditProfileForm
from app.models import Player, User, Usersplayers, Stats
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required
import requests


@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html.j2')

@app.route('/delete/<int:id>', methods=['GET'])
@login_required
def remove(id):
    user = current_user
    theplayer = Usersplayers().query.filter_by(user_id = user.id,player_id = id).first() 
    theplayer.delete()
    error_string = 'You have removed player from the squad, they will be missed', 'warning'
    return redirect(url_for('team', error = error_string))

@app.route('/comparison', methods=['GET'])
@login_required
def comparison():
    return render_template('comparison.html.j2', team = current_user.squad)

@app.route('/team', methods=['GET'])
@login_required
def team():
    user = current_user
    team_list = user.squad
    stats=Stats().query.filter_by(user_id = user.id).all()
    return render_template('team.html.j2', teamlist = team_list, stats=stats, Stats=Stats())

@app.route('/world', methods=['GET'])
@login_required
def world():
    return render_template('world.html.j2', users = User.query.all(), Stats=Stats(), Players = Player())

# @app.route('/addtoteam/<int:id>', methods=['GET','POST'])
# def addtoteam(id):
#     plyr = Player.existsid(id)
#     user = current_user
#     team = Usersplayers().query.filter_by(user_id = user.id).all()
#     team_list = []
#     for pid in team:
#         team_list.append(Player.existsid(pid.player_id))
#     stats=Stats().query.filter_by(user_id = user.id).all()
#     if user.team_full():
#         if Usersplayers().query.filter_by(user_id = user.id,player_id = id).first():
#             error_string = "This player is already on your team"
#             return render_template('compare.html.j2', error = error_string, form = CompareForm())
#         else:
#             user.add_to_team(plyr)
#             user.save()
#             print(team_list)
#             print(stats)
#             return render_template('comparison.html.j2', players = team_list, stats=stats)
#     else:
#         error_string = "Your team is full"
#         return render_template('compare.html.j2', error = error_string, form = CompareForm())

@app.route('/addtoteam/<int:id>', methods=['GET','POST'])
@login_required
def addtoteam(id):
    plyr = Player.existsids(id)
    user = current_user
    team_list = user.squad
    stats=Stats().query.filter_by(user_id = user.id).all()
    if user.team_full():
        if Usersplayers().query.filter_by(user_id = user.id,player_id = id).first():
            error_string = "This player is already on your team"
            return render_template('team.html.j2', error = error_string, form = CompareForm(), Stats=Stats())
        else:
            user.add_to_team(plyr)
            user.save()
            print(team_list)
            print(stats)
            return render_template('team.html.j2', teamlist = team_list, stats=stats, Stats=Stats())
    else:
        error_string = "Your team is full"
        return render_template('team.html.j2', teamlist = team_list, error = error_string, Stats=Stats())

@app.route('/player', methods=['GET','POST'])
@login_required
def player():
    form=PlayerForm()
    if form.validate_on_submit():
        player = request.form.get('player').title()
        print(Player.exists(player))
        if Player.exists(player):
            return render_template('player.html.j2', form=form, player = Player.exists(player) )
        else:
            error_string = "Houston We Have a Problem"
            return render_template('player.html.j2', form=form, error = error_string)
    return render_template('player.html.j2', form=form)

@app.route('/compare', methods=['GET','POST'])
@login_required
def compare():
    form=CompareForm()
    if request.method == 'POST' and form.validate_on_submit():
        # contact the api and get the name of the pokemon from the form
        season1 = request.form.get('season1')
        player1 = request.form.get('player1').title()
        season2 = request.form.get('season2')
        player2 = request.form.get('player2').title()
        myplayer1 = Player.exists(player1)
        myplayer2 = Player.exists(player2)
        url1 = f"https://www.balldontlie.io/api/v1/season_averages?season={season1}&player_ids[]={myplayer1.main_id}"
        url2 = f"https://www.balldontlie.io/api/v1/season_averages?season={season2}&player_ids[]={myplayer2.main_id}"
        response1 = requests.get(url1)
        response2 = requests.get(url2)
        me=current_user
        if response1.ok and response2.ok:
            myl = []
            newl = []
            slist = [season1,season2]
            szn=0
            newl.append(response1.json()['data'])
            newl.append(response2.json()['data'])
            print(newl)
            for i in newl:
                print(i)
                myl.append({
                    "main_id":i[0]['player_id'],
                    "name":Player.existsids(i[0]['player_id']).full_name,
                    "team":Player.existsids(i[0]['player_id']).team,
                    "height":Player.existsids(i[0]['player_id']).height,
                    "ppg":i[0]['pts'],
                    "rpg":i[0]['reb'],
                    "apg":i[0]['ast'],
                    "mpg":i[0]['min'],
                    "spg":i[0]['stl'],
                    "bpg":i[0]['blk'],
                    "tpg":i[0]['turnover'],
                    "pf":i[0]['pf'],
                    "fgpct":int((i[0]['fg_pct'])*100),
                    "fgtpct":int((i[0]['fg3_pct'])*100),
                    "ftpct":int((i[0]['ft_pct'])*100),
                    "games":i[0]['games_played'],
                    "jersey":Player.existsids(i[0]['player_id']).jersey,
                    "pic":Player.existsids(i[0]['player_id']).pic,
                    "team_pic":Player.existsids(i[0]['player_id']).team_pic,
                    "team_color":Player.existsids(i[0]['player_id']).team_color,
                    "position":Player.existsids(i[0]['player_id']).position,
                    "season":slist[szn]  
                })

                stats_dict = {
                    "main_id":i[0]['player_id'],
                    "season":slist[szn],
                    "ppg":i[0]['pts'],
                    "rpg":i[0]['reb'],
                    "apg":i[0]['ast'],
                    "mpg":i[0]['min'],
                    "spg":i[0]['stl'],
                    "bpg":i[0]['blk'],
                    "tpg":i[0]['turnover'],
                    "pf":i[0]['pf'],
                    "fgpct":int((i[0]['fg_pct'])*100),
                    "fgtpct":int((i[0]['fg3_pct'])*100),
                    "ftpct":int((i[0]['ft_pct'])*100),
                    "games":i[0]['games_played'],
                    "user_id":me.id
                }
                stats = Stats()
                stats.from_dict(stats_dict)
                stats.save()
                szn+=1
            return render_template('comparison.html.j2', form=form, players = myl)
        else:
            error_string = "Houston We Have a Problem"
            return render_template('compare.html.j2', form=form, error = error_string)
    return render_template('compare.html.j2', form=form)




from .forms import LoginForm, RegisterForm, EditProfileForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required
from flask import Flask, render_template, request, flash, redirect, url_for
import requests

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        #We will do the login stuff here
        email = request.form.get('email').lower()
        password = request.form.get('password')
        U = User.query.filter_by(email=email).first() #Left is column, right is variable
        if U and U.check_hashed_password(password):
            login_user(U)
            return redirect(url_for('index'))
        return render_template('login.html.j2', form = form)
    return render_template('login.html.j2', form = form)

@app.route('/logout')
@login_required
def logout():
    if current_user:
        logout_user()
        return redirect(url_for('login'))

@app.route('/register',methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        #Create a new user 
        try:
            new_user_data = {
                "first_name":form.first_name.data.title(),
                "last_name":form.last_name.data.title(),
                "email":form.email.data.lower(),
                "password":form.password.data
            }
            #creating an empty user 
            new_user_object = User()
            new_user_object.from_dict(new_user_data)
            new_user_object.save()
        except:
            flash("We ran into an error ",'danger')
            #Error Return
            return render_template('register.html.j2', form=form)
        # If it worked
        flash('You have successfully registered', 'success')
        return redirect(url_for('login'))
    #Get Return
    return render_template('register.html.j2', form=form)

@app.route('/editprofile', methods= ['GET', 'POST'])
@login_required
def editprofile():
    form = EditProfileForm
    if request.method == 'Post' and form.validate_on_submit():
        new_user_data = {
            "first_name":form.first_name.data.title(),
                "last_name":form.last_name.data.title(),
                "email":form.email.data.lower(),
                "password":form.password.data
        }
        user = User.query.filter_by(email = form.email.data.lower()).first()
        if user and user.email != current_user.email:
            flash('Email already in use','danger')
            return redirect(url_for('auth.edit_profile'))
        try:
            current_user.from_dict(new_user_data)
            current_user.save()
            flash('Profile Updated', 'success')
        except:
            flash('Something went wrong. Surprisingly, not your fault','danger')
            return redirect(url_for('edit_profile'))
        return redirect(url_for('main.index'))
    return render_template('register.html.j2', form=form)

# @app.route('/scrap', methods=['GET', 'POST'])
# def scrap():
#     s=360
#     while s < 3000:
#         for i in range(s,3092):
#             # contact the api and get the name of the pokemon from the form
#             url = f"https://www.balldontlie.io/api/v1/players/{i}"
#             response = requests.get(url)
#             if response.ok:
#                 player_dict={
#                     "main_id":response.json()['id'],
#                     "first_name":response.json()['first_name'],
#                     "last_name":response.json()['last_name'],
#                     "full_name":str(response.json()['first_name'])+" "+str(response.json()['last_name']),
#                     "position":response.json()['position'],
#                     "team":response.json()['team']['full_name'],
#                     "height":(str(response.json()['height_feet'])+"'"+str(response.json()['height_inches'])),
#                     "weight":response.json()['weight_pounds']
#                 }

#                 # if not Player.exists(player_dict['main_id']):
#                 importplayer = Player()
#                 importplayer.from_dict(player_dict)
#                 importplayer.save()
                
#         s+=60
#     return render_template('index.html.j2')

# @app.route('/clean', methods=['GET', 'POST'])
# def clean():
#     for i in range(1,3092):
#         print("testing "+ str(i))
#         if not Player.exists(i):
#             print("We are getting "+ str(i))
#             # contact the api and get the name of the pokemon from the form
#             url = f"https://www.balldontlie.io/api/v1/players/{i}"
#             response = requests.get(url)
#             if response.ok:
#                 player_dict={
#                     "main_id":response.json()['id'],
#                     "first_name":response.json()['first_name'],
#                     "last_name":response.json()['last_name'],
#                     "full_name":str(response.json()['first_name'])+" "+str(response.json()['last_name']),
#                     "position":response.json()['position'],
#                     "team":response.json()['team']['full_name'],
#                     "height":(str(response.json()['height_feet'])+"'"+str(response.json()['height_inches'])),
#                     "weight":response.json()['weight_pounds']
#                 }

#                 # if not Player.exists(player_dict['main_id']):
#                 importplayer = Player()
#                 importplayer.from_dict(player_dict)
#                 importplayer.save()
#     return render_template('index.html.j2')

# @app.route('/player', methods=['GET','POST'])
# def player():
#     form=PlayerForm()
#     if request.method == 'POST' and form.validate_on_submit():
#         # contact the api and get the name of the pokemon from the form
#         player = request.form.get('player')
#         url = f"https://www.balldontlie.io/api/v1/players/{player}"
#         response = requests.get(url)
#         if response.ok:
#             player_dict={
#                 "main_id":response.json()['id'],
#                 "first_name":response.json()['first_name'],
#                 "last_name":response.json()['last_name'],
#                 "full_name":str(response.json()['first_name'])+" "+str(response.json()['last_name']),
#                 "position":response.json()['position'],
#                 "team":response.json()['team']['full_name'],
#                 "height":(str(response.json()['height_feet'])+"'"+str(response.json()['height_inches'])),
#                 "weight":response.json()['weight_pounds']
#             }

#             if not Player.exists(player_dict['main_id']):
#                 importplayer = Player()
#                 importplayer.from_dict(player_dict)
#                 importplayer.save()
            
#             return render_template('player.html.j2', form=form, player = player_dict )
#         else:
#             error_string = "Houston We Have a Problem"
#             return render_template('player.html.j2', form=form, error = error_string)
#     return render_template('player.html.j2', form=form)

# @app.route('/scrap2', methods=['GET', 'POST'])
# def scrap2():
#     for i in range(2021,2022):
#         #contact the api and get the name of the pokemon from the form
#         url = f"https://data.nba.net/data/10s/prod/v1/{i}/players.json"
#         response = requests.get(url)
#         if response.ok:
#             print("Response is okay")
#             for z in response.json()['league']['standard']:
#                 print('trying')
#                 api_full_name = str(z['firstName'])+  " " + str(z['lastName'])
#                 if Player.exists(api_full_name) and  len(z['teams']) > 0:
#                     theplayer = Player.exists(api_full_name)
#                     player_dict={
#                         "nba_id":z['personId'],
#                         "jersey":z['jersey'],
#                         "year":z['teams'][0]['seasonStart']
#                     }
#                     if theplayer.main_id not in [3078,2064,395,2063,1145] and not theplayer.nba_id:  
#                         theplayer.add_dict(player_dict)
#                         theplayer.save()
#                         print('saved')
#         print(str(i)+" just finished")
    
#     return render_template('index.html.j2')

# @app.route('/scrap3', methods=['GET', 'POST'])
# def scrap3():
#     for i in range(3092,3093):
#         tester = Player.existsid(i)
#         if tester.nba_id:    
#             url = f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{tester.nba_id}.png"
#             tester.add_pic(url)
#             tester.save()
#             print(str(i)+" just finished")
        
#     return render_template('index.html.j2')               