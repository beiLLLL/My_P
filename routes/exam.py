"""雅思口语模拟考试核心路由"""
import json
import queue
import threading
from flask import Blueprint, render_template, request, jsonify, Response, stream_with_context
from flask_login import login_required, current_user
from models import db, ExamRecord
from services.llm import get_exam_reply

exam_bp = Blueprint('exam', __name__)

EXAMINERS = {
    'kobe': {
        'name': 'Kobe',
        'file': 'kobe.png',
        'bio': '前美国职业篮球运动员，曾效力于NBA洛杉矶湖人队，司职得分后卫/小前锋，绰号"黑曼巴"。出生于1978年8月23日，来自宾夕法尼亚州费城，整个职业生涯都奉献给了湖人队，共获得五次总冠军、两次总决赛MVP和四次得分王，但因直升机事故不幸离世，享年41岁。我从地狱杀回来了孩子们。',
        'style': 'kobe',
    },
    'dongxuelian': {
        'name': '东雪莲',
        'file': 'dongxuelian.png',
        'bio': '虚拟主播。她以银白色长发、精致发饰和独特妆容为标志性形象，常在直播或视频内容中展现活泼、可爱的风格，深受二次元文化爱好者喜爱。暗恋着小孙，貌似只会一点英文。',
        'style': 'dongxuelian',
    },
    'gunmu': {
        'name': '滚木',
        'file': 'gunmu.png',
        'bio': '',
        'style': 'gunmu',
    },
    'examiner': {
        'name': 'Examiner',
        'file': 'examiner.jpeg',
        'bio': '就是正常雅思考官',
        'style': 'normal',
    },
    'nailong': {
        'name': '奶龙',
        'file': 'nailong.png',
        'bio': '哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈',
        'style': 'nailong',
    },
    'shaoyu': {
        'name': '少羽',
        'file': 'shaoyu.png',
        'bio': '《和平精英》游戏圈内具有较高知名度的网络主播。他以独特的游戏风格和深度的游戏理解脱颖而出，但貌似不会说英语......',
        'style': 'shaoyu',
    },
    'sunxiaochuan': {
        'name': '孙笑川',
        'file': 'sunxiaochuan.png',
        'bio': '中国网络文化中具有标志性地位的游戏主播与自媒体创作者。出生于1990年5月12日，四川成都人，曾是斗鱼TV的知名《英雄联盟》主播，后转至Twitch平台继续直播。以"带带大师兄"为微博昵称，被网友亲切称为"大师兄"，并因直播中独特的语言风格和与观众的激烈互动而走红，暗恋着小东，貌似不会说英语...好像是日本人？',
        'style': 'sunxiaochuan',
    },
    'tafei': {
        'name': 'Taffy',
        'file': 'tafei.png',
        'bio': '2021年6月正式出道，主要在B站通过直播、动态与动画投稿开展活动，同时也在YouTube、抖音、微博等平台运营。她的粉丝群体被称为"雏草姬"喵~',
        'style': 'tafei',
    },
}

DIFFICULTIES = {
    'easy': '🟢 Easy',
    'medium': '🟡 Medium',
    'hard': '🔴 Hard',
}


@exam_bp.route('/exam')
@login_required
def exam_page():
    return render_template('exam.html', examiners=EXAMINERS, difficulties=DIFFICULTIES)


@exam_bp.route('/api/exam/stream', methods=['POST'])
@login_required
def exam_stream():
    """SSE 流式对话"""
    data = request.get_json()
    difficulty = data.get('difficulty', 'medium')
    examiner = data.get('examiner', 'kobe')
    message = data.get('message', '').strip()
    history = data.get('history', [])
    current_part = data.get('currentPart', 'part1')
    question_count = data.get('questionCount', 0)
    style = EXAMINERS.get(examiner, {}).get('style', 'normal')

    if not message:
        return jsonify({'error': 'Empty message'}), 400

    # 在独立线程中调用 AI，避免 Flask 线程 SSL 问题
    from flask import current_app as ca
    app_ref = ca._get_current_object()  # 获取真实 app 对象
    result_queue = queue.Queue()

    def ai_worker():
        with app_ref.app_context():
            try:
                reply = get_exam_reply(difficulty, examiner, history, message, current_part, question_count, style)
                result_queue.put(('ok', reply))
            except Exception as e:
                result_queue.put(('error', str(e)))

    t = threading.Thread(target=ai_worker)
    t.start()

    def generate():
        full_text = ''
        # 等待 AI 线程完成
        status, data = result_queue.get()

        if status == 'error':
            full_text = f'[Error: {data}]'
            yield f"data: {json.dumps({'token': full_text, 'full': full_text})}\n\n"
        else:
            for char in data:
                full_text += char
                yield f"data: {json.dumps({'token': char, 'full': full_text})}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

        t.join()

        # 保存记录
        try:
            record = ExamRecord(
                user_id=current_user.id,
                examiner=examiner,
                difficulty=difficulty,
                messages=json.dumps(history + [
                    {'role': 'user', 'content': message},
                    {'role': 'assistant', 'content': full_text}
                ]),
            )
            db.session.add(record)
            db.session.commit()
        except Exception:
            pass

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    )


@exam_bp.route('/api/exam/feedback', methods=['POST'])
@login_required
def exam_feedback():
    """生成考试反馈（独立线程避免 SSL 问题）"""
    from services.llm import generate_feedback
    data = request.get_json()
    difficulty = data.get('difficulty', 'medium')
    history = data.get('history', [])

    if not history:
        return jsonify({'error': 'No exam history'}), 400

    from flask import current_app as ca
    app_ref = ca._get_current_object()
    result_queue = queue.Queue()

    def worker():
        with app_ref.app_context():
            try:
                r = generate_feedback(difficulty, history)
                result_queue.put(('ok', r))
            except Exception as e:
                result_queue.put(('error', str(e)))

    t = threading.Thread(target=worker)
    t.start()
    t.join()
    status, result = result_queue.get()

    if status == 'error':
        return jsonify({'error': result}), 500

    record = ExamRecord.query.filter_by(user_id=current_user.id).order_by(ExamRecord.id.desc()).first()
    if record:
        record.score = result.get('score', '?')
        record.feedback = result.get('feedback', '')
        db.session.commit()

    return jsonify(result)
