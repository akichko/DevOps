from flask import Flask
from flask import render_template, request, redirect, jsonify
from flask_bootstrap import Bootstrap
import requests
from gpt import GptDummy, Gpt2
import threading
import shutil
import os

# function def ####################################################

def load_model(model_path):
    print(f'model loading: {model_path}')
  
    if model_path == '':
        model = GptDummy('追加テキスト')
    else:
        model = Gpt2(model_path)

    print('model loaded')
    return model


def ignore_git_folders(src, names):
    # .git フォルダを除外するための関数
    return ['.git']


def copy_model(src_model_path, dst_model_path):
    # current_model_pathフォルダが存在する場合は削除する
    if os.path.exists(dst_model_path):
        shutil.rmtree(dst_model_path)
    
    shutil.copytree(src_model_path, dst_model_path, ignore=ignore_git_folders)  # モデルの最新バージョンをコピー


def copy_and_deploy_model(model_text, src_model_path, dst_model_path):
    global is_on_deploying
    is_on_deploying = True
   
    # ダミーモデルに切替
    global model
    model = GptDummy(model_text)
    
    print('コピー開始')
    copy_model(src_model_path, dst_model_path)
    print('コピー完了')

    model = load_model(dst_model_path)
    is_on_deploying = False



# params ##########################################################

train_model_output = "/workspace/LLM/finetune_work"
train_data = "/workspace/train_data/akane-talk/dataset_plain.txt"
current_model_path = "/workspace/LLM/current"


#initial_model_path = "/workspace/LLM/rinna/japanese-gpt-1b"
#initial_model_path = "/workspace/LLM/rinna/japanese-gpt2-medium"
initial_model_path = "/workspace/LLM/rinna/japanese-gpt2-small"
#initial_model_path = "/workspace/LLM/cyberagent/open-calm-medium"

model_path = '' #dummyModel
#model_path = initial_model_path
#model_path = train_model_output

is_on_training = False
is_on_deploying = False


# main app ########################################################

app = Flask(__name__, static_folder='static')

bootstrap = Bootstrap(app)
   
model = load_model(model_path)
 
    
   
@app.route("/debug", methods=['GET','POST'])
def debug():
    if request.method == 'GET':
        return render_template('debug.html')
    
@app.route("/", methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', messate_text=model.get_status())

@app.route('/message', methods=['GET', 'POST'])
def message():
    return render_template('message.html', messate_text='aaa')


@app.route("/apitest", methods=['GET','POST'])
def apitest():
    if request.method == 'GET':
        return render_template('apitest.html')

@app.route("/training", methods=['GET','POST'])
def training():
    if request.method == 'GET':
        return render_template('training.html')

@app.route('/text', methods=['GET', 'POST'])
def text():
    if request.method == 'POST':
        text = request.form['text']
        with open('学習用テキストファイル.txt', 'a') as f:
            f.write(text + '\n')

    with open('学習用テキストファイル.txt', 'r') as f:
        text_data = f.read()

    return render_template('training.html', text_data=text_data)

@app.route("/finetune", methods=['GET','POST'])
def finetune():
    if request.method == 'GET':
        return render_template('finetune.html')


# チャットボットのUIページ
@app.route("/chat", methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        input_text = request.form['input_text']
        response = requests.post('/api', data={'input_text': input_text})
        output_text = response.json()['message']['output']
        return render_template('chat.html', input_text=input_text, output_text=output_text)
    return render_template('chat.html')


@app.route("/api/gpt", methods=['POST'])
def api():
    input_text = request.form['input_text']
    num = int(request.form.get('data_num', '1'))
    full_text_array = model.generate(input_text, num_return_sequences=num)
    output_text = full_text_array[0][len(input_text):]
    return create_json(input_text, output_text, full_text_array)


# チャットボットのUIページ
@app.route("/api/chat", methods=['POST'])
def api2():
    input_text = '「' + request.form['input_text'] + '」「'
    response = requests.post('http://localhost/api/gpt', data={'input_text': input_text})
    full_text = response.json()['message']['full'][0]
    output_text = full_text[len(input_text):]
    if '」' in output_text:
        response_text = output_text.split('」', 1)[0]
    else:
        response_text = output_text

    response = {
        "message":
            {
                "input_text": input_text,
                "response_text": response_text
            }
    }
    return jsonify(response)


def create_json(input_text, output_text, full_text_array):
    response = {
        "message":
            {
                "input": input_text,
                "output": output_text,
                "full": full_text_array
            }
    }
    return jsonify(response)

@app.route("/switch_dummy_model", methods=['GET', 'POST'])
def switch_dummy_model():
    global model
    model = GptDummy('学習中')
    return render_template('message.html', messate_text='ダミーモデルに切り替えました')

@app.route("/switch_current_model", methods=['GET', 'POST'])
def switch_current_model():
    global model
    model = load_model(model_path)
    return render_template('message.html', messate_text=f'実モデルに切り替えました({model_path})')


def train_in_background():
    train_data = "/workspace/train_data/akane-talk/dataset_plain.txt"
    model.finetune(train_data, "/workspace/LLM/finetune_work",
                 batch_size=4, num_train_epochs=2)
    
@app.route("/start_training", methods=['GET', 'POST'])
def start_training():
    global model
    if not model.is_trainable:
        return render_template('message.html', messate_text='学習非対応モデルです')
    if model.train_status == 1:
        return render_template('message.html', messate_text='既に学習中です')

    model.train_status = 1
    threading.Thread(target=train_in_background).start()
    return render_template('message.html', messate_text='学習開始しました')


@app.route("/deploy_model", methods=['GET', 'POST'])
def deploy_model():
    global is_on_deploying
    if is_on_deploying:
        return render_template('message.html', messate_text='エラー：処理中です')

    threading.Thread(target=copy_and_deploy_model,
                     args=('学習モデルデプロイ中', train_model_output, current_model_path)
                     ).start()

    return redirect('/')


@app.route("/reset_model", methods=['GET', 'POST'])
def reset_model():
    global is_on_deploying
    if is_on_deploying:
        return render_template('message.html', messate_text='エラー：処理中です')

    threading.Thread(target=copy_and_deploy_model,
                     args=('モデル初期化中', initial_model_path, current_model_path)
                     ).start()

    return redirect('/')


    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
