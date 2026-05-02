from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, UserMixin, login_required
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
import os
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash

# .envファイルの読み込み
load_dotenv()

# Flaskアプリケーションの作成
app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == os.getenv('LOGIN_USER'):
        return User(user_id)
    return None

# Flask-Bootstrapの初期化
bootstrap = Bootstrap(app)

# データベース接続
def connect_db():
    return psycopg.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        row_factory=dict_row  # クエリ結果を辞書形式で取得
    )

# アンケート画面
@app.route('/')
def index():
    
    # データベースから行事名、演目、来場きっかけを取得
    with connect_db() as conn:
        with conn.cursor() as cur:  # カーソルの作成
            try:
                cur.execute("SELECT event_name FROM events ORDER BY event_id DESC LIMIT 1;")
                db_event = cur.fetchone()   # 行事名の取得（辞書）
                if db_event is None:
                    return '行事が見つかりませんでした  ', 500
                cur.execute("SELECT performance_id, performance_name FROM performances;")
                db_performances = cur.fetchall()    # 演目の取得（辞書）
                cur.execute("SELECT chance_id, chance_text FROM chances;")
                db_chances = cur.fetchall()    # 来場きっかけの取得（辞書）
            except Exception as e:
                print('データ取得に失敗', e)
                return 'データ取得に失敗', 500
    
    # 取得したデータをindex.htmlに渡す
    event_name = db_event['event_name']
    return render_template('index.html', event_name=event_name, performances=db_performances, chances=db_chances)


# アンケート送信処理
@app.route('/answered', methods=['POST'])
def answered():
    
    # フォームからのデータをデータベースに格納
    with connect_db() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("SELECT event_id FROM events ORDER BY event_id DESC LIMIT 1;")
                event_row = cur.fetchone()
                if event_row is None:
                    return '行事が見つかりませんでした', 500
                event_id = event_row['event_id']
                performance = int(request.form.get('performance'))  # 演目の選択(idで取得)
                chance = int(request.form.get('chance'))  # 来場きっかけの選択(idで取得)
                rating = int(request.form.get('rating'))  # 総評の選択
                answer_text = request.form.get('feedback')  # 感想の取得
                if not performance or not chance or not rating:
                    return '入力が不正です', 400
                cur.execute(
                    "INSERT INTO answers(event_id, performance_id, chance_id, answer_eval, answer_text, answer_time) VALUES (%s, %s, %s, %s, %s, NOW());",
                    (event_id, performance, chance, rating, answer_text)
                )
            except Exception as e:
                print('データ保存に失敗', e)
                return 'データ保存に失敗', 500
    return render_template('answered.html')


# 部員ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        if username == os.getenv('LOGIN_USER') and check_password_hash(os.getenv('LOGIN_PASSWORD_HASH'), password):
            user = User(id=username)
            login_user(user)
            return redirect(url_for('results'))
        else:
            return render_template('login.html', error='ユーザー名またはパスワードが間違っています')
        
# アンケート回答集
@app.route('/results', methods=['GET', 'POST'])
@login_required
def results():
    # 最初：最新の行事のアンケート回答を表示、以降：選択された行事のアンケート回答を表示
    with connect_db() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("SELECT * FROM events;")
                events = cur.fetchall()
                
                if request.method == 'POST':
                    event_id = request.form.get('event_id')
                    current_event = next((event['event_name'] for event in events if event['event_id']==int(event_id)), None)
                else:
                    cur.execute("SELECT event_id FROM events ORDER BY event_id DESC LIMIT 1;")
                    event_id = cur.fetchone()['event_id']
                    current_event = next((event['event_name'] for event in events if event['event_id']==int(event_id)), None)
                
                query = '''
                        SELECT per.performance_name, chan.chance_text, ans.answer_eval, ans.answer_text
                        FROM answers AS ans
                        LEFT OUTER JOIN performances AS per ON ans.performance_id = per.performance_id
                        LEFT OUTER JOIN chances AS chan ON  ans.chance_id = chan.chance_id
                        WHERE ans.event_id= %s 
                        ORDER BY ans.answer_time;
                    '''
                cur.execute(query, (event_id,))
                answers = cur.fetchall()

            except Exception as e:
                print('データの取得に失敗', e)
                return 'データの取得に失敗', 500
    return render_template('results.html', answers=answers, events=events, current_event=current_event)