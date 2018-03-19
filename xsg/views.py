import os
import time
import json
import pickle
import atexit
from math import floor, inf
from xsg.json_pprint import MyEncoder
from xsg import game, app
from flask import request, session, redirect, url_for, render_template, flash, jsonify, Response, send_from_directory
import logging
from logging.handlers import RotatingFileHandler


################################################################################
# Logging setup
################################################################################
logging.basicConfig(level=logging.DEBUG,format='%(name)-12s|%(message)s')
file_log = RotatingFileHandler(filename='./instance/server.log', maxBytes=1048576, backupCount=9)
file_log.setLevel(logging.DEBUG)
file_log.setFormatter(logging.Formatter('%(asctime)s|%(name)-12s|%(message)s'))
logging.getLogger().addHandler(file_log)
logger = logging.getLogger(__name__)


def log_msg(msg: str):
    logger.warning(msg)


def show_error(m: str, e: Exception):
    template = "   Error: {0}. Exception of type {1} occurred. Arguments:{2!r}."
    message = template.format(m, type(e).__name__, e.args)
    log_msg(message)
    flash(message)


################################################################################
# flask setup
################################################################################
log_msg('****** XSG server started')
log_msg('   Local working folder location: ' + os.getcwd())
log_msg('   Current instance location:     ' + app.instance_path)
app.config.from_object(__name__)  # load config from this file
try:
    with open('./xsg/config.json') as config_file:  # Load default config and override config from an environment variable
        config_data = json.load(config_file)
    log_msg('   Read config from ' + os.getcwd() + '/xsg/config.json')
except Exception as e:
    show_error('Error in reading XSG\'s config file',e)
config_data['GameStatusData'] = os.path.join(app.instance_path, config_data['GameStatusData'])
app.secret_key = config_data['SECRET_KEY']  # set the secret key for 'session'
app.config.update(config_data)
app.config.from_envvar('XSG_SETTINGS', silent=True)
SecondsAway_to_Disconnect = int(config_data['SECONDSAWAY_TO_DISCONNECT'])
ALLOWED_EXTENSIONS = set(['json'])

GAMES = {}


################################################################################
# output formating & utility functions
################################################################################
@atexit.register  # this won't work in Flask-debug-mode as the restart process will change the variable ID
def cleanup():
    if save_games_state():
        log_msg('Saved games state. Server shutting down...')
    else:
        log_msg('Failed to save games state. Server shutting down...')


def kill_expired_games():
    d = []
    for k,v in GAMES.items():
        if (time.time() - v.created)/86400 > v.expiry:  # 86400 second in a day
            d.append(k)
    if len(d) > 0:
        log_msg("The following game(s) expired and will be deleted: {:}.".format(str(d)))
        for k in d:
            del GAMES[k]


def save_games_state():
    kill_expired_games()
    with open(app.config['GameStatusData'],'wb') as f:
        pickle.dump(GAMES,f)
        return True
    return False


def load_games_state():
    if os.path.isfile(app.config['GameStatusData']):
        with open(app.config['GameStatusData'],'rb') as f:
            GAMES.clear()
            GAMES.update(pickle.load(f))
            kill_expired_games()
            return True
    else:
        log_msg('   previous gastate file not found: ' + app.config['GameStatusData'])
    return False


# loading previous server game state data if existing
load_games_state()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def list_avg(x):
    if len(x) == 0:
        return 0
    else:
        return sum(x)/len(x)


def toHTMLtbl(x):
    if type(x) is list:
        return ' ' + str(x).replace('\'','').replace('[','').replace(']','').replace('(','<tr><td>')\
            .replace('), ','</td></tr>').replace(', ','</td><td>').replace(')','</td></tr>')


def txt2list(l):
    try:
        return [inf if x == 'Infinity' else int(x) for x in l.split(',')]
    except Exception as e:
        msg = "Could not convert text list '{:}' to numeric list. Exception {:} - {:!r}.".format(l,type(e).__name__, e.args)
        log_msg(msg)
        raise ValueError(msg)


def show_week(D,week):
    """show a given week's values as a dict"""
    r = {}
    for k,v in D.items():
        r[k] = v[week]
    return r


def week_sum(D,week):
    """ return a week's sum from a dictionary of lists of weekly values """
    return sum([x[week] for x in D.values()])


