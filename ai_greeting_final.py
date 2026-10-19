import time
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sentence_transformers import SentenceTransformer
from greeting_examples_v2 import EXAMPLES as GROUPS

LABELS = ['お辞儀', '手振り', 'うなずき']
EXAMPLES = [
    'こんにちは。はじめまして。よろしくお願いします。',
    'さようなら。また会いましょう。',
    'はい、わかりました。'
]
JOINTS = [
    'crane_plus_joint1', 'crane_plus_joint2',
    'crane_plus_joint4', 'crane_plus_joint3'
]

# 動作データ：（開始からの秒数、第1関節角度、第2関節角度）
MOTIONS = {
    'お辞儀': [
        (1, 0, 0), (3, 0, 0.35), (5, 0, 0)
    ],
    '手振り': [
        (1, 0, 0), (2, 0, 0.3),
        (3, 0.3, 0.3), (4, -0.3, 0.3),
        (5, 0.3, 0.3), (6, -0.3, 0.3),
        (7, 0, 0.3), (8, 0, 0)
    ],
    'うなずき': [
        (1, 0, 0), (2, 0, 0.16),
        (3, 0, 0), (4, 0, 0.16),
        (5, 0, 0), (6, 0, 0.16),
        (7, 0, 0)
    ]
}

def send_motion(pub, action):
    trajectory = JointTrajectory()
    trajectory.joint_names = JOINTS

    for seconds, joint1, joint2 in MOTIONS[action]:
        point = JointTrajectoryPoint()
        point.positions = [float(joint1), float(joint2), 0.0, 0.0]
        point.time_from_start.sec = seconds
        trajectory.points.append(point)

    pub.publish(trajectory)
    print(f'ロボット動作開始: {action}', flush=True)

    # 動作が終了するまで待機
    time.sleep(MOTIONS[action][-1][0] + 1)
    print('ロボット動作完了', flush=True)

def main():
    print('AIモデルを読み込んでいます...', flush=True)
    start = time.perf_counter()
    model = SentenceTransformer(
        'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    )
    reference = {k: model.encode(v) for k, v in GROUPS.items()}
    print(f'AI準備時間: {time.perf_counter()-start:.1f}秒')

    rclpy.init()
    node = Node('ai_greeting_fast')
    pub = node.create_publisher(
        JointTrajectory,
        '/crane_plus_arm_controller/joint_trajectory',
        10
    )

    try:
        for _ in range(100):
            if pub.get_subscription_count() > 0:
                break
            time.sleep(0.1)

        if pub.get_subscription_count() == 0:
            print('エラー: ロボットに接続できません')
            return

        print('準備完了！日本語を入力してください。')

        while True:
            text = input('\n日本語を入力（終了は exit）: ').strip()
            if text.lower() == 'exit':
                break
            if not text:
                continue

            start = time.perf_counter()
            vector = model.encode([text])
            scores = {
                k: float(model.similarity(vector, v)[0].max())
                for k, v in reference.items()
            }
            action = max(scores, key=scores.get)

            print(f'AIの判定: {action}')
            print(f'判定時間: {time.perf_counter()-start:.2f}秒')
            send_motion(pub, action)

    except (KeyboardInterrupt, EOFError):
        print('\n入力を終了しました')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
