---
title: クイックスタート
locale: jp
sidebar:
  nav: "japanese"
---
本ページは、TataruBookの初心者向けの入門書です。この入門書では、首尾一貫した使用例を通じて、TataruBookの一般的な機能を最初から最後まで使用する方法を説明します。

# データベースファイルを初期化する

まずTataruBookをダウンロードしてインストールします。その方法がわからない場合は、[こちら]({{ site.baseurl }}/index_jp.html#どうやってダウンロードやインストールする)を参照してください。Windowsシステムで実行可能ファイルを使用してTataruBookをインストールしたと仮定します。

インストールが完了したら、エクスプローラーを開き、任意フォルダー内の空白の部分を右クリックし、`TataruBook create DB file`を選択します。Windows 11システムでは、一部の右クリックメニュー項目がデフォルトで非表示になっている場合は、まず｢その他のオプションを確認」を選択する必要があります。その後、データベースファイル名を入力するためのウィンドウが表示されます。

~~~
Input DB filename to create with(for example: financial.db):
~~~

ファイル名は任意のものにできますが、拡張子は必ず`.db`とする必要があります。この例では、`accounting.db`と入力してEnterキーを押すと、そのディレクトリ内に`accounting.db`というファイルが追加されました。それは、財務データが保存されている**データベースファイル**です。

データベースファイルを作成する別の方法もあります。オペレーティングシステムのコマンドのターミナルを開き、TataruBookプログラムが配置されているディレクトリに移動し、次のコマンドを実行します。

~~~
tatarubook init accounting.db
~~~

この操作は同様に`accounting.db`のファイルを作成します。実際に、TataruBookの右クリックメニュー機能を使用する場合、TataruBookは自動的にメニュー項目を対応するコマンドに変換して実行します。そのため、各右クリックメニュー項目と対応するコマンドで同じ機能を使用できます。

次に、簿記のためには、まず通貨を追加する必要があります。通貨を追加するには、[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルを変更する必要があります。テーブルの内容を変更するために、まずテーブルにどのようなフィールドがあるか分かるようにする必要があります。そのため、まずexport機能を使用してこのテーブルをエクスポートしてから、変更することをお勧めします。

先ほど作成した`accounting.db`ファイルを右クリックし、`TataruBook export`というサブメニューから`asset_types`を選択します。

![DB文件的快捷菜单]({{ site.baseurl }}/assets/images/context_menu.png)

ポップアップで`asset_types.csv`ファイルが作成されたことが表示されます。そのポップアップを閉じ、Excelで`asset_types.csv`ファイルを開くと、ヘッダー一行のみを含む空のテーブルが表示されます。

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
||||

そして、そのテーブルに内容を追加します。`asset_index`フィールドは自動生成されたインデックスです。内容を追加する際、この列は空にしてください。`asset_name`フィールドは資産（通貨）の名前を表します。この例では、`ギル`と入力します。`asset_order`フィールドは並べ替えに資産の番号です。ひとまずは`0`と入力しておきます。入力後のテーブル内容は以下のようになります。

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
|| ギル | 0 |

TataruBookのサポートファイルでは、例の多くは、「ファイナルファンタジー14」というゲームの設定から引用しています。ファイナルファンタジー14ではメインの通貨は`ギル`なので、ここでも例としてギルを使用しています。実際の簿記では、JPY、USD、RMB など、任意の通貨名を使用できます。
{: .notice}

次に、追加された行を選択し、`Ctrl+C`のショートカットでクリップボードにコピーし、`accounting.db`ファイルを右クリックして、`TataruBook paste`というサブメニューから`asset_types`を選択します。これにより、新しく追加された行が`accounting.db`ファイル内の`asset_types`テーブルに挿入されます。

実際には、テーブル内の任意の行または複数の行をコピーし、`TataruBook paste`コマンドを使用してデータベースファイルに挿入することができます。コピーされた内容にヘッダー一行が含まれている場合、`TataruBook paste`コマンドは自動的に識別し、ヘッダー一行をスキップします。
{: .notice}

さっきのTataruBook pasteコマンドを実行すると、ポップアップで異常なメッセージが表示されました。

~~~
Integrity check after insertion:
start_date should contain exactly 1 row but 0 row(s) are found.
end_date should contain exactly 1 row but 0 row(s) are found.
standard_asset should contain exactly 1 row but 0 row(s) are found.
~~~

それは**データ整合性チェック**を実行した後に報告された問題です。TataruBookには、財務データを分析するための複数の**ビュー**があり、その多くは計算するための特定のデータが必要です。そのため、TataruBookは必要なデータが不足していると判断すると、データの入力を要求します。多くの場合、エラーメッセージに書かれたコードによって、問題を推測できます。

では、エラーメッセージが表示された場合は、該当する対処方法をお試しください。

まず、**統計期間**の開始日と終了日を設定して、[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)テーブルと[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)テーブルにそれぞれレコードが必要であるという問題を解決します。テキストを編集できるところで`2022-12-31`と入力し、それをコピーします。そして、`accounting.db`ファイルを右クリックし、`TataruBook paste`のサブメニューから`start_date`を選択し、統計期間の開始日が設定されます。同じ方法で、統計期間の終了日を`2023-12-31`に設定します。

注意: 統計期間は`start_date`の日の**終了時**から始まります。したがって、2023年全体のデータを集計する場合、`start_date`を`2023-1-1`としないようにしてください。そうすると、`2023-1-1`の一日分のデータが計に含まれなくなってしまいます。

TataruBookのほとんどのビューの内容は、[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)テーブルと[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)テーブルで定義される統計期間によって決定されます。例えば、[start_stats]({{ site.baseurl }}/tables_and_views_jp.html#start_stats)ビューは`start_date`の終了時の残高と価値を示します。[end_stats]({{ site.baseurl }}/tables_and_views_jp.html#end_stats)ビューは`end_date`の終了時の残高と価値を示します。ROIに関するビューは統計期間内の収益率を示します。`start_date`と`end_date`を変えることで、統計期間を変更できて、特定の過去期間の財務状態を確認することができます。
{: .notice}

次に、[standard_asset]({{ site.baseurl }}/tables_and_views_jp.html#standard_asset)テーブルにレコードが必要であるという問題を解決するために、唯一の通貨として`ギル`を**自国通貨**に設定します。先ほど作成した`asset_types.csv`テーブル内の`ギル`を含むセルをコピーし、`accounting.db`ファイルを右クリックして、`TataruBook paste`のサブメニューから`standard_asset`を選択して、自国通貨が`ギル`に設定されます。

実際のTataruBookのデータでは、資産を参照する際に`asset_index`フィールドではなく、`asset_name`フィールドの値が使用されます。これは、`asset_name`フィールドがテーブルのメインキーではなく、同名の資産が存在する可能性があるためです。ただし、ユーザーが`asset_index`フィールドの値を直接入力するのは不便です。そのため、TataruBookでは、`asset_index`フィールドの値を入力する必要があるところで、`asset_name`フィールドの値を入力できるようにしています。入力された値が資産のタイプを特定できる場合、TataruBookは内部で自動的にそれを対応する`asset_index`フィールドの値に変換します。
{: .notice}

以上でデータ整合性の問題が解決しました。最後の`TataruBook paste`の操作で表示されたポップアップで、TataruBookは次のように報告します。

~~~
Integrity check after overwrite:
Everything is fine, no integrity breach found.
~~~

TataruBookは、データを変更するたびに自動的にデータ整合性チェックを行います。 ショートカットメニューから`TataruBook check`を選択することで、いつでも手動でチェックを行うことができます。

# 簿記を始める

まずアカウントを追加しましょう。`accounting.db`ファイルを右クリックし、`TataruBook export`のサブメニューから`accounts`を選択し、生成された`accounts.csv`ファイルを開き、右クリックで｢新しい行を追加する」を選択して、以下のような新しい行を追加します。

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
|| シャーレアン銀行普通預金 | ギル | 0 |

この行をクリップボードにコピーして、`accounting.db`ファイルを右クリックし、`TataruBook paste`のサブメニューから`accounts`を選択し、挿入してください。

データベースファイルのテーブルに内容を挿入するプロセスはこれと同様なので、以降では挿入操作のプロセスについては繰り返し説明しません。

この一行は、アカウントの名前が`シャーレアン銀行普通預金`であり、対応する資産 (通貨) が`ギル`であり、最後のフィールドの値`0`はそのアカウントが**内部アカウント**であることを意味します。

｢内部アカウント」とは何なのか疑問に思うかもしれません。このセクションの最後に答えます。

簿記を始める前に、`シャーレアン銀行`の残高が$$ 0 $$ではないと仮定します。この残高をTataruBookに入力します。ただし、TataruBookは[複式簿記]({{ site.baseurl }}/tables_and_views_jp.html#容易化された複式簿記)を使用しますので、**アカウントに資産を追加する際には、別のアカウントから同額の資産を減らす必要があります**。この要件を満たすために、[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルに`期首残高`という名前の**外部アカウント**を追加します(今回`is_external`フィールドの値は`1`であることに注意してください）。


| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
|| 期首残高 | ギル | 1 |

`TataruBook paste`の操作は**同期**ではなく、**入力**であることにご注意ください。現在編集しているテーブルで、コンテンツの一部がデータベースファイルに存在している場合は、追加された分だけをコピーして`TataruBook paste`の操作を実行します。
{: .notice}

この一行を挿入すると、`期首残高`のアカウントから`シャーレアン銀行普通預金`のアカウントに資産を移すことができます。[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルにコンテンツを挿入して取引記録を追加します

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
|| 2022-12-31 | 期首残高 | -5000 | シャーレアン銀行普通預金 | 残高 |

例えば、上記の表を例に説明します。挿入操作を実行すると、TataruBookでは、`2022-12-31`に`历史结余`アカウントが $$ 5000 $$ギル減少し、`シャーレアン銀行普通預金`アカウントが$$ 5000 $$ギル増加したことになります。ですから、`シャーレアン銀行普通預金`アカウントには`2022-12-31`の終わる時点で$$ 5000 $$ギルの残高が残ります。

次に、飲食費の支出を記録するため、まず[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルに`飲食費用`という外部アカウントを追加します。

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
|| 飲食費用 | ギル | 1 |

続いて、[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルに2件の消費記録を追加します。

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
|| 2023-1-5 | シャーレアン銀行普通預金 | -20 | 飲食費用 | ホテルのモーニング |
|| 2023-1-7 | シャーレアン銀行普通預金 | -45 | 飲食費用 | ラストスタンドの夕食 |

実行後、`accounting.db`を右クリックし、`TataruBook export`のサブメニューから`statements`を選択し、[statements]({{ site.baseurl }}/tables_and_views_jp.html#statements)というビューをエクスポートします。そして、Excelを使用して、ディレクトリに生成された`statements.csv`ファイルを開くと、次の内容が確認できます。

| posting_index | trade_date | account_index | amount | target | comment | src_name | asset_index | is_external | target_name | balance |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2022/12/31 | 1 | 5000 | 2 | 期首残高 | シャーレアン銀行普通預金 | 1 | 0 | 期首残高 | 5000 |
| 1 | 2022/12/31 | 2 | -5000 | 1 | 期首残高 | 期首残高 | 1 | 1 | シャーレアン銀行普通預金 | -5000 |
| 2 | 2023/1/5 | 1 | -20 | 3 | ホテルのモーニング | シャーレアン銀行普通預金 | 1 | 0 | 飲食費用 | 4980 |
| 2 | 2023/1/5 | 3 | 20 | 1 | ホテルのモーニング | 飲食費用 | 1 | 1 | シャーレアン銀行普通預金 | 20 |
| 3 | 2023/1/7 | 1 | -45 | 3 | ラストスタンドの夕食 | シャーレアン銀行普通預金 | 1 | 0 | 飲食費用 | 4935 |
| 3 | 2023/1/7 | 3 | 45 | 1 | ラストスタンドの夕食 | 飲食費用 | 1 | 1 | シャーレアン銀行普通預金 | 65 |

このデータは、よく目にする支払明細書に似ています。Excelの`src_name`列でフィルタをかけることで、さまざまな角度からデータを確認できます。例えば、内部アカウントの`シャーレアン銀行普通預金`を選ぶと、そのアカウントの取引と残高を時系列で確認できます。外部アカウントの`飲食費用`を選ぶと、飲食費用の明細を確認できます。つまり、**内部アカウントは資産や負債をふ込んでおり、外部アカウントは収支の分類するためのものです**。TataruBookでは、収支の統計を自由に分類できます。対応する外部アカウントを追加するだけです。

# 分類統計

前のステップを踏まえて、さらなる財務データをインポートしてみましょう。まず、[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルに内部アカウントと外部アカウントを追加します。

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
|| シャーレアン銀行クレジットカード | Gil | 0 |
|| ショッピング | ギル | 1 |
|| 家賃 | ギル | 1 |
|| 給料 | ギル | 1 |

然后，向[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)表添加一批交易记录：

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023-2-10 | 給料 | -8000 | シャーレアン銀行普通預金 | 月給 |
| | 2023-2-13 | シャーレアン銀行クレジットカード | -190 | ショッピング | 洋服 |
| | 2023-2-26 | シャーレアン銀行クレジットカード | -140 | ショッピング | 家庭用品 |
| | 2023-3-2 | シャーレアン銀行クレジットカード | -9000 | 家賃 | 半年の家賃 |
| | 2023-3-10 | 給料 | -8000 | シャーレアン銀行普通預金 | 月給 |
| | 2023-3-10 | シャーレアン銀行クレジットカード | -43 | 餐饮费 | ラストスタンドのランチ |
| | 2023-3-20 | 萨雷安银行活期 | -9300 | シャーレアン銀行クレジットカード | クレジットカードの支払い |

実際の簿記では、簿記のデータは銀行や証券会社などの組織が提供する取引詳細から得られることが多いため、各取引を[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルが要求するフォーマットに手入力するのは明らかに面倒なので、Excel関数を使って、生データを自動的に変換することをお勧めします。[データインポートガイド]({{ site.baseurl }}/importing_data_jp.html)では、Excelを使って簿記データを自動的にインポートする方法について詳しく説明しています。
{: .notice}

TataruBookでは挿入データに対して多くのチェックが行われるため、一括インポート中に特定のデータを挿入できない場合があります。 この場合、自動的に**ロールバック**を実行し、データベースファイルをインポート前の状態に復元します。その後、テーブルの内容のエラーを修正すると、入力を再実行できます。その自動ロールバック機能により、巨大なデータをインポートする際に、部分的な成功によってデータベースファイルの状態が不明確になる心配は必要ありません。
{: .notice}

次に、収支の分類統計を確認します。まず[income_and_expenses]({{ site.baseurl }}/tables_and_views_jp.html#income_and_expenses)ビューをエクスポートします。以下のような内容で表示されます。

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

通常、銀行口座の資金には利子がつきます。利子収益を記録するには、まず[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルに利子用の外部アカウントを追加します。

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
|| ギルの利子 | ギル | 1 |

複数の異なる通貨を使用している場合は、通貨ごとに異なる外部アカウントを設定する必要があります。利子アカウントを`ギルの利子`と命名しておくと、後から他の通貨を追加する際に、他の通貨の利子に対応する外部アカウントと`ギルの利子`を区別しやすくなります。もちろん、１つの通貨しか使用しない場合は、その必要はありません。
{: .notice}

TataruBookでは、利子収益を統計として管理できます。それを利用するには、利子アカウントを[interest_accounts]({{ site.baseurl }}/tables_and_views_jp.html#interest_accounts)テーブルに追加する必要があります。

| interest_accounts |
|:-:|
| ギルの利子 |

これで、[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)ーブルに利子収益を追加できるようになります。

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023-3-30 | ギルの利子 | -30 | シャーレアン銀行普通預金 | ギル |
| | 2023-6-30 | ギルの利子 | -35 | シャーレアン銀行普通預金 | ギル |


次に、[interest_rates]({{ site.baseurl }}/tables_and_views_jp.html#interest_rates)ビューを使用して、現在のデータに基づいて収益率を計算し表示できます。

| account_index | account_name | asset_index | avg_balance | interest | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | シャーレアン銀行普通預金 | 1 | 11278.38 | 65.0 | 0.00576 |

統計期間内における`シャーレアン銀行普通預金`の一日平均残高は$$ 11278.38 $$ギルで、収益率は約$$ 0.576\% $$であったことが表示されます。計算の詳細については、[修正ディーツ法]({{ site.baseurl }}/rate_of_return_jp.html#修正ディーツ法)を参照してください。

{: .notice}

各アカウントの収益率を確認することで、簿記の誤りを防ぐことができます。もし計算された収益率が異常であれば、財務データに誤りが含まれている可能性があります。

# 株式投資

株式投資を記録するには、特定の株式**資産**を追加する必要があります。TataruBookでは、株式と通貨は本質的に区別されず、どちらも一種の資産として扱われます。そのため、[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルに株式資産を追加する方法は、通貨を追加する方法と同じです。

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
|| ガーロンド・アイアンワークス | 1 |

末尾のフィルドの`asset_order`の値を`1`に設定すると、[end_stats]({{ site.baseurl }}/tables_and_views_jp.html#end_stats)などのビューで株式資産が通貨資産の後に表示されます。各ビューの資産の表示順序にこだわらない場合は、すべての資産の`asset_order`を`0`に設定できます。

次に、この株を保有する内部アカウントを追加します。TataruBookでは、複数の内部アカウントが同じ株式を保有できますが、現時点では[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルに１つの株式アカウントを追加するだけです。

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
|| モーグリ証券_ガーロンドの株 | ガーロンド・アイアンワークス社の株 | 0 |

TataruBookでの株式取引は、内部アカウント間で資産を移動される操作に過ぎません。しかし、１つの問題があります。前述のすべての取引では、元のアカウント（振り出し側のアカウント）の減少と、目的アカウント（移動先のアカウント）の増加は常に同等です。そのため、簿記の際には、１つの数値を入力するだけで、TataruBookが元のアカウントと目的アカウントの残高を同時に更新します。ただし、現金アカウントと株式アカウントは異なる資産を持っており、現金アカウントの残高は金額で表されるのに対して、株式アカウントの残高は株式の数で表されます。そのため、取引における現金アカウントの変化額は、株式アカウントの変化額の反数にはなりません (株価がちょうど$$ 1 $$である場合を除きます)。

この問題を解決するために、TataruBookでは、**取引記録において２つのアカウントに異なる資産が含まれる場合、元のアカウントと目的アカウントの両方の変化額を同時に指定する必要がある**というルールがあります。具体的には、[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)に入力された一行の末尾に目的アカウントの変化額を表す数字を追加する必要があります。

| posting_index | trade_date | src_account | src_change | dst_account | comment ||
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023-7-3 | シャーレアン銀行普通預金 | -2000 | モーグリ証券_ガーロンドの株 | 株を買う | 200 |

この場合、コマンド末尾の$$ 200 $$は、200株が購入されたことを示しています。[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルがエクスポートされた時にこの列が存在しなかったため、自分でこの列の意味を覚えておく必要があります。最後の列の1行目に`dst_change`を書くことで、ヘッダ一行を編集して、データの意味を明確にすることもできます。TataruBookでは、挿入されたデータを処理する際に、ヘッダーの内容は気にしません。

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

もし入門書に従って最初から実行していた場合、`end_stats.csv`ファイルがエクスポートされており、このファイルが既にカレントフォルダに存在するはずです。この場合、まず`end_stats.csv`ファイルを削除してから、`export`コマンドを実行してください。そうしないと、`export`コマンドの実行時に失敗が報告され、`end_stats.csv`ファイルの内容は変わりません。これは、TataruBookが既存のファイルを誤って破壊しないようにしているためです。
{: .notice--warning}

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-12-31 | 1 | シャーレアン銀行普通預金 | 9700.0 | 1 | Gil | 1.0 | 9700.0 | 0.8065 |
| 0 | 2023-12-31 | 4 | シャーレアン銀行クレジットカード | -73.0 | 1 | Gil | 1.0 | -73.0 | -0.0061 |
| 1 | 2023-12-31 | 9 | モーグリ証券_ガーロンドの株 | 200.0 | 2 | ガーロンド・アイアンワークス社の株 | 12.0 | 2400.0 | 0.1996 |

# 投資収益率

株式に加えて、ファンド、債券、商品、先物などの他の資産も同様の方法で記録されます。[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルにファンド資産を追加します。

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
|| エオルゼア100インデックスファンド | 1 |

[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルにアカウントを追加します。

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
|| モーグリ証券_エオルゼア100 | エオルゼア100インデックスファンド | 0 |

このファンドには、購入と償還の両方に関する複数の取引があります。[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルに、以下のような取引記録をインポートします。

| posting_index | trade_date | src_account | src_change | dst_account | comment | dst_change |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| | 2023/8/2 | シャーレアン銀行普通預金 | -3000 | モーグリ証券_エオルゼア100 | ファンド購入 | 1500 |
| | 2023/8/21 | シャーレアン銀行普通預金 | -1000 | モーグリ証券_エオルゼア100 | ファンド購入 | 450 |
| | 2023/9/12 | モーグリ証券_エオルゼア100 | -1000 | シャーレアン銀行普通預金 | ファンド償還 | 2500 |
| | 2023/9/30 | シャーレアン銀行普通預金 | -1200 | モーグリ証券_エオルゼア100 | ファンド購入 | 630 |

各行の最後のフィールドを明確にするため、ヘッダ一行に`dst_change`が追加されました。しかし、実際にはTataruBookではCSVファイルをインポートする際、ヘッダ一行の内容を考慮しないため、指定された順序で各フィールドの値を入力すれば十分です。
{: .notice}

和之前一样，向[prices]({{ site.baseurl }}/tables_and_views_jp.html#prices)テーブルに[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)の日付における`エオルゼア100インデックスファンド`の価格情報を追加します。

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2023-12-31 | エオルゼア100インデックスフ | 2.35 |

完了したら、[end_stats]({{ site.baseurl }}/tables_and_views_jp.html#end_stats)ビューで[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)の日付におけるすべてのアカウントの残高と市場価値を確認します（`end_stats.csv`ファイルが既に存在する場合は、まずそれを削除してから`export`コマンドを実行してください）。

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-12-31 | 1 | シャーレアン銀行普通預金 | 7000.0 | 1 | Gil | 1.0 | 7000.0 | 0.5368 |
| 0 | 2023-12-31 | 4 | シャーレアン銀行クレジットカード | -73.0 | 1 | Gil | 1.0 | -73.0 | -0.0056 |
| 1 | 2023-12-31 | 9 | モーグリ証券_ガーロンドの株 | 200.0 | 2 | ガーロンド・アイアンワークス社の株 | 12.0 | 2400.0 | 0.1840 |
| 1 | 2023-12-31 | 10 | モーグリ証券_エオルゼア100 | 1580.0 | 3 | エオルゼア100インデックスファンド | 2.35 | 3713.0 | 0.2847 |

アカウント別に価値を確認できるだけでなく、[end_assets]({{ site.baseurl }}/tables_and_views_jp.html#end_assets)ビューを使用して各資産の数量と価値を確認できます。

| asset_order | date_val | asset_index | asset_name | amount | price | total_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-12-31 | 1 | Gil | 6927.0 | 1.0 | 6927.0 | 0.5312 |
| 1 | 2023-12-31 | 2 | ガーロンド・アイアンワークス社の株 | 200.0 | 12.0 | 2400.0 | 0.1840 |
| 1 | 2023-12-31 | 3 | エオルゼア100インデックスファンド | 1580.0 | 2.35 | 3713.0 | 0.2847 |

最終の価値は算出されましたが、投資者は、これらの売買取引を通じてファンド全体の収益がまた気になります。[return_on_shares]({{ site.baseurl }}/tables_and_views_jp.html#return_on_shares)ビューでは、投資対象が含まれている各アカウントの投資収益を確認できます(TataruBookは、自国通貨以外のすべての資産を投資対象として扱います)。

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

# グラフィカルインターフェイスソフトウェアでデータベースファイルを表示する

TataruBookはグラフィカルユーザーインターフェイス(GUI)は備わっていませんが、テーブルとビューを含むすべてのデータベースファイルは**SQLiteファイル形式**保存されています。そのため、SQLite形式を対応しているソフトウェアを使用すれば、これらのテーブルやビューを表示できます。ここでは、オープンソースソフトウェアである[DB Browser for SQLite](https://sqlitebrowser.org/)を例に説明します。まず、`DB Browser for SQLite`をダウンロードしてインストールし、次に`DB Browser for SQLite`を起動し、最後に`データベースファイルを開く`ボタンをクリックして、`accounting.db`文件ファイルを選択します。これにより、データベースファイル内のテーブルやビューのデータが表示されます。

![DB Browser for SQLiteの画面]({{ site.baseurl }}/assets/images/statements_jp.png)

なお、TataruBook以外のソフトウェアを使用してデータベースファイルのデータを編集することも可能ですが、データ入力時に完全な整合性チェックを行うのはTataruBookのみです。そのため、他のソフトウェアを使用してデータベースファイルを編集した場合は、TataruBookでチェックを行う必要があります。もしSQLプログラミング言語を使用できる場合、SQLコマンドを書いて、TataruBookが提供していないデータ分析機能を自作することも可能です。
{: .notice}