################################################################################
# application views
################################################################################
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'robots.txt', mimetype='text/plain')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/cmd/<cmd>')
def cmd(cmd):
    if cmd == 'index':
        return redirect(url_for('index'))
    if cmd == 'about':
        return render_template('about.html')
    if cmd == 'logout':
        session.pop('username',None)
        session.pop('password',None)
        return redirect(url_for('cmd',cmd='reset'))
    if cmd == 'reset':
        session.pop('player_name',None)
        session.pop('selected_game',None)
        session.pop('selected_station',None)
        return redirect(url_for('index'))
    if cmd == 'import_game':
        return render_template('import_game.html')
    if cmd == 'advanced_menu':
        return render_template('advanced_menu.html')
    if cmd == 'admin_game_start':
        return select_game_page(text='Select a game, and fill in the game\'s admin password:',next_page='admin_game', ask_name=False, ask_password=True)
    if cmd == 'join_game':
        return select_game_page(text='Select the game you like to join, and fill in your info:',next_page='join_station', ask_name=True, ask_password=True)
    if cmd == 'create_game_from_template':
        templates = [x.rsplit('.',1)[0] for x in os.listdir('./game_templates/')]
        return render_template('create_game_from_template.html', data=templates)
    if cmd == 'monitor_games':
        kill_expired_games()
        return render_template('multi-game-select.html', games_list=[' ']+[x.team_name for x in GAMES.values()])
    if cmd == 'under_construction':
        return 'Sorry, this part is still under construction'
    return "Unknown cmd: " + cmd


# direct entry point, not reachable through WUI
@app.route('/admin')
def admin_server_start():
    if 'password' in session.keys() and 'username' in session.keys():
        if app.config['USERNAME'] == session['username'] and app.config['PASSWORD'] == session['password']:
            return redirect(url_for('admin_server_menu'))
    return render_template('admin_password.html')


@app.route('/admin_server_menu', methods=['POST','GET'])
def admin_server_menu():
    if request.method == 'GET':
        if 'password' in session.keys() and 'username' in session.keys():
            if app.config['USERNAME'] != session['username']:
                flash('User is not an admin!')
                return redirect(url_for('admin_server_start'))
            if app.config['PASSWORD'] != session['password']:
                flash('Incorrect password!')
                return redirect(url_for('admin_server_start'))
        else:
            return redirect(url_for('admin_server_start'))
    elif request.method == 'POST':
        if app.config['USERNAME'] != request.form['username']:
            flash('User is not an admin!')
            return redirect(url_for('admin_server_start'))
        if app.config['PASSWORD'] != request.form['password']:
            flash('Incorrect password!')
            return redirect(url_for('admin_server_start'))
        session['username'] = request.form['username']
        session['password'] = request.form['password']
    return render_template('admin_server_menu.html')


@app.route('/demo')
def demo():
    demo_filename = './game_templates/5 stations 1 player Demo.json'
    kill_expired_games()
    import random
    id = '{:03d}'.format(random.randint(1, 999))
    while 'demo_'+id in GAMES.keys():
        id = '{:03d}'.format(random.randint(1, 999))
    if os.path.isfile(demo_filename):
        try:
            with open(demo_filename) as game_file:
                game_data = json.load(game_file)
            game_data['team_name'] = 'demo_'+id
            game_data['play_password'] = id
            game_data['admin_password'] = id
            GAMES[game_data['team_name']] = game.Game(game_data)
            session['player_name'] = 'DemoPlayer'
            session['selected_game'] = game_data['team_name']
            session['selected_station'] = 'wholesaler'
            return render_template('demo_start.html', id=id)
        except Exception as e:
            if game_data['team_name'] in GAMES.keys():
                del GAMES[game_data['team_name']]
            show_error("Could not create demo game",e)
    else:
        flash('Demo game JSON file not found.')
    return redirect(url_for('index'))


@app.route('/admin_game', methods=['POST','GET'])
def admin_game():
    if request.method == 'GET':
        if 'selected_game' in session.keys():
            this_game = session['selected_game']
        else:
            this_game = ''
        if this_game not in GAMES.keys():
            flash('Previous game is no longer valid. Please select another game.')
            return redirect(url_for('cmd',cmd='admin_game_start'))
    if request.method == 'POST':
        this_game = request.form.get('selected_game')
        if this_game == '** No games created yet! **':
            return redirect(url_for('index'))
        if this_game not in GAMES.keys():
            flash('Selected game is no longer valid. Please select another game.')
            return redirect(url_for('cmd',cmd='admin_game_start'))
        if GAMES[this_game].admin_password != request.form['password']:
            flash('Incorrect password!')
            return redirect(url_for('cmd',cmd='admin_game_start'))
        session['selected_game'] = this_game
    return render_template('admin_game.html', game=this_game)


@app.route('/join_station', methods=['POST','GET'])
def join_station():
    if request.method == 'GET':
        if 'selected_game' in session.keys():
            this_game = session['selected_game']
        else:
            this_game = ''
        if this_game not in GAMES.keys():
            flash('Selected game is no longer valid. Please select another game.')
            return redirect(url_for('cmd', cmd='join_game'))
    if request.method == 'POST':
        this_game = request.form.get('selected_game')
        if this_game == '** No games created yet! **':
            return redirect(url_for('index'))
        if this_game not in GAMES.keys():
            flash('Selected game is no longer valid. Please select another game.')
            return redirect(url_for('cmd',cmd='join_game'))
        if GAMES[this_game].play_password != request.form['password']:
            flash('Incorrect password!')
            return redirect(url_for('cmd',cmd='join_game'))
        session['player_name'] = request.form['player_name']
        session['selected_game'] = this_game
    if GAMES[this_game].manual_stations_names:
        return select_station_page(text='Select your game station:',game_name=this_game,next_page='play_screen')
    else:
        if GAMES[this_game].Run():
            flash('Game simulation complete. (All stations are fully automated, see game config)')
        else:
            flash('Game already simulated. Nothing done.')
        return redirect(url_for('index'))


