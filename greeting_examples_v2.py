from greeting_examples import EXAMPLES as ORIGINAL

EXAMPLES = {k: list(v) for k, v in ORIGINAL.items()}

EXAMPLES['お辞儀'] += [
    '初対面の方に丁寧にご挨拶します。',
    'お会いするのは今日が初めてですね。'
]

EXAMPLES['手振り'] += [
    'もう帰る時間だね。また今度！',
    'お別れの時間です。どうぞ元気で。',
    'またね。無事に帰ってね。'
]

EXAMPLES['うなずき'] += [
    '説明の内容を理解し、同意します。',
    'その提案で進めることに賛成です。'
]
