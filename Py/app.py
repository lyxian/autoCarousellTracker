from flask import Flask, request, render_template
from datetime import datetime
import time
import pytz

from tmp import start_test

wb_name = ''
start = ''

app = Flask(__name__)

@app.route('/template/<id>')
def home(id):
   return render_template(f'{id}.html')

@app.route('/start')
def _start():
    while True:
        # try:
        if wb_name == '':
            source = request.args.get('source', '')
            if source not in ['Airflow', 'Zapier']:
                source = 'Staging'
        else:
            source = wb_name
        target = f'Automated Carousell-{source}'
        
        print('Starting app...')
        success, cmd = start(target)
        if success:
            print('--Success--')
            return '--Success--', 200
        else:
            if cmd == 'Stop':    # Stop Code
                print('Program Stopped...')
                return '--Program Stopped--', 400
            elif cmd == 'Wait':    # Wait 1 min
                print('Awaiting Query...')
                time.sleep(60)
            elif cmd == 'Off':
                print(
                    f'Sleeping since {datetime.strftime(datetime.now(tz=pytz.timezone("Singapore")),  "%Y-%m-%d %I:%M %p")}')
                time.sleep(10*60)
            else:    # Update Failed -> Stop with msg OR Retry in 1 min
                print('--Program Failed--')
                return '--Program Failed--', 401
        # except Exception as e:
        #     print(f'--Program Exited Early--\n{e}')
        #     return '!', 401

@app.route('/stop')
def _stop():
    shutdown_hook = request.environ.get('werkzeug.server.shutdown')
    try:
        shutdown_hook()
        print('--End--')
        return '--End--', 0
    except:
        pass

@app.route('/test', methods=['GET'])
def _test():
    if request.method == 'GET':
        try:
            target = f'Automated Carousell-Staging'
            print('Starting app...')
            success, cmd = start_test(target)
            return {'status': 'OK'}, 200
        except Exception as e:
            import traceback
            error = traceback.format_exc().strip()
            print(f'Error: {error}')
            return {'status': 'NOT_OK'}, 400
    else:
        return {'ERROR': 'Nothing here!'}, 404

@app.route('/arg')
def _arg():
    def inner_func():
        print('hello_inner')
    try:
        inner_func()
        print(request.args)
        return '--End--', 0
    except Exception as e:
        print(f'{e}')
        return '--Error--', 400

app.run(host='0.0.0.0', port=5000, debug=True)