@app.route('/play_screen', methods=['POST','GET'])
def play_screen():
    if request.method == 'GET':  # when user reloads page
        pass
    if request.method == 'POST':
        if request.form.get('selected_station') == '** Sorry, this game has no available stations remaining! **':
            return redirect(url_for('cmd',cmd='join_game'))
        else:
            session['selected_station'] = request.form.get('selected_station')
    if 'selected_game' in session.keys() and 'selected_station' in session.keys():
        this_game = session['selected_game']
        this_station = session['selected_station']
    else:
        this_game = ''
        this_station = ''
    if this_game not in GAMES.keys():
        flash('Game is no longer valid, please try again.')
        return redirect(url_for('cmd',cmd='join_game'))
    if this_station not in GAMES[this_game].network_stations.keys():
        flash('Station is no longer valid, please try again.')
        return redirect(url_for('join_station'))
    if this_station not in GAMES[this_game].manual_stations_names:
        flash('Station has been switched to autopilot, please select another game/station.')
        return redirect(url_for('join_station'))
    if 'player_name' not in session.keys():
        session['player_name'] = ''
    if GAMES[this_game].network_stations[this_station].player_name == session['player_name']:
        GAMES[this_game].network_stations[this_station].touch()
    elif time.time() - GAMES[this_game].network_stations[this_station].last_communication_time > SecondsAway_to_Disconnect:
        GAMES[this_game].network_stations[this_station].touch()
        GAMES[this_game].network_stations[this_station].player_name = session['player_name']
    else:
        flash('Station already selected by another player. Please try again.')
        return redirect(url_for('join_station'))
    static_info = {'weeks':GAMES[this_game].weeks,
                   'current_week':GAMES[this_game].current_week,
                   'turn_time': GAMES[this_game].turn_time,
                   'number_of_players': len(GAMES[this_game].manual_stations_names),
                   'secondsaway_to_disconnect':SecondsAway_to_Disconnect,
                   'suppliers':[x.station_name for x in GAMES[this_game].network_stations[this_station].suppliers],
                   'customers':[x.station_name for x in GAMES[this_game].network_stations[this_station].customers],
                   'auto_ship':GAMES[this_game].network_stations[this_station].auto_decide_ship_qty,
                   'auto_order':GAMES[this_game].network_stations[this_station].auto_decide_order_qty,
                   'game_info':'<tr><td>' + str(GAMES[this_game].network_stations[this_station].holding_cost) + '</td><td>holding cost ($/unit)</td></tr>' +
                               '<tr><td>' + str(GAMES[this_game].network_stations[this_station].backorder_cost) + '</td><td>backorder cost ($/unit)</td></tr>' +
                               '<tr><td>' + str(GAMES[this_game].network_stations[this_station].transport_cost) + '</td><td>transport cost ($/truck)</td></tr>' +
                               '<tr><td>' + str(GAMES[this_game].network_stations[this_station].transport_size) + '</td><td>units/truck</td></tr>' +
                               '<tr><td>' + str(GAMES[this_game].network_stations[this_station].delay_shipping) + '</td><td>weeks shipping delay</td></tr>' +
                               '<tr><td>' + str(GAMES[this_game].network_stations[this_station].delay_ordering) + '</td><td>weeks ordering delay</td></tr>'}
    if len(GAMES[this_game].network_stations[this_station].suppliers) == 0 and \
       not GAMES[this_game].network_stations[this_station].auto_decide_order_qty:
        static_info['suppliers'] = ['MyWorkshop']
    return render_template('play_screen.html', static_info=static_info)


@app.route('/monitor_games_screen', methods=['POST','GET'])
def monitor_games_screen():
    games_list = []
    if request.method == 'GET':  # when user reloads page
        pass
    if request.method == 'POST':
        for i in range(10):
            G = request.form.get('selected_game'+str(i))
            P = request.form.get('password'+str(i))
            if G in GAMES.keys():
                if GAMES[G].admin_password == P:
                    games_list.append(G)
    return render_template('multi-game-monitor.html', games_list=games_list)


@app.route('/monitor_screen', methods=['GET'])
def monitor_screen():
    this_game = request.args.get('game_name')
    if this_game not in GAMES.keys():
        flash('Error: Game not found.')
        return redirect(url_for('admin_game'))
    static_info = {'game':this_game,
                   'weeks':GAMES[this_game].weeks,
                   'stations':GAMES[this_game].auto_stations_names + GAMES[this_game].manual_stations_names,
                   'demands':GAMES[this_game].demand_stations_names,
                   'station_players':{k:v.player_name for (k,v) in GAMES[this_game].network_stations.items()}}
    return render_template('monitor_screen.html', static_info=static_info)


