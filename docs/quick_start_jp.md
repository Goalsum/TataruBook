---
title: クイックスタート
locale: jp
sidebar:
  nav: "japanese"
---
本ページは、TataruBookの初心者向けの入門書です。この入門書では、首尾一貫した使用例を通じて、TataruBookの一般的な機能を最初から最後まで使用する方法を説明します。

# データベースファイルを初期化する

まずTataruBookをダウンロードしてインストールします。その方法がわからない場合は、[これ]({{ site.baseurl }}/index_jp.html#どうやってダウンロードやインストールする？)を参照してください。。

便宜上、以下ではTataruBookが２つ目のインストール方法 (実行ファイル方式) を使用してインストールされたと仮定します。１つ目のインストール方法 (Pythonスクリプト方式) が使用された場合は、以下のコマンドの冒頭の`tatarubook`を`python tatarubook.py`に置き換える必要があります。たとえば、データベースファイルを作成するコマンドは`tatarubook init accounting.db`から`python tatarubook.py init accounting.db`に変更する必要があります。

インストールしたら、コマンドラインプログラムを実行して、TataruBookプログラムがあるディレクトリに切り替えて、以下のコマンドを実行します。

~~~
tatarubook init accounting.db
~~~

そのディレクトリ内に`accounting.db`というファイルが追加されました。それは、財務データが保存されている**データベースファイル**です。

次に、[insert]({{ site.baseurl }}/commands_jp.html#insert)コマンドを使用して通貨の種類を追加します。

~~~
tatarubook insert accounting.db asset_types NULL ギル 0
~~~

レコードが[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルに挿入されました。そのレコードが、`asset_index`、`asset_name`、`asset_order`という3つのフィールドが含まれています。`asset_index`の数値は`NULL`で、インデックスが自動的に生成されたことを表します。`asset_name`の数値は`ギル`で、資産(あるいは通貨)の名前を表します。`asset_order`の数値は`0`で、資産のシリアル番号を表します。TataruBookは、複数の資産を表示するときに、このシリアル番号を使って並べ替えを行います。

[insert]({{ site.baseurl }}/commands_jp.html#insert)コマンドは、テーブル名や各フィールドの数値を含むレコードを任意のテーブルに挿入します。
{: .notice}

TataruBookのサポートファイルでは、例の多くは、「ファイナルファンタジー14」というゲームの設定から引用しています。ファイナルファンタジー14ではメインの通貨は`ギル`なので、ここでも例としてギルを使用しています。実際の簿記では、日本円や米ドル、人民元など、任意の通貨名を使用できます。
{: .notice}

前回のコマンドを実行すると、異常なメッセージが表示されました。

~~~
Integrity check after insertion:
start_date should contain exactly 1 row but 0 row(s) are found.
end_date should contain exactly 1 row but 0 row(s) are found.
standard_asset should contain exactly 1 row but 0 row(s) are found.
~~~

それは**データ整合性チェック**を実行した後に報告された問題です。TataruBookには、財務データを分析するための複数の**ビュー**があり、その多くは計算するための特定のデータが必要です。そのため、TataruBookは必要なデータが不足していると判断すると、データの入力を要求します。多くの場合、メッセージの内容だけで、どの問題が報告されたのかを把握できます。

では、メッセージ内で報告された問題を１つずつ解決していきましょう。

まず、[standard_asset]({{ site.baseurl }}/tables_and_views_jp.html#standard_asset)テーブルにレコードが必要であるという問題を解決するために、唯一の通貨として`ギル`を**自国通貨**に設定します。

~~~
tatarubook overwrite accounting.db standard_asset ギル
~~~

次に、**統計期間**の開始日と終了日を設定して、 start_date[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)テーブルと[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)テーブルにそれぞれレコードが必要であるという問題を解決します。

~~~
tatarubook overwrite accounting.db start_date 2022-12-31
tatarubook overwrite accounting.db end_date 2023-12-31
~~~

注意: 統計期間は`start_date`の日の**終了時**から始まります。したがって、2023年全体のデータを集計する場合、`start_date`を`2023-1-1`としないようにしてください。そうすると、`2023-1-1`の一日分のデータが合計に含まれなくなってしまいます。

TataruBookの多くのビューは、[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)および[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)テーブルで設定された統計期間に基づいて内容が決まります。たとえば、[start_stats]({{ site.baseurl }}/tables_and_views_jp.html#start_stats)ビューには、`start_date`の日の終了時点でのアカウント残高と資産価値が表示されます。[end_stats]({{ site.baseurl }}/tables_and_views_jp.html#end_stats)ビューには、`end_date`の日の終了時点でのアカウント残高と資産価値が表示されます。また、ROIに関連するビューには、統計期間の収益が表示されます。 `start_date`と`end_date`を変更することで、統計期間を調整し、指定した過去期間の財務状況を確認できます。
{: .notice}

以上でデータ整合性の問題が解決したため、TataruBookは次のように報告します。

~~~
Integrity check after overwrite:
Everything is fine, no integrity breach found.
~~~

# 簿記を始める

まずアカウントを追加しましょう:

~~~
tatarubook insert accounting.db accounts NULL シャーレアン銀行普通預金 ギル 0
~~~

このコマンドは、アカウントの名前が`シャーレアン銀行普通預金`であり、対応する資産 (通貨) が`ギル`であり、最後のフィールドの値0はそのアカウントが**内部アカウント**であることを意味します。

「内部アカウント」とは何なのか疑問に思うかもしれません。後で答えます。

簿記を始める前に、 シャーレアン銀行の残高が$$ 0 $$ではないと仮定します。この残高をTataruBookに入力します。ただし、TataruBookは[複式簿記]({{ site.baseurl }}/tables_and_views_jp.html#容易化された複式簿記)を使用しますので、**アカウントに資産を追加する際には、別のアカウントから同額の資産を減らす必要があります。**この要件を満たすために、`期首残高`という名前の**外部アカウント**を追加します（最後のフィールドの値は`1`に設定してください）。

~~~
tatarubook insert accounting.db accounts NULL 期首残高 ギル 1
~~~

`期首残高`アカウントから`シャーレアン銀行普通預金`アカウントに資産を移動できるようになりました。次のコマンドを使用して、`シャーレアン銀行普通預金`に$$ 5000 $$ギルの残高を追加します。

~~~
tatarubook insert accounting.db postings NULL 2022-12-31 期首残高 -5000 シャーレアン銀行普通預金 期首残高
~~~

このコマンドを実行すると、TataruBookでは、`2022-12-31`に`期首残高`アカウントが$$ 5000 $$ギル減少し、`シャーレアン銀行普通預金`アカウントが$$ 5000 $$ギル増加したことになります。

次に、飲食費の支出を記録するため、まず「飲食費用」という外部アカウントを追加します。

~~~
tatarubook insert accounting.db accounts NULL 飲食費用 ギル 1
~~~

続いて、2件の消費記録を追加します。

~~~
tatarubook insert accounting.db postings NULL 2023-1-5 シャーレアン銀行普通預金 -20 飲食費用 ホテルのモーニング
tatarubook insert accounting.db postings NULL 2023-1-7 シャーレアン銀行普通預金 -45 飲食費用 ラストスタンドの夕食
~~~

実行後、[export]({{ site.baseurl }}/commands_jp.html#export)コマンドを使用して、[statements]({{ site.baseurl }}/tables_and_views_jp.html#statements)というビューをエクスポートします。

~~~
tatarubook export accounting.db --table statements
~~~

このコマンドにより、`statements.csv`ファイルがディレクトリに生成されます。Excel で開くと、次の内容が確認できます。

| posting_index | trade_date | account_index | amount | target | comment | src_name | asset_index | is_external | target_name | balance |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2022/12/31 | 1 | 5000 | 2 | 期首残高 | シャーレアン銀行普通預金 | 1 | 0 | 期首残高 | 5000 |
| 1 | 2022/12/31 | 2 | -5000 | 1 | 期首残高 | 期首残高 | 1 | 1 | シャーレアン銀行普通預金 | -5000 |
| 2 | 2023/1/5 | 1 | -20 | 3 | ホテルのモーニング | シャーレアン銀行普通預金 | 1 | 0 | 飲食費用 | 4980 |
| 2 | 2023/1/5 | 3 | 20 | 1 | ホテルのモーニング | 飲食費用 | 1 | 1 | シャーレアン銀行普通預金 | 20 |
| 3 | 2023/1/7 | 1 | -45 | 3 | ラストスタンドの夕食 | シャーレアン銀行普通預金 | 1 | 0 | 飲食費用 | 4935 |
| 3 | 2023/1/7 | 3 | 45 | 1 | ラストスタンドの夕食 | 飲食費用 | 1 | 1 | シャーレアン銀行普通預金 | 65 |

このデータは、よく目にする支払明細書に似ています。Excelの`src_name`列でフィルタをかけることで、さまざまな角度からデータを確認できます。例えば、内部アカウントの`シャーレアン銀行普通預金`を選ぶと、そのアカウントの取引と残高を時系列で確認できます。外部アカウントの`飲食費用`を選ぶと、飲食費用の明細を確認できます。つまり、**外部アカウントは収支の分類するためのものです**。TataruBookでは、収支の統計を自由に分類できます。対応する外部アカウントを追加するだけです。

# データを一括インポートする

前のステップを踏まえて、さらなる財務データをインポートしてみましょう。まず、アカウントと外部アカウントを追加します。

~~~
tatarubook insert accounting.db accounts NULL シャーレアン銀行クレジットカード ギル 0
tatarubook insert accounting.db accounts NULL ショッピング ギル 1
tatarubook insert accounting.db accounts NULL 家賃 ギル 1
tatarubook insert accounting.db accounts NULL 給料 ギル 1
~~~

次に、取引記録を一括入力します。データ入力を効率化するため、銀行や他の組織から提供された取引詳細を一括でインポートします。TataruBookは[import]({{ site.baseurl }}/commands_jp.html#import)コマンドを提供します。

まずExcelで以下の形式にデータを整え、`postings.csv`というファイルとして保存します（`posting_index`列のデータはインポートされる時に自動生成されるため、空のままにしておきます。[自動生成されるインデックスフィールド]({{ site.baseurl }}/commands_jp.html#自動生成されるインデックスフィールド)を参照してください）。

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023/2/10 | 給料 | -8000 | シャーレアン銀行普通預金 | 月給 |
| | 2023/2/13 | シャーレアン銀行クレジットカード | -190 | ショッピング | 洋服 |
| | 2023/2/26 | シャーレアン銀行クレジットカード | -140 | ショッピング | 家庭用品 |
| | 2023/3/2 | シャーレアン銀行クレジットカード | -9000 | 家賃 | 半年の家賃 |
| | 2023/3/10 | 給料 | -8000 | シャーレアン銀行普通預金 | 月給 |
| | 2023/3/10 | シャーレアン銀行クレジットカード | -43 | 飲食費用 | ラストスタンドのランチ |
| | 2023/3/20 | シャーレアン銀行普通預金 | -9300 | シャーレアン銀行クレジットカード | クレジットカードの支払い |

次に、以下のコマンドを使用して、CSVファイルの全レコードを[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルにインポートします。

~~~
tatarubook import accounting.db postings.csv
~~~

実際の簿記では、簿記のデータは銀行や証券会社などの組織が提供する取引詳細から得られることが多いため、[insert]({{ site.baseurl }}/commands_jp.html#insert)コマンドよりも[import]({{ site.baseurl }}/commands_jp.html#import)コマンドの方が一般的に使用されます。TataruBookでは挿入データに対して多くのチェックが行われるため、一括インポート中に特定のデータを挿入できない場合があります。 この場合、`import`コマンドは自動的に**ロールバック**を実行し、データベースファイルを`import`コマンドを実行する前の状態に復元します。その後、CSVファイルの内容のエラーを修正してから、再実行できます。その自動ロールバック機能により、巨大なCSVファイルをインポートする際に、部分的な成功によってデータベースファイルの状態が不明確になる心配をする必要がありません。
{: .notice}

次に、収支の分類統計を確認します。まず[export]({{ site.baseurl }}/commands_jp.html#export)コマンドを使用して[income_and_expenses]({{ site.baseurl }}/tables_and_views_jp.html#income_and_expenses)ビューをエクスポートします。

~~~
tatarubook export accounting.db --table income_and_expenses
~~~

次に、生成された`income_and_expenses.csv`ファイルを開きます。内容は次の通りです。

| asset_order | account_index | account_name | total_amount | asset_index | asset_name | total_value |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 3 | ショッピング | 108.0 | 1 | ギル | 108.0 |
| 0 | 5 | ショッピング | 330.0 | 1 | ギル | 330.0 |
| 0 | 6 | 家賃 | 9000.0 | 1 | ギル | 9000.0 |
| 0 | 7 | 給料 | -16000.0 | 1 | ギル | -16000.0 |

これらのデータには、統計期間内の各収支の分類結果を示しています。注: 外部アカウントの取引額は、内部アカウントの反数であるため、正の数値が支出を、負の数値が収入を示します。

[income_and_expenses]({{ site.baseurl }}/tables_and_views_jp.html#income_and_expenses)ビューには、特定の収支における内部アカウントの取引額の合計が表示されます。各内部アカウントごとの詳細な統計データを確認するには、[flow_stats]({{ site.baseurl }}/tables_and_views_jp.html#flow_stats)ビューを使用します。

~~~
tatarubook export accounting.db --table flow_stats
~~~

| flow_index | flow_name | account_index | account_name | amount |
|:-:|:-:|:-:|:-:|:-:|
| 3 | 飲食費用 | 1 | シャーレアン銀行普通預金 | 65.0 |
| 3 | 飲食費用 | 4 | シャーレアン銀行クレジットカード | 43.0 |
| 5 | ショッピング | 4 | シャーレアン銀行クレジットカード | 330.0 |
| 6 | 家賃 | 4 | シャーレアン銀行クレジットカード | 9000.0 |
| 7 | 給料 | 1 | シャーレアン銀行普通預金 | -16000.0 |

[flow_stats]({{ site.baseurl }}/tables_and_views_jp.html#flow_stats)ビューでは、 `シャーレアン銀行普通預金`と`シャーレアン銀行クレジットカード`という２つの内部アカウントの`飲食費用`をそれぞれに確認できます。

これらの取引後の各内部アカウントの最終的な残高を確認するには、[end_stats]({{ site.baseurl }}/tables_and_views_jp.html#end_stats)ビューを使用します。

~~~
tatarubook export accounting.db --table end_stats
~~~

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-12-31 | 1 | シャーレアン銀行普通預金 | 11635.0 | 1 | Gil | 1.0 | 11635.0 | 1.006 |
| 0 | 2023-12-31 | 4 | シャーレアン銀行クレジットカード | -73.0 | 1 | Gil | 1.0 | -73.0 | -0.006 |

注:クレジットカードの残高はマイナスであり、これは多くのクレジットカードアカウントで通常見られる状態です。

{: .notice}

TataruBookでは、アカウント残高を直接に入力できません (前述の期首残高は実際には取引として入力されています)。すべてのアカウント残高は、取引記録から計算されます。簿記において、TataruBookが表示する残高と実際のアカウント残高が一致するか確認することで、入力されたデータの完全性と正確性を検証できます。

# 利子収益

通常、銀行口座の資金には利子がつきます。利子収益を記録するには、まず利子用の外部アカウントを追加します。

~~~
tatarubook insert accounting.db accounts NULL ギルの利子 ギル 1
~~~

複数の異なる通貨を使用している場合は、通貨ごとに異なる外部アカウントを設定する必要があります。利子アカウントを`ギルの利子`と命名しておくと、後から他の通貨を追加する際に、他の通貨の利子に対応する外部アカウントと`ギルの利子`を区別しやすくなります。もちろん、１つの通貨しか使用しない場合は、その必要はありません。
{: .notice}

TataruBookでは、利子収益を統計として管理できます。それを利用するには、利子アカウントを[interest_accounts]({{ site.baseurl }}/tables_and_views_jp.html#interest_accounts)テーブルに追加する必要があります。

~~~
tatarubook insert accounting.db interest_accounts ギルの利子
~~~

これで、利子収益を追加できるようになります。

~~~
tatarubook insert accounting.db postings NULL 2023-3-30 ギルの利子 -30 シャーレアン銀行普通預金 利子
tatarubook insert accounting.db postings NULL 2023-6-30 ギルの利子 -35 シャーレアン銀行普通預金 利子
~~~

次に、[interest_rates]({{ site.baseurl }}/tables_and_views_jp.html#interest_rates)ビューを使用して、現在のデータに基づいて収益率を計算し表示できます。

~~~
tatarubook export accounting.db --table interest_rates
~~~

| account_index | account_name | asset_index | avg_balance | interest | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | シャーレアン銀行普通預金 | 1 | 11278.38 | 65.0 | 0.00576 |

統計期間内における`シャーレアン銀行普通預金`の一日平均残高は$$ 11278.38 $$ギルで、収益率は約$$ 0.576\% $$であったことが表示されます。計算の詳細については、[修正ディーツ法]({{ site.baseurl }}/rate_of_return_jp.html#修正ディーツ法)を参照してください。

{: .notice}

各アカウントの収益率を確認することで、簿記の誤りを防ぐことができます。もし計算された収益率が異常であれば、財務データに誤りが含まれている可能性があります。

# 株式投資

株式投資を記録するには、特定の株式**資産**を追加する必要があります。TataruBookでは、株式と通貨は本質的に区別されず、どちらも一種の資産として扱われます。そのため、[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルに株式資産を追加する方法は、通貨を追加する方法と同じです。

~~~
tatarubook insert accounting.db asset_types NULL ガーロンド・アイアンワークス社の株 1
~~~

末尾のフィルドの`asset_order`の値を`1`に設定すると、[end_stats]({{ site.baseurl }}/tables_and_views_jp.html#end_stats)などのビューで株式資産が通貨資産の後に表示されます。各ビューの資産の表示順序にこだわらない場合は、すべての資産の`asset_order`を`0`に設定できます。

次に、この株を保有する内部アカウントを追加します。TataruBookでは、複数の内部アカウントが同じ株式を保有できますが、ここでは１つの株式アカウントを追加します。

~~~
tatarubook insert accounting.db accounts NULL モーグリ証券_ガーロンドの株 ガーロンド・アイアンワークス社の株 0
~~~

TataruBookでの株式取引は、内部アカウント間で資産を移動される操作に過ぎません。しかし、１つの問題があります。前述のすべての取引では、元のアカウント（振り出し側のアカウント）の減少と、目的アカウント（移動先のアカウント）の増加は常に同等です。そのため、簿記の際には、１つの数値を入力するだけで、TataruBookが元のアカウントと目的アカウントの残高を同時に更新します。ただし、現金アカウントと株式アカウントは異なる資産を持っており、現金アカウントの残高は金額で表されるのに対して、株式アカウントの残高は株式の数で表されます。そのため、取引における現金アカウントの変化額は、株式アカウントの変化額の反数にはなりません (株価がちょうど$$ 1 $$である場合を除きます)。

この問題を解決するために、TataruBookでは、**取引記録において２つのアカウントに異なる資産が含まれる場合、元のアカウントと目的アカウントの両方の変化額を同時に指定する必要がある**というルールがあります。具体的には、insertコマンドの末尾に目的アカウントの変化額を表す数字を追加する必要があります。

~~~
tatarubook insert accounting.db postings NULL 2023-7-3 シャーレアン銀行普通預金 -2000 モーグリ証券_ガーロンドの株 株を買う 200
~~~

この場合、コマンド末尾の$$ 200 $$は、200株が購入されたことを示しています。[import]({{ site.baseurl }}/commands_jp.html#import)コマンドを使用して記録をインポートする場合も、このコマンド (記録) の末尾に、目的アカウントの変動額を示すフィールドを追加する必要があります。

２つのアカウントの変化額が既に取引価格を反映しているため、取引を追加する際にリアルタイムの取引価格を入力する必要はありません。手数料やコミッション、税金を記録する場合には、対応する外部アカウントを追加して、取引を複数の記録に分割して入力してください。

この取引を追加した後、TataruBookは再びデータ整合性に関する問題を報告します。

~~~
Integrity check after insertion:
These (date, asset) pairs need price info in calculation:
(2, 'ガーロンド・アイアンワークス社の株', 1, '2023-12-31')
~~~

これは、TataruBookが資産を計算する際に、自国通貨で他の資産の価値を算出するため、特定の日付の株価情報を入力する必要があるためです。この要件を満たすためには、[prices]({{ site.baseurl }}/tables_and_views_jp.html#prices)テーブルに記録を追加します。

~~~
tatarubook insert accounting.db prices 2023-12-31 ガーロンド・アイアンワークス社の株 12
~~~

[end_stats]({{ site.baseurl }}/tables_and_views_jp.html#end_stats)ビューを使用して、[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)におけるすべてのアカウント残高と価値を確認できます。

もし入門書に従って最初から実行していた場合、`end_stats.csv`ファイルがエクスポートされており、このファイルが既にカレントフォルダに存在するはずです。この場合、以下のコマンドを実行しても、そのファイルは更新されません。これは、TataruBookが既存のファイルを誤って破壊しないようにしているためです。そのため、まず`end_stats.csv`ファイルを削除してから、以下のコマンドを実行してください。
{: .notice--warning}

~~~
tatarubook export accounting.db --table end_stats
~~~

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-12-31 | 1 | シャーレアン銀行普通預金 | 9700.0 | 1 | Gil | 1.0 | 9700.0 | 0.8065 |
| 0 | 2023-12-31 | 4 | シャーレアン銀行クレジットカード | -73.0 | 1 | Gil | 1.0 | -73.0 | -0.0061 |
| 1 | 2023-12-31 | 9 | モーグリ証券_ガーロンドの株 | 200.0 | 2 | ガーロンド・アイアンワークス社の株 | 12.0 | 2400.0 | 0.1996 |

# 投資収益率

株式に加えて、ファンド、債券、商品、先物などの他の資産も同様の方法で記録されます。ファンド資産と対応するアカウントを追加します。

~~~
tatarubook insert accounting.db asset_types NULL エオルゼア100インデックスファンド 1
tatarubook insert accounting.db accounts NULL モーグリ証券_エオルゼア100 エオルゼア100インデックスファンド 0
~~~

このファンドには、購入と償還の両方に関する複数の取引があります。[import]({{ site.baseurl }}/commands_jp.html#import)コマンドを使用して、すべての取引記録を一括でインポートします。
まず、CSVファイルを作成します。

| posting_index | trade_date | src_account | src_change | dst_account | comment | dst_change |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023/8/2 | シャーレアン銀行普通預金 | -3000 | モーグリ証券_エオルゼア100 | ファンド購入 | 1500 |
| | 2023/8/21 | シャーレアン銀行普通預金 | -1000 | モーグリ証券_エオルゼア100 | ファンド購入 | 450 |
| | 2023/9/12 | モーグリ証券_エオルゼア100 | -1000 | シャーレアン銀行普通預金 | ファンド償還 | 2500 |
| | 2023/9/30 | シャーレアン銀行普通預金 | -1200 | モーグリ証券_エオルゼア100 | ファンド購入 | 630 |

各行の最後のフィールドを明確にするため、ヘッダ一行に`dst_change`が追加されました。しかし、実際にはTataruBookではCSVファイルをインポートする際、ヘッダ一行の内容を考慮しないため、指定された順序で各フィールドの値を入力すれば十分です。
{: .notice}

次に、このCSVファイルの内容をインポートします。

~~~
tatarubook import accounting.db postings.csv
~~~

以前のように、[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)の日付におけるエオルゼア100インデックスファンドの価格情報を追加します。

~~~
tatarubook insert accounting.db prices 2023-12-31 エオルゼア100インデックスファンド 2.35
~~~

最後に、[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)の日付におけるすべてのアカウントの残高と価値を確認します。`end_stats.csv`ファイルが既に存在する場合は、まずそれを削除してください。

~~~
tatarubook export accounting.db --table end_stats
~~~

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-12-31 | 1 | シャーレアン銀行普通預金 | 7000.0 | 1 | Gil | 1.0 | 7000.0 | 0.5368 |
| 0 | 2023-12-31 | 4 | シャーレアン銀行クレジットカード | -73.0 | 1 | Gil | 1.0 | -73.0 | -0.0056 |
| 1 | 2023-12-31 | 9 | モーグリ証券_ガーロンドの株 | 200.0 | 2 | ガーロンド・アイアンワークス社の株 | 12.0 | 2400.0 | 0.1840 |
| 1 | 2023-12-31 | 10 | モーグリ証券_エオルゼア100 | 1580.0 | 3 | エオルゼア100インデックスファンド | 2.35 | 3713.0 | 0.2847 |

アカウント別に価値を確認できるだけでなく、[end_assets]({{ site.baseurl }}/tables_and_views_jp.html#end_assets)ビューを使用して各資産の数量と価値を確認できます。

~~~
tatarubook export accounting.db --table end_assets
~~~

| asset_order | date_val | asset_index | asset_name | amount | price | total_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-12-31 | 1 | Gil | 6927.0 | 1.0 | 6927.0 | 0.5312 |
| 1 | 2023-12-31 | 2 | ガーロンド・アイアンワークス社の株 | 200.0 | 12.0 | 2400.0 | 0.1840 |
| 1 | 2023-12-31 | 3 | エオルゼア100インデックスファンド | 1580.0 | 2.35 | 3713.0 | 0.2847 |

終了日の価値は算出されましたが、これらの売買取引を通じてファンド全体の収益がまた気になります。[return_on_shares]({{ site.baseurl }}/tables_and_views_jp.html#return_on_shares)ビューでは、投資対象が含まれている各アカウントの投資収益を確認できます(TataruBookは、自国通貨以外のすべての資産を投資対象として扱います)。

~~~
tatarubook export accounting.db --table return_on_shares
~~~

| asset_order | asset_index | asset_name | account_index | account_name | start_amount | start_value | diff | end_amount | end_value | cash_gained | min_inflow | profit | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2 | ガーロンド・アイアンワークス社の株 | 9 | モーグリ証券_ガーロンドの株 | 0 | 0 | 200.0 | 200.0 | 2400.0 | -2000.0 | 2000.0 | 400.0 | 0.2 |
| 1 | 3 | エオルゼア100インデックスファンド | 10 | モーグリ証券_エオルゼア100 | 0 | 0 | 1580.0 | 1580.0 | 3713.0 | -2700.0 | 4000.0 | 1013.0 | 0.25325 |

これらの投資から、`モーグリ証券_ガーロンドの株`のアカウントの投資収益は$$ 400 $$ギル、収益率は$$ 20\% $$、`モーグリ証券_エオルゼア100`のアカウントの投資収益は$$ 1013.0 $$ギル、収益率は$$ 25.325\% $$であることがわかります。計算の詳細については、[最小初期現金法]({{ site.baseurl }}/rate_of_return_jp.html#最小初期現金法)を参照してください。

TataruBookでは、すべての内部アカウントを**ポートフォリオ**として認定されるため、この資産アロケーション全体の収益率が計算されます。この結果は[portfolio_stats]({{ site.baseurl }}/tables_and_views_jp.html#portfolio_stats)ビューに表示されます。

~~~
tatarubook export accounting.db --table portfolio_stats
~~~

| start_value | end_value | net_outflow | interest | net_gain | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5000.0 | 13040.0 | -6562.0 | -65.0 | 1478.0 | 0.178 |

これらのデータは、統計期間中のすべての内部アカウントの合計投資収益が合計$$ 1478 $$ギル、収益率が$$ 17.8\% $$であることを示しています。注：投資収益には利子収益が含まれています。計算の詳細については、[修正ディーツ法]({{ site.baseurl }}/rate_of_return_jp.html#修正ディーツ法)を参照してください。

TataruBookは通常、個人または家族のすべての資産を簿記に使用されるため、[portfolio_stats]({{ site.baseurl }}/tables_and_views_jp.html#portfolio_stats)ビューで表示される情報は非常に重要です。このビューには、[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)や[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)の日付時点の個人または家族の資産状況や、その期間中の収支、収益情報が表示されます。
{: .notice}

# ウインドウアプリでデータベースファイルを表示する

TataruBookはコマンドラインプログラムであり、グラフィカルユーザーインターフェイス(GUI)は備わっていません。ただし、テーブルとビューを含むすべてのデータベースファイルは**SQLiteファイル形式**で保存されているため、SQLite形式を対応しているソフトウェア(SQLiteの最新機能に対応している場合) を使用すれば、これらのテーブルやビューを表示できます。ここでは、オープンソースソフトウェアである[DB Browser for SQLite](https://sqlitebrowser.org/)を例に説明します。

まず、`DB Browser for SQLite`の[nightly](https://nightlies.sqlitebrowser.org/latest)バージョン（SQLiteの新機能に対応しているのはnightlyバージョンのみです）。次に`DB Browser for SQLite`を起動し、最後に`Open Database`ボタンをクリックして`accounting.db`ファイルを選択します。これにより、データベースファイル内のテーブルやビューのデータが表示されます。

![DB Browser for SQLiteの画面]({{ site.baseurl }}/assets/images/statements_jp.png)

なお、TataruBook以外のソフトウェアを使用してデータベースファイルのデータを編集することも可能ですが、データ入力時に完全な整合性チェックを行うのはTataruBookのみです。そのため、他のソフトウェアを使用してデータベースファイルを編集した場合は、TataruBookでチェックを行う必要があります。もしSQLプログラミング言語を使用できる場合、SQLコマンドを書いて、TataruBookが提供していないデータ分析機能を自作することも可能です。
{: .notice}
