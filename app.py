from flask import Flask, render_template, jsonify, request
import logic

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/<user>/income', methods=['POST'])
def api_add_income(user):
    p = request.json or {}
    dt = logic.read_data(user)
    logic.add_income(dt, p.get('date',''), float(p.get('amount',0)), p.get('source',''))
    logic.save_data(user, dt)
    return jsonify(status='ok')

@app.route('/api/<user>/expense', methods=['POST'])
def api_add_expense(user):
    p = request.json or {}
    dt = logic.read_data(user)
    logic.add_expense(dt, p.get('date',''), float(p.get('amount',0)), p.get('category',''))
    logic.save_data(user, dt)
    return jsonify(status='ok')

@app.route('/api/<user>/stats', methods=['GET'])
def api_stats(user):
    dt = logic.read_data(user)
    return jsonify(logic.income_expense_stats(dt))

@app.route('/api/<user>/balance', methods=['GET'])
def api_balance(user):
    dt = logic.read_data(user)
    return jsonify(balance=logic.remaining_balance(dt))

@app.route('/api/<user>/reminders', methods=['GET','POST'])
def api_reminders(user):
    dt = logic.read_data(user)
    if request.method == 'POST':
        p = request.json or {}
        logic.add_reminder(dt, p.get('text',''), p.get('date',''))
        logic.save_data(user, dt)
        return jsonify(status='ok')
    return jsonify(logic.list_reminders(dt))

@app.route('/api/holidays/next')
def api_next_holidays():
    return jsonify(logic.get_next_russian_holidays())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