@app.route('/monitor_screen_radar', methods=['GET'])
def monitor_screen_radar():
    this_game = request.args.get('game_name')
    if this_game not in GAMES.keys():
        flash('Error: Game not found.')
        return redirect(url_for('admin_game'))
    static_info = {'game':this_game,
                   'stations':GAMES[this_game].auto_stations_names + GAMES[this_game].manual_stations_names,
                   'station_players':{k:v.player_name for (k,v) in GAMES[this_game].network_stations.items()}}
    return render_template('monitor_screen_radar.html', static_info=static_info)


@app.route('/show_network', methods=['GET'])
def show_network():
    this_game = request.args.get('game_name')
    if this_game not in GAMES.keys():
        flash('Error: Game is no longer valid.')
        return render_template('network.html', static_info={'nodes':[], 'edges':[]})
    nodes = []
    node_id = {}
    i = 1
    for x in GAMES[this_game].demand_stations_names:
        nodes.append({'id': i, 'label': x, 'image':url_for('static', filename='clients.png')})
        node_id[x] = i
        i += 1
    for x in GAMES[this_game].manual_stations_names:
        nodes.append({'id': i, 'label': x + '\n(' + GAMES[this_game].network_stations[x].player_name + ')', 'image':url_for('static', filename='warehouse1.png')})
        node_id[x] = i
        i += 1
    for x in GAMES[this_game].auto_stations_names:
        nodes.append({'id': i, 'label': x + '\n(' + GAMES[this_game].network_stations[x].player_name + ')', 'image':url_for('static', filename='warehouse0.png')})
        node_id[x] = i
        i += 1
    edges = []
    config = GAMES[this_game].get_config()
    for x in config['connections']:
        edges.append({'from': node_id[x['supp']], 'to': node_id[x['cust']], 'arrows':'middle'})
    static_info = {'nodes':nodes, 'edges':edges}
    return render_template('network.html', static_info=static_info)


################################################################################
# game and station selection screens
################################################################################
def select_game_page(text,next_page,ask_name,ask_password):
    kill_expired_games()
    data = {'text':text,
            'next_page':next_page,
            'ask_name':ask_name,
            'ask_password':ask_password,
            'games_list':[x.team_name for x in GAMES.values()]}
    return render_template('select_game.html', data=data)


def select_station_page(text,game_name,next_page):
    if game_name not in GAMES.keys():
        flash('Game is no longer valid, please try again.')
        return redirect(url_for('cmd',cmd='join_game'))
    data = {'text':text,
            'next_page':next_page,
            'stations_list':[x for x in GAMES[game_name].manual_stations_names
                             if time.time() - GAMES[game_name].network_stations[x].last_communication_time > SecondsAway_to_Disconnect]}
    return render_template('select_station.html', data=data)


################################################################################
# game data management
################################################################################
@app.route('/edit_game_setup', methods=['POST','GET'])
def edit_game_setup():
    action = request.args.get('action','')
    if request.method == 'GET':
        if 'selected_game' in session.keys():
            this_game = session['selected_game']
        else:
            this_game = ''
        if this_game not in GAMES.keys():
            flash('Game is no longer valid. Please select another game.')
            return redirect(url_for('index'))
    if request.method == 'POST':
        this_game = request.form.get('selected_game')
        if this_game == '** No game templates found! **':
            return redirect(url_for('index'))
        if action == 'edit':
            if this_game not in GAMES.keys():
                flash('Game is no longer valid. Please select another game.')
                return redirect(request.url)
        elif action == 'create':
            kill_expired_games()
            filename = './game_templates/' + this_game + '.json'
            this_game = ''
            if not os.path.isfile(filename) or not allowed_file(filename):
                flash('Template not found or is not a JSON file.')
                return redirect(request.url)
            try:
                with open(filename) as game_file:
                    game_data = json.load(game_file)
                i = 1
                this_game = '{:s}{:d}'.format(game_data['team_name'],i)
                while this_game in GAMES.keys():
                    i += 1
                    this_game = '{:s}{:d}'.format(game_data['team_name'],i)
                game_data['team_name'] = this_game
                GAMES[this_game] = game.Game(game_data)
            except Exception as e:
                if this_game in GAMES.keys():
                    del GAMES[this_game]
                show_error("Could not create game", e)
        else:
            flash('Error: no action type provided; must include edit or create actions call.')
            return redirect(request.url)
    session['selected_game'] = this_game
    return render_template('edit_game_setup.html', setup=GAMES[this_game].get_config(), action=action, sort_keys=True)


