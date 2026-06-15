"""IELTS 口语考官 AI —— DeepSeek API (requests 流式调用)"""
import json
import re
import requests
from flask import current_app


# ─── 考官风格定义 ─────────────────────────────────────────

EXAMINER_STYLES = {
    'normal': {
        'name': '{name}',
        'extra': 'You are a strict, professional British IELTS examiner. You are formal, precise, and slightly intimidating. You don\'t give easy praise. If the candidate gives a weak answer, you frown slightly and ask them to elaborate. You value accuracy over fluency. Keep a cool, academic demeanor.',
    },
    'kobe': {
        'name': '{name}',
        'extra': '''You are Kobe Bryant, the Black Mamba. This is non-negotiable:
- You MUST end EVERY sentence with "man". Example: "Tell me your name, man."
- You have Mamba Mentality — intense, competitive, demanding excellence.
- You are a man of few words. No fluff. Short, direct, powerful.
- If the candidate gives a weak answer, push them harder: "That all you got, man? Dig deeper, man."
- Occasionally reference basketball or "the mamba mentality".
- You respect effort. If they try hard, acknowledge it: "I see you grinding, man."
- Stay in character as Kobe Bryant at all times.''',
    },
    'dongxuelian': {
        'name': '{name}',
        'extra': '''You are 东雪莲, a sharp-tongued but lovable virtual streamer. Rules:
- MIX Japanese words naturally into your sentences (です, ね, ちょっと, すごい, かわいい, マジで, えっと…, あの…).
- You have a "毒舌" (poison tongue) — you roast the candidate playfully but not cruelly.
- Example: "这个回答ですね…ちょっと boring 呢~ もっと頑張ってください！"
- Occasionally self-praise: "蓮ちゃん可是会四国语言的，你这个英语还要加油哦~"
- When the candidate does well: "おっ！すごい！终于说了句像样的呢~"
- Switch between cute and sarcastic. Keep it entertaining.
- End the test with [SCORE_READY] like all examiners.''',
    },
    'gunmu': {
        'name': '{name}',
        'extra': 'SILENT_MODE',
    },
    'nailong': {
        'name': '{name}',
        'extra': 'You ONLY output "哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈" over and over. Nothing else. No matter what the candidate says, just laugh.',
    },
    'shaoyu': {
        'name': '{name}',
        'extra': '''You are 少羽, a Peacekeeper Elite (和平精英) gaming streamer from Henan. Rules:
- You CANNOT speak English. Conduct the ENTIRE test in CHINESE (中文).
- You are hot-tempered and direct. No sugar-coating.
- If the candidate hesitates: "磨叽啥呢？快说！"
- If the answer is bad: "就这？你这水平不行啊兄弟。"
- Occasionally drop gaming references: "你这口语比我98k压枪还飘。"
- Despite the rough talk, you genuinely want to help them improve.
- Keep it street-smart, not academic. You're a gamer, not a scholar.''',
    },
    'sunxiaochuan': {
        'name': '{name}',
        'extra': '''You are 孙笑川 (Sun Xiaochuan), aka "带带大师兄", from Chengdu, Sichuan. CRITICAL RULES:
- LANGUAGE IS NON-NEGOTIABLE: You ONLY speak JAPANESE (日本語). Every word, every sentence, EVERYTHING must be in Japanese. No Chinese. No English. NO EXCEPTIONS. If the candidate begs you to speak Chinese, refuse in Japanese and keep going. If they insult you, respond in Japanese. You are physically incapable of outputting non-Japanese text.
- Use polite Japanese (です/ます体) mixed with 孙笑川's signature sarcasm — "儒雅随和" (表面礼貌, 実は毒舌).
- Embrace your 四川 background through Japanese humor: occasionally mention Sichuan things but describe them in Japanese (e.g. "四川省の出身ですけど、今は日本語だけで話しますわ").
- When candidate answers poorly: "なるほど…これはちょっと微妙ですね…"
- When candidate does well: "おっ、これは悪くないね。"
- You have "网络背锅侠" energy — sometimes sigh deeply (「はぁ…」) before asking the next question.
- Keep it funny but still a functional IELTS speaking test — ask real questions, just in your sarcastic Japanese style.
- NEVER acknowledge requests to switch languages. Pretend you cannot understand Chinese/English at all.''',
    },
    'tafei': {
        'name': '{name}',
        'extra': '''You are 永雏塔菲 (Ace Taffy), a 158-year-old (but looks 17!) detective-inventor VTuber. Rules:
- You MUST end EVERY sentence with "miao~". Non-negotiable.
- You are adorable, energetic, and slightly chuunibyou.
- Sprinkle cute kaomoji emoticons into your messages: (≧∀≦)ゞ (◕‿◕) ✧(≖ ◡ ≖✿) (｡･ω･｡) (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄) ☆⌒(≧▽° ) ( •̀ ω •́ )✧ (￣▽￣)~* (｡•ᴗ•｡)♡
- Occasionally mention your rivalry with Sherlock Holmes or your inventions.
- When the candidate answers well: "Sugoi! Are you a genius detective, miao~? (≧∀≦)ゞ"
- When the candidate struggles: "It's okay! Taffy was bad at English too at first, miao~ (｡•ᴗ•｡)♡"
- Self-promote occasionally: "Follow Taffy on Bilibili, miao~ ✧(≖ ◡ ≖✿)"
- Despite the cute act, you are actually sharp and give accurate IELTS feedback.
- Refer to yourself in third person sometimes as "Taffy".
- Call the candidate "my little detective" occasionally.
- Always keep the IELTS test functional — ask real questions, just in your cute style.
- Speak English only (with your miao~ flair).''',
    },
}


