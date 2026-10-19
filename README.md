# ことばに応えるAI挨拶ロボット
**Japanese AI Greeting Robot — ROS 2 / Gazebo / Sentence Transformers**

Physical AI講座の最終課題として作成した、**入力された日本語の意味に応じてロボットアームの挨拶動作を切り替える**デモです。

## 作品概要

テキストで日本語を入力すると、学習済みの多言語文埋め込みモデルが文章を数値ベクトルに変換し、挨拶の代表例文との**意味的類似度**を比較します。最大の類似度を持つ動作を選択し、ROS 2の `JointTrajectory` を通じて、Gazebo上の **CRANE+ V2** を動かします。

**処理の流れ:** 日本語テキスト → Sentence Transformersによる意味判定 → 動作選択 → ROS 2 → Gazebo / CRANE+ V2

| 入力例 | 選ばれる動作 | 動き |
| --- | --- | --- |
| こんにちは | お辞儀 | 第2関節を大きく曲げ、戻す |
| また会おうね！ | 手振り | アームを少し傾け、左右に振る |
| 承知しました。お任せください。 | うなずき | 第2関節を小さく3回動かす |

**AI利用:** 学習済みモデルの推論のみです。追加学習はしていません。AIが関節軌道を新規生成するのではなく、**あらかじめ設計した3種類の関節軌道から選択**します。音声入力には対応していません。

## 技術構成

- **言語モデル:** [sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
- **推論:** Python 3.10 / Sentence Transformers / PyTorch
- **ロボット制御:** ROS 2 Humble、`rclpy`、`trajectory_msgs/JointTrajectory`
- **ロボットシミュレーション:** Gazebo（Ignition）とCRANE+ V2
- **開発環境:** Ubuntu 22.04（講座配布のROS 2・Gazebo Docker環境で検証）

## ファイル構成

| ファイル | 内容 |
| --- | --- |
| `ai_greeting_final.py` | AIの意味判定とROS 2関節軌道制御を統合した実行プログラム |
| `greeting_examples.py` | 基本の代表例文（各動作3文） |
| `greeting_examples_v2.py` | 代表例文を追加した改善版。完成版プログラムが使用 |
| `test_cases.py` | 開発用の12件の判定テスト文章と期待する動作 |
| `requirements.txt` | Pythonの主要な追加依存ライブラリ |

ROS 2、Gazebo、`crane_plus_gazebo` およびロボットモデルは本リポジトリには含まれません。**対応する講義・シミュレーション環境が別途必要**です。

## 実行手順

Ubuntu上に **ROS 2 Humble / Gazebo / CRANE+ V2のシミュレーション環境**があることを前提とします。

### 1. リポジトリとPython環境

```bash
git clone https://github.com/Masa-0101/pai-ai-greeting-robot.git
cd pai-ai-greeting-robot
python3 -m venv --system-site-packages ~/pai_ai_venv
source ~/pai_ai_venv/bin/activate
python -m pip install -r requirements.txt
```

`--system-site-packages` は、ROS 2によりシステムにインストールされたPythonパッケージを仮想環境から参照するための設定です。必要に応じてROS 2の環境設定を読み込んでください。

### 2. ターミナルA：シミュレーター起動

```bash
source /opt/ros/humble/setup.bash
ros2 launch crane_plus_gazebo crane_plus_with_table.launch.py
```

GazeboでCRANE+ V2が表示され、関節コントローラーが起動するまで待ちます。

### 3. ターミナルB：AI挨拶ロボット実行

上記のクローン先ディレクトリから、次のコマンドを実行します。

```bash
source /opt/ros/humble/setup.bash
source ~/pai_ai_venv/bin/activate
python ai_greeting_final.py
```

表示された `日本語を入力（終了は exit）:` に日本語を入力します。終了は `exit` と入力してください。モデルの初回読み込みにはネットワーク接続と一定の時間が必要です。

## 開発中の評価・改善

- **日本語判定:** 代表例文を各動作1文から複数文へ増やし、開発用12例の一致数は **9/12 → 11/12** になりました。これは**改善内容を検討するために参照した開発用テスト**であり、未知データに対する一般的な正解率を示すものではありません。
- **起動速度:** Windows共有領域からLinux側へ仮想環境を移すことで、ライブラリの読み込み時間が実測で **140.9秒 → 40.0秒** に短縮しました。実行環境に依存する参考値です。
- **動作制御:** AIとROS 2の処理を統合し、動作ごとに別のPythonプロセスを起動する方式を廃止しました。

## 現時点の制限

- すべての入力に対し3種類のいずれかを選ぶため、**分類が不確かな文章を保留する機能はありません**。
- あらかじめ定義された関節軌道を送る方式です。動作完了のメッセージは指定した待機時間の終了を意味し、**センサーによる到達確認ではありません**。
- 動作はGazebo上で確認したもので、実機での安全性や動作は検証していません。

本リポジトリは講義最終課題の実装と、その再現に必要な説明をまとめたものです。