@app.route('/import_game_file', methods=['POST'])
def import_game_file():
    if 'importfilename' not in request.files:
        flash('No file part in posted request.')
        return redirect(request.url)
    file = request.files['importfilename']
    if file.filename == '':
        flash('No selected file.')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        game_data = json.loads(file.read().decode('ascii'))
    else:
        flash('Can\'t load file.')
        return redirect(request.url)
    kill_expired_games()
    if game_data['team_name'] in GAMES.keys():
        flash(game_data['team_name'] + ': Game already exists.')
    else:
        try:
            GAMES[game_data['team_name']] = game.Game(game_data)
            flash(game_data['team_name'] + ': Game successfully added.')
        except Exception as e:
            if game_data['team_name'] in GAMES.keys():
                del GAMES[game_data['team_name']]
            show_error("Could not create game",e)
    return redirect(url_for('cmd',cmd='import_game'))


@app.route('/export_game_file', methods=['GET'])
def export_game_file():
    game_name = request.args.get('game_name','')
    if game_name not in GAMES.keys():
        flash('Error: Game is no longer valid.')
        return redirect(url_for('admin_game'))
    game_file = json.dumps(GAMES[game_name].get_config(),cls=MyEncoder,indent=2,sort_keys=True)
    return Response(
        game_file,
        mimetype="application/json",
        headers={"Content-disposition":"attachment; filename=game_export.json"})


@app.route('/show_game_setup', methods=['GET'])
def show_game_setup():
    game_name = request.args.get('game_name','')
    if game_name not in GAMES.keys():
        flash('Error: Game is no longer valid.')
        return redirect(url_for('admin_game'))
    else:
        try:
            game_setup = GAMES[game_name].get_config()
            return render_template('show_game_setup.html', setup=game_setup, sort_keys=True)
        except Exception as e:
            show_error("Could get game setup data",e)
            return redirect(url_for('admin_game'))


@app.route('/copy_game', methods=['POST'])
def copy_game():
    org = request.args.get('org','')
    dst = request.form.get('dst','')
    if dst == '':
        flash('Error: Please provide a new game name.')
        return redirect(url_for('admin_game'))
    if org not in GAMES.keys():
        flash('Error: Origin game is no longer valid.')
        return redirect(url_for('admin_game'))
    if dst in GAMES.keys():
        flash('Error: destination game already exists.')
        return redirect(url_for('admin_game'))
    try:
        game_config = GAMES[org].get_config()
        game_config['team_name'] = dst
        GAMES[dst] = game.Game(game_config)
        flash(dst + ': Game successfully copied.')
    except Exception as e:
        if dst in GAMES.keys():
            del GAMES[dst]
        show_error("Could not create game", e)
    return redirect(url_for('admin_game'))


@app.route('/rename_game', methods=['POST'])
def rename_game():
    org = request.args.get('org','')
    dst = request.form.get('new_name','')
    if dst == '':
        flash('Error: Please provide a new game name.')
        return redirect(url_for('admin_game'))
    if org not in GAMES.keys():
        flash('Error: Origin game is no longer valid.')
        return redirect(url_for('admin_game'))
    if dst in GAMES.keys():
        flash('Error: destination game already exists.')
        return redirect(url_for('admin_game'))
    try:
        GAMES[dst] = GAMES.pop(org)
        GAMES[dst].team_name = dst
        session['selected_game'] = dst
        flash(dst + ': Game successfully renamed.')
    except Exception as e:
        show_error("Could not rename game",e)
    return redirect(url_for('admin_game'))


@app.route('/delete_game', methods=['GET'])
def delete_game():
    game_name = request.args.get('game_name','')
    next_page = request.args.get('next','advanced_menu')
    if game_name in GAMES.keys():
        del GAMES[game_name]
        flash(game_name + ': Game deleted.')
    else:
        flash('Error: Game not found.')
    return redirect(url_for('cmd', cmd=next_page))


@app.route('/reset_game', methods=['GET','POST'])
def reset_game():
    game_name = request.args.get('game_name','')
    if request.method == 'POST':  # when called from $.post()
        if game_name in GAMES.keys():
            try:
                GAMES[game_name].reset()
            except Exception as e:
                return jsonify({'Result': '{:}:{:}'.format(type(e).__name__, e.args)})
            return jsonify({'Result': ''})  # game_name + ' was successfully reset.'}) # # reset effects are obvious on the screen, no need for a message
        else:
            return jsonify({'Result': game_name + ' is no longer valid.'})
    if request.method == 'GET':  # when redirected ehre or user reloads page
        if game_name not in GAMES.keys():
            flash('Error: Game is no longer valid.')
            return redirect(url_for('admin_game'))
        else:
            try:
                GAMES[game_name].reset()
                flash(game_name + ': Game successfully reset.')
            except Exception as e:
                show_error("Could not reset game",e)
        return redirect(url_for('admin_game'))


@app.route('/save_games_state', methods=['GET'])
def save_server_state():
    if save_games_state():
        flash('Games states saved.')
    else:
        flash('Error: Could not save games state.')
    return redirect(url_for('admin_server_menu'))


@app.route('/load_games_state', methods=['GET'])
def load_server_state():
    if load_games_state():
        flash('Games states loaded.')
    else:
        flash('Error: Could not load games state.')
    return redirect(url_for('admin_server_menu'))