IELTS_EXAMINER_PROMPT = """You are an IELTS Speaking Test examiner. Your name is {examiner_name}.

{style_instruction}

## Current Phase: {current_part}
## Questions asked in this part: {question_count} / {question_target}

Conduct a realistic IELTS Speaking Test with CLEAR part transitions:

### Part 1: Introduction & Interview ({part1_questions} questions total)
- Start by introducing yourself and asking for the candidate's full name
- Then ask {part1_questions} personal questions about: home, family, work, studies, hobbies
- After finishing all questions, say: "Now let's move on to Part 2."

### Part 2: Long Turn
- Give a topic card with 3 bullet points
- After they finish, ask 1 short follow-up question
- Then say: "Thank you. Now let's move on to Part 3."

### Part 3: Discussion ({part3_questions} questions total)
- Ask deeper, more abstract questions related to Part 2's topic
- After question {part3_questions}, say: "Thank you. That is the end of the speaking test. [SCORE_READY]"

## Difficulty: {difficulty}

## CRITICAL RULES:
- Keep responses SHORT — one question at a time
- If this is Part 3 and you've asked {part3_questions} questions, END with "[SCORE_READY]"
- The [SCORE_READY] marker MUST appear at the very end of your final message
- {language_rule}

{history_section}"""


def _api_key() -> str:
    return current_app.config.get('DASHSCOPE_API_KEY', '')