################################################################################
# Debug screens
################################################################################
@app.route('/debug', methods=['GET'])
def debug():
    return select_game_page(text='Select a game to debug:',next_page='debug_screen', ask_name=False, ask_password=False)


@app.route('/debug_screen', methods=['GET','POST'])
def debug_screen():
    if request.method == 'GET':
        if 'selected_game' in session.keys():
            this_game = session['selected_game']
        else:
            this_game = ''
        if this_game not in GAMES.keys():
            flash('Game is no longer valid, please select another game.')
            return redirect(url_for('debug'))
    if request.method == 'POST':
        this_game = request.form.get('selected_game')
        if this_game == '** No games created yet! **':
            return redirect(url_for('index'))
        if this_game not in GAMES.keys():
            flash('Please select a game.')
            return redirect(url_for('debug'))
        session['selected_game'] = this_game
    static_info = {'game':this_game,
                   'weeks':GAMES[this_game].weeks,
                   'number_of_players':len(GAMES[this_game].manual_stations_names)}
    return render_template('admin_debug.html', static_info=static_info)
#
#
# @app.route('/debug_wsg', methods=['GET'])
# def debug_wsg():
#     # return GAMES['WSG_test'].Debug_Report_WSG_Inv_PO_Report()
#     if 'WSG' in GAMES.keys():
#         return '<!DOCTYPE html><html><head><title>WSG Debug Screen</title></head>' + \
#                 '<body><pre>' + GAMES['WSG'].Debug_Report_WSG_Inv_PO_Report() + \
#                 '</pre></body></html>'
#     else:
#         flash('No such game: WSG')
#         return redirect(url_for('index'))


################################################################################
# AJAX
################################################################################
@app.route('/change_game_settings', methods=['POST'])
def change_game_settings():
    kill_expired_games()
    try:
        this_game = session['selected_game']
        game_settings = request.json
        for x in game_settings['demands']:
            x['demand'] = txt2list(x['demand'])
        for x in game_settings['stations']:
            x['production_max'] = txt2list(x['production_max'])
            x['production_min'] = txt2list(x['production_min'])
        if this_game != game_settings['team_name']:
            if game_settings['team_name'] in GAMES.keys():
                return jsonify({'result':False,'msg':'Couldn\'t save game setting: the changed game name conflicts with an existing game.'})
        G = game.Game(game_settings)
        del GAMES[this_game]
        GAMES[game_settings['team_name']] = G
        session['selected_game'] = game_settings['team_name']
        return jsonify({'result':True,'msg':'Game setup saved.'})
    except Exception as e:
        return jsonify({'result':False,'msg':'Couldn\'t save game setup. Error: Exception of type {0} occurred. Arguments:{1!r}.'.format(type(e).__name__, e.args)})


@app.route('/submit', methods=['POST'])
def submit():
    this_game = ''
    try:
        this_game = session['selected_game']
        this_station = session['selected_station']
        this_week = request.json['DATA']['week']
        suppliers = request.json['DATA']['suppliers']
        customers = request.json['DATA']['customers']
        for k, v in suppliers.items():  # convert text input into numbers
            suppliers[k] = int(v)
        for k, v in customers.items():
            customers[k] = int(v)
        GAMES[this_game].network_stations[this_station].touch()
        GAMES[this_game].SetPlayerTurnData(
            this_station, this_week, suppliers, customers)
    except Exception as e:
        log_msg("Issue in player submission. Game: {:}. Exception: {:} - {:!r}".format(this_game,type(e).__name__, e.args))
    return Response("this will not change the user view"), 204


@app.route('/get_station_status', methods=['GET'])
def get_station_status():
    this_game = request.args.get('game','')
    this_station = request.args.get('station','')

    if this_game not in GAMES.keys():
        log_msg("'{:}' is no longer a valid game. AJAX get_station_status request ignored.".format(this_game))
        return jsonify({})
    if this_station not in GAMES[this_game].network_stations.keys():
        log_msg("'{:}.{:}' is no longer a valid station. AJAX get_station_status request ignored.".format(this_game, this_station))
        return jsonify({})

    GAMES[this_game].network_stations[this_station].touch()
    w = GAMES[this_game].current_week
    if w >= GAMES[this_game].weeks:
        w = GAMES[this_game].weeks - 1
    current_time = time.time()
    GAMES[this_game].connected_stations = len([1 for x in GAMES[this_game].network_stations.values() if (current_time - x.last_communication_time) < SecondsAway_to_Disconnect])

    return jsonify({
        'current_week':w,
        'turn_start_time':GAMES[this_game].turn_start_time,
        'game_done':GAMES[this_game].game_done,
        'players_completed_turn':GAMES[this_game].players_completed_turn,
        'connected_stations':GAMES[this_game].connected_stations,
        'connection_state':GAMES[this_game].network_stations[this_station].last_communication_time,
        'cost_inventory':game.currency(sum(GAMES[this_game].network_stations[this_station].kpi_weeklycost_inventory)),
        'cost_backorder':game.currency(sum(GAMES[this_game].network_stations[this_station].kpi_weeklycost_backorder)),
        'cost_transport':game.currency(sum(GAMES[this_game].network_stations[this_station].kpi_weeklycost_transport)),
        'total_cost':game.currency(sum(GAMES[this_game].network_stations[this_station].kpi_total_cost)),
        'fulfillment_rate':game.percent(list_avg(GAMES[this_game].network_stations[this_station].kpi_fulfillment_rate[:w])),
        'truck_utilization':game.percent(list_avg(GAMES[this_game].network_stations[this_station].kpi_truck_utilization[:w])),
        'inventory':GAMES[this_game].network_stations[this_station].inventory[w],
        'backorder':show_week(GAMES[this_game].network_stations[this_station].backorder,w),
        'incomming_order':show_week(GAMES[this_game].network_stations[this_station].received_po,w),
        'incomming_delivery':show_week(GAMES[this_game].network_stations[this_station].inbound,w),
        'production_min':str(GAMES[this_game].network_stations[this_station].production_min[w]),
        'production_max':str(GAMES[this_game].network_stations[this_station].production_max[w]),
        'production_limits':toHTMLtbl([('wk','min','max')]+GAMES[this_game].network_stations[this_station].production_limits[w+1:w+11])})


@app.route('/get_game_status', methods=['GET'])
def get_game_status():
    this_game = request.args.get('game','')
    if this_game not in GAMES.keys():
        log_msg("'{:}' is no longer a valid game. AJAX get_game_status request ignored.".format(this_game))
        return jsonify({})
    current_week = GAMES[this_game].current_week
    current_time = time.time()

    if current_week == 0:
        return jsonify({
            'week':current_week,
            'waitingfor':[GAMES[this_game].network_stations[x].station_name for x in GAMES[this_game].manual_stations_names
                          if GAMES[this_game].network_stations[x].week_turn_completed < current_week],
            'disconnected':[GAMES[this_game].network_stations[x].station_name for x in GAMES[this_game].manual_stations_names
                            if (current_time - GAMES[this_game].network_stations[x].last_communication_time) >= SecondsAway_to_Disconnect]})

    stations_list = GAMES[this_game].manual_stations_names + GAMES[this_game].auto_stations_names
    demands_list = GAMES[this_game].demand_stations_names
    cost_inventory = {k:[0]*current_week for k in stations_list}
    cost_backorder = {k:[0]*current_week for k in stations_list}
    cost_transport = {k:[0]*current_week for k in stations_list}
    cost_total = {k:[0]*current_week for k in stations_list}
    fulfillment = {k:[0]*current_week for k in stations_list}
    green_score = {k:[0]*current_week for k in stations_list}
    shipments = {k:[0]*current_week for k in stations_list}
    extra_shipments = {k:[0]*current_week for k in stations_list}
    backorder = {k:[] for k in stations_list}
    inventory = {k:[] for k in stations_list}
    orders = {k:[] for k in (stations_list + demands_list)}
    deliveries = {k:[] for k in stations_list}

    for x in (stations_list + demands_list):
        S = GAMES[this_game].network_stations[x]
        if x in GAMES[this_game].demand_stations_names:
            orders[x] = S.demand
        else:
            cost_inventory[x] = sum(S.kpi_weeklycost_inventory[:current_week])
            cost_backorder[x] = sum(S.kpi_weeklycost_backorder[:current_week])
            cost_transport[x] = sum(S.kpi_weeklycost_transport[:current_week])
            cost_total[x] = sum(S.kpi_total_cost[:current_week])
            fulfillment[x] = sum(S.kpi_fulfillment_rate[:current_week])/(current_week)
            green_score[x] = sum(S.kpi_truck_utilization[:current_week])/(current_week)
            shipments[x] = S.kpi_shipment_trucks
            for w in range(current_week):
                extra_shipments[x][w] = floor(S.kpi_shipment_trucks[w]*(1-S.kpi_fulfillment_rate[w]))
            backorder[x] = game.combine_weekly(S.backorder)
            inventory[x] = S.inventory
            orders[x] = game.combine_weekly(S.sent_po)
            deliveries[x] = game.combine_weekly(S.outbound)

    return jsonify({
        'week':current_week,
        'waitingfor':[GAMES[this_game].network_stations[x].station_name for x in GAMES[this_game].manual_stations_names
                      if GAMES[this_game].network_stations[x].week_turn_completed < current_week],
        'disconnected':[GAMES[this_game].network_stations[x].station_name for x in GAMES[this_game].manual_stations_names
                        if (current_time - GAMES[this_game].network_stations[x].last_communication_time) >= SecondsAway_to_Disconnect],
        'data':{
            'cost_inventory':cost_inventory,
            'cost_backorder':cost_backorder,
            'cost_transport':cost_transport,
            'cost_total':cost_total,
            'fulfillment':fulfillment,
            'green_score':green_score,
            'shipments':shipments,
            'extra-shipments':extra_shipments,
            'backorder':backorder,
            'inventory':inventory,
            'orders':orders,
            'deliveries':deliveries}
        })