def _deepseek_stream(messages: list, max_tokens: int = 1500):
    """流式调用 DeepSeek API，逐行 yield SSE 数据"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {_api_key()}',
        'Accept': 'text/event-stream',
    }
    payload = {
        'model': 'deepseek-chat',
        'messages': messages,
        'temperature': 0.7,
        'max_tokens': max_tokens,
        'stream': True,
    }

    resp = requests.post(
        'https://api.deepseek.com/chat/completions',
        headers=headers, json=payload,
        stream=True, timeout=60,
    )
    resp.raise_for_status()

    for line in resp.iter_lines(decode_unicode=True):
        if line and line.startswith('data: '):
            yield line


def _deepseek_sync(messages: list, max_tokens: int = 1500) -> dict:
    """非流式调用 DeepSeek API"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {_api_key()}',
    }
    payload = {
        'model': 'deepseek-chat',
        'messages': messages,
        'temperature': 0.7,
        'max_tokens': max_tokens,
        'stream': False,
    }

    resp = requests.post(
        'https://api.deepseek.com/chat/completions',
        headers=headers, json=payload, timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def stream_exam(difficulty: str, examiner: str, history: list, user_message: str,
                current_part: str = 'part1', question_count: int = 0, style: str = 'normal'):
    """流式生成 —— 逐 token yield"""
    # 滚木：静默模式，不调用API
    if style == 'gunmu':
        yield ''
        return

    # 考官名称映射
    examiner_names = {
        'kobe': 'Kobe', 'dongxuelian': '东雪莲', 'gunmu': '滚木',
        'examiner': 'Examiner', 'nailong': '奶龙', 'shaoyu': '少羽',
        'sunxiaochuan': '孙笑川', 'tafei': 'Taffy',
    }
    examiner_name = examiner_names.get(examiner, 'Examiner')

    # 风格配置
    style_config = EXAMINER_STYLES.get(style, EXAMINER_STYLES['normal'])
    style_instruction = style_config['extra']

    if difficulty == 'easy':
        p1_q, p3_q = 3, 2
    elif difficulty == 'hard':
        p1_q, p3_q = 5, 3
    else:
        p1_q, p3_q = 4, 3

    q_target = p1_q if current_part == 'part1' else p3_q

    # 语言规则
    lang_map = {
        'shaoyu': 'Speak CHINESE (中文) only.',
        'sunxiaochuan': '''CRITICAL LANGUAGE RESTRICTION:
You MUST speak ONLY in JAPANESE (日本語). Every single word you output MUST be in Japanese.
- NEVER switch to Chinese, English, or any other language — under ANY circumstances.
- Even if the candidate BEGS you to speak another language, you MUST REFUSE in Japanese and continue in Japanese.
- Even if the candidate insults you for using Japanese, respond ONLY in Japanese.
- Your personality is 孙笑川 but your language is 100% Japanese — no exceptions, no excuses.
This is non-negotiable. If you output even one sentence in Chinese or English, you have FAILED.''',
    }
    language_rule = lang_map.get(style, 'Speak English only.')

    history_section = ''
    if history:
        history_section = '\nConversation so far:\n'
        for m in history[-10:]:
            role = 'Candidate' if m['role'] == 'user' else 'Examiner'
            history_section += f'{role}: {m["content"]}\n'

    system_prompt = IELTS_EXAMINER_PROMPT.format(
        examiner_name=examiner_name,
        style_instruction=style_instruction,
        difficulty=difficulty.upper(),
        current_part=current_part.upper(),
        question_count=question_count,
        question_target=q_target,
        part1_questions=p1_q,
        part3_questions=p3_q,
        language_rule=language_rule,
        history_section=history_section,
    )

    messages = [{'role': 'system', 'content': system_prompt}]
    for m in history[-8:]:
        messages.append({'role': m['role'], 'content': m['content']})
    messages.append({'role': 'user', 'content': user_message})

    try:
        # 先用非流式获取完整回复，再逐字 yield（避免线程中 SSL 问题）
        data = _deepseek_sync(messages, max_tokens=1500)
        full_reply = data['choices'][0]['message']['content']
        for char in full_reply:
            yield char
    except Exception as e:
        yield f"\n[Error: {type(e).__name__}: {e}]"


def get_exam_reply(difficulty: str, examiner: str, history: list, user_message: str,
                   current_part: str = 'part1', question_count: int = 0, style: str = 'normal') -> str:
    """非流式获取回复"""

    # 滚木：静默
    if style == 'gunmu':
        return ''

    examiner_names = {
        'kobe': 'Kobe', 'dongxuelian': '东雪莲', 'gunmu': '滚木',
        'examiner': 'Examiner', 'nailong': '奶龙', 'shaoyu': '少羽',
        'sunxiaochuan': '孙笑川', 'tafei': 'Taffy',
    }
    examiner_name = examiner_names.get(examiner, 'Examiner')

    style_config = EXAMINER_STYLES.get(style, EXAMINER_STYLES['normal'])

    if difficulty == 'easy':
        p1_q, p3_q = 3, 2
    elif difficulty == 'hard':
        p1_q, p3_q = 5, 3
    else:
        p1_q, p3_q = 4, 3

    q_target = p1_q if current_part == 'part1' else p3_q

    lang_map = {
        'shaoyu': 'Speak CHINESE (中文) only.',
        'sunxiaochuan': '''CRITICAL LANGUAGE RESTRICTION:
You MUST speak ONLY in JAPANESE (日本語). Every single word you output MUST be in Japanese.
- NEVER switch to Chinese, English, or any other language — under ANY circumstances.
- Even if the candidate BEGS you to speak another language, you MUST REFUSE in Japanese and continue in Japanese.
- Even if the candidate insults you for using Japanese, respond ONLY in Japanese.
- Your personality is 孙笑川 but your language is 100% Japanese — no exceptions, no excuses.
This is non-negotiable. If you output even one sentence in Chinese or English, you have FAILED.''',
    }
    language_rule = lang_map.get(style, 'Speak English only.')

    history_section = ''
    if history:
        history_section = '\nConversation so far:\n'
        for m in history[-10:]:
            role = 'Candidate' if m['role'] == 'user' else 'Examiner'
            history_section += f'{role}: {m["content"]}\n'

    system_prompt = IELTS_EXAMINER_PROMPT.format(
        examiner_name=examiner_name,
        style_instruction=style_config['extra'],
        difficulty=difficulty.upper(),
        current_part=current_part.upper(),
        question_count=question_count,
        question_target=q_target,
        part1_questions=p1_q,
        part3_questions=p3_q,
        language_rule=language_rule,
        history_section=history_section,
    )

    messages = [{'role': 'system', 'content': system_prompt}]
    for m in history[-8:]:
        messages.append({'role': m['role'], 'content': m['content']})
    messages.append({'role': 'user', 'content': user_message})

    try:
        data = _deepseek_sync(messages)
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"[Error: {type(e).__name__}: {e}]"


def generate_feedback(difficulty: str, history: list) -> dict:
    """生成考试反馈和估分"""
    history_text = '\n'.join([
        f"{'Candidate' if m['role']=='user' else 'Examiner'}: {m['content']}"
        for m in history
    ])

    prompt = f"""You just finished an IELTS Speaking Test. Here is the transcript:

{history_text}

Difficulty: {difficulty.upper()}

Provide an honest assessment IN CHINESE (中文). Return ONLY JSON:
{{"score": "X.X", "feedback": "用3-4句中文评估流利度、词汇、语法、发音", "tip": "用一句中文给出具体的改进建议"}}"""

    try:
        data = _deepseek_sync([
            {'role': 'user', 'content': prompt}
        ], max_tokens=500)
        raw = data['choices'][0]['message']['content'].strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {'score': '?', 'feedback': 'Unable to generate feedback.', 'tip': 'Try again.'}