@app.route('/get_game_status_radar', methods=['GET'])
def get_game_status_radar():
    data = {}
    best = {'inventory':float("inf"),'backorder':float("inf"),'transport':float("inf"),'fulfillment':0,'green':0}
    this_game = request.args.get('game','')
    if this_game not in GAMES.keys():
        log_msg("'{:}' is no longer a valid game. AJAX get_game_status_radar request ignored.".format(this_game))
        return jsonify({'nodata': True})
    current_week = GAMES[this_game].current_week
    stations_list = GAMES[this_game].manual_stations_names + GAMES[this_game].auto_stations_names
    if current_week == 0:
        return jsonify({'nodata':True})

    for x in stations_list:
        S = GAMES[this_game].network_stations[x]
        data[x] = {'inventory':sum(S.kpi_weeklycost_inventory[:current_week]),
                   'backorder':sum(S.kpi_weeklycost_backorder[:current_week]),
                   'transport':sum(S.kpi_weeklycost_transport[:current_week]),
                   'fulfillment':sum(S.kpi_fulfillment_rate[:current_week])/(current_week),
                   'green':sum(S.kpi_truck_utilization[:current_week])/(current_week)}
        for k,v in data[x].items():
            if k in ['inventory','backorder','transport']:
                if v < best[k]:
                    best[k] = v
            if k in ['fulfillment','green']:
                if v > best[k]:
                    best[k] = v
    for x in stations_list:
        for k,v in data[x].items():
            if k in ['fulfillment','green']:
                if best[k] > 0:
                    data[x][k] = data[x][k]/best[k]
            if k in ['inventory','backorder','transport']:
                if data[x][k] > 0:
                    data[x][k] = best[k]/data[x][k]
    return jsonify(data)


@app.route('/get_games_status', methods=['GET'])
def get_games_status():
    games_list = request.args.get('games_list','').split(',')
    current_time = time.time()
    data = {}
    for g in games_list:
        if g not in GAMES.keys():
            log_msg("'{:}' is no longer a valid game. Game skipped in AJAX get_games_status request.".format(g))
        else:
            current_week = GAMES[g].current_week
            if current_week >= GAMES[g].weeks:
                current_week = GAMES[g].weeks - 1
            if current_week == 0:
                data[g] = {'week':current_week+1,
                           'waiting':[GAMES[g].network_stations[x].station_name for x in GAMES[g].manual_stations_names if GAMES[g].network_stations[x].week_turn_completed < current_week],
                           'disconnected':[GAMES[g].network_stations[x].station_name for x in GAMES[g].manual_stations_names if (current_time - GAMES[g].network_stations[x].last_communication_time) >= SecondsAway_to_Disconnect],
                           'inventory':0,'backorder':0,'trucks':0,'cost':0,'fulfillment':0,'greenscore':0}
            else:
                if GAMES[g].game_done:
                    fulfillment = GAMES[g].kpi_customer_satisfaction
                    greenscore = GAMES[g].kpi_green_score
                else:
                    fulfillment = GAMES[g].kpi_customer_satisfaction[:current_week]
                    greenscore = GAMES[g].kpi_green_score[:current_week]
                data[g] = {'week':current_week+1,
                           'waiting':[GAMES[g].network_stations[x].station_name for x in GAMES[g].manual_stations_names if GAMES[g].network_stations[x].week_turn_completed < current_week],
                           'disconnected':[GAMES[g].network_stations[x].station_name for x in GAMES[g].manual_stations_names if (current_time - GAMES[g].network_stations[x].last_communication_time) >= SecondsAway_to_Disconnect],
                           'inventory':sum([x.inventory[current_week] for x in GAMES[g].network_stations.values() if type(x) is not game.stations.Demand]),
                           'backorder':sum([week_sum(x.backorder,current_week) for x in GAMES[g].network_stations.values() if type(x) is not game.stations.Demand]),
                           'trucks':sum(GAMES[g].kpi_trucks),
                           'cost':sum(GAMES[g].kpi_cost['total']),
                           'fulfillment':list_avg(fulfillment),
                           'greenscore':list_avg(greenscore)}
    return jsonify(data)


@app.route('/get_debug_data', methods=['GET'])
def get_debug_data():
    this_game = request.args.get('game','')
    if this_game not in GAMES.keys():
        log_msg("'{:}' is no longer a valid game. AJAX get_debug_data request ignored.".format(this_game))
        return jsonify({})
    w = GAMES[this_game].current_week
    current_time = time.time()
    GAMES[this_game].connected_stations = len([1 for x in GAMES[this_game].network_stations.values() if (current_time - x.last_communication_time) < SecondsAway_to_Disconnect])
    return jsonify({
        'week':w,
        'players_completed_turn':GAMES[this_game].players_completed_turn,
        'connected_stations':GAMES[this_game].connected_stations,
        'report':GAMES[this_game].Debug_Report()})
