---
title: テーブルとビュー
locale: jp
sidebar:
  nav: "japanese"
---
このページでは、データベースファイルに含まれるすべてのテーブルとビューについて説明します。

**テーブル**は、ユーザーからの財務データが格納されており、すべての財務諸表のデータソースとして機能します。TataruBookでは、データの整合性と一貫性を確保するために、データを追加、変更、削除する際に、データ間で矛盾や不一致が生じないよう、各種のチェックを行います。

**ビュー**は、テーブル内のデータを基に計算された財務諸表であり、資産、分類された収支、投資収益率などの統計情報を含んでいます。テーブルのデータが変更されると、すべてのビューの統計情報が即座に再計算されて更新されます。通常、ビューの更新は非常に迅速で、遅延を感じることはありません。また、手動でビューの更新をトリガーする必要はありません。

ビューには、ユーザー向けの財務諸表としてのビューと、他のビューで使用される中間計算結果を表示しますビューの2種類があります。通常、中間計算結果のビューを意識する必要はありませんが、財務諸表のデータに疑問がある場合は、計算詳細を確認するために中間結果のビューを参照することができます。また、SQLコマンドを作る上級ユーザーにとっては、中間結果のビューが役立つこともあります。

タイトルが`check`で始まるビューは、すべてデータの整合性を確認するために使用されます。データに整合性の問題がない場合、これらのビューは空のままです。しかし、TataruBookが冒頭部分は`check`であるビューにデータが存在することを発見すると、コマンドを通じて関連するデータエラーを報告し、修正が必要であることを知らせます。

# 容易化された複式簿記

![记账数据架构]({{ site.baseurl }}/assets/images/architecture.png)

TataruBookは、「１つの取引には２つのアカウントが必要である」という[複式簿記](https://ja.wikipedia.org/wiki/%E8%A4%87%E5%BC%8F%E7%B0%BF%E8%A8%98)のルールに従っていますが、専門的な会計方法におけるアカウントの分類や、それぞれのアカウントに[規定された正負の符号](https://en.wikipedia.org/wiki/Debits_and_credits)を使用していません。個人や家庭での簿記において、専門的な会計方法に厳守すると、簿記が複雑になり、理解しづらくなることがあります。そのため、TataruBookでは、よりシンプルで直感的な簿記方法を採用し、すべてのアカウントを２種類に分けます：

- **内部アカウント**には、取引金額がプラスであれば資産が増加し、マイナスであれば資産減少することを表します。残高がプラスであれば資産を保有し、マイナスであれば対外負債を負っていることを表します。
- **外部アカウント**には、取引金額がプラスであれば支出、マイナスであれば収入または利子を表します。

このようにして、取引に関わる２つのアカウントの取引金額を合計すると、常に$$ 0 $$になります。(２つのアカウントが同じ資産を保有している場合）。任意の時点で、すべての内部アカウントの残高を合計することで、その時点の資産額が得られます。

TataruBookの容易化された複式簿記では、会計の専門用語と完全に一致しない用語がいくつかあります。例えば、TataruBookでの**資産（Asset）**は、会計式での**負債**プラス**純資産**に等しいではなく、通貨や異なる単位価格を持つ取引可能な所有権を指します。
{: .notice}

TataruBookで使用されている簿記方法では、各取引に関わる２つのアカウントには異なる資産（例えば、異なる2種類の通貨、または１つの通貨と１つの株式）が含まれる可能性があるため、これらの取引では２つのアカウントの変動額を合計しても、通常は$$ 0 $$と一致しません（2つの資産の単位価格がちょうど等しい場合を除きます）。TataruBookでは１つの資産を**標準資産**（即ち自国通貨）として指定する必要があり、他のすべての資産は、指定された時点での単位価格に基づいて標準資産に換算されて計算されます。

一部のビューでは、標準資産以外の資産を**株式（share）**，標準資産を**現金（cash）**に関わる名称と呼びます。注：これは理解やすくするための仮称であり、現実の株式や現金と完全に対応しているものではありません。 例えば、標準資産が人民元と指定した場合、保有する米ドルはTataruBookでは「株式」として扱われます。これは、米ドルの為替レートが変動し、米ドルを人民元に換算し評価した際に、損益が生じる可能性があるためです。資産の量は整数に限らず、小数でも問題ありません。たとえば、簿記上では$$ 0.1 $$ドルや$$ 0.001 $$ドルを記入することが可能です。

# テーブル

## asset_types

資産の種類のリストです。TataruBookでは、**資産**とは、特定の通貨、特定の株式、または単位価格を持つ特定のファンドなど、それぞれが**独立した単位価格**を持つ取引可能な所有権です。

１種類の通貨しか使用せず、他の投資対象やコモディティを保有・取引しない場合、asset_typesテーブルのレコードは１つだけになります。それは、使用している通貨です。

**フィールド**
- `asset_index`（整数）：自動的に生成されるインデックスです。入力する必要がありません。
- `asset_name`（文字列）：資産の名前です。空欄にはできません。ビューに表示用で、計算には影響しません。
- `asset_order`（整数）：資産のシリアル番号です。空欄にはできません。これは、ビューで資産を順位付けして表示するためにのみ使用され、計算には影響しません (シリアル番号が小さいほど、前に表示されます)。特に順序にこだわらない場合は、すべての資産の`asset_order`を$$ 0 $$に設定しても問題ありません。

## standard_asset

標準資産であり、**自国通貨**として使用されます。すべての他の資産は、この標準資産に換算して市場価値が計算されます。

**フィールド**
- `asset_index`（整数）：資産のインデックスです。空欄にはできません。[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルに存在する資産のインデックスである必要があります。

**制約**
- このテーブルには1つのレコードしか許可されません。
- 標準資産の価格は常に$$ 1 $$に固定されているため、このテーブルの`asset_index`は、[prices]({{ site.baseurl }}/tables_and_views_jp.html#prices)テーブル内の任意の`asset_index`と一致させることはできません。（[check_standard_prices]({{ site.baseurl }}/tables_and_views_jp.html#check_standard_prices)ビューでチェックされます）

## accounts

アカウントのリストです。**アカウント**というのは、**独立した残高**を持つ実体を指します。個人はある銀行に複数の口座、例えば、普通預金口座、証券口座、クレジット口座などを開設ことがあり、アカウントに名前を付ける際には注意が必要です。

アカウントの残高の単位は、アカウントに含まれる資産の種類によって定義されます。たとえば、資産が通貨の場合、残高は通貨の金額になり、資産が株式の場合、残高は株数になります。

アカウントの残高が必ずしもプラスであるとは限らず、マイナスの場合は負債を意味します。たとえば、ほとんどの場合、クレジットカードの残高はマイナスで、これは将来返済する必要がある負債があることを示しています。

アカウントには**内部アカウント**と**外部アカウント**の2種類があります。[容易化された複式簿記]({{ site.baseurl }}/tables_and_views_jp.html#容易化された複式簿記)を参照してください。外部アカウントは特定の収入/支出を表しており、これを定義することで、収入/支出の分類方法を決定します。

**フィールド**
- `account_index`（整数）：自動的に生成されるインデックスです。入力する必要がありません。
- `account_name`（文字列）：アカウントの名前です。空欄にはできません。ビューに表示用で、計算には影響しません。
- `asset_index`（整数）：アカウントに含まれる資産のインデックスです。空欄にはできません。[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルに存在する資産のインデックスである必要があります。
- `is_external`（`0`または`1`）：`0`は内部アカウント、`1`は外部アカウントを示します。

## interest_accounts

利子アカウントのリストです。**利子アカウント**は、預金や資産運用商品などの利子所得を記録するための特殊な**外部アカウント**です。

利子アカウントと内部アカウントの間で取引が発生すると、TataruBookはその内部アカウントに利子所得が発生したと見なし、関連する**金利**を計算します。計算時には、TataruBookはその内部アカウントの1日平均残高を利率の計算基準（分母）と見なします。詳細については、[interest_rates]({{ site.baseurl }}/tables_and_views_jp.html#interest_rates)ビューを参照してください。

金利データを正確に保持するため、ファンドや株式の配当は利子アカウントに記入すべきではありません（価格が常に$$ 1 $$で、配当がシェアの増加として反映される通貨基金は例外です）。これらの配当はファンドや株式が存在する内部アカウントに直接に支払われるのではなく、別の内部アカウントに現金で支払われます。ファンドや株式の配当や分割の記録方法についでは、[return_on_shares]({{ site.baseurl }}/tables_and_views_jp.html#return_on_shares)ビューの例を参照してください。

**フィールド**
- `account_index`（整数）：アカウントのインデックスです。空欄にはできません。[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルに存在する資産のインデックスである必要があります。

**制約**
- すべての利子アカウントは外部アカウントでなければなりません。つまり、[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`is_external`字フィールドの値が`1`である必要があります。（[check_interest_account]({{ site.baseurl }}/tables_and_views_jp.html#check_interest_account)ビューでチェックされます）

## postings

取引詳細のリストです。[容易化された複式簿記]({{ site.baseurl }}/tables_and_views_jp.html#容易化された複式簿記)の会計方法に基づき、各取引はアカウント間の資産の移転と見なされます。そのため、このリストの各取引詳細には**元のアカウント**と**目的アカウント**が含まれ、元のアカウントの残高が減少し、目的アカウントの残高が増加します。

元のアカウントと目的アカウントに同じ資産が含まれている場合、目的アカウントの変動額は元のアカウントの変動額の反数になり、両者の合計は$$ 0 $$になります。この場合、元のアカウントの変動額を入力するだけで、目的アカウントの変動額が自動的に計算されます。元のアカウントと目的アカウントが異なる資産を含んでいる場合、[posting_extras]({{ site.baseurl }}/tables_and_views_jp.html#posting_extras)テーブルと併用して、その取引における目的アカウントの変動額を記録する必要があります。

**フィールド**
- `posting_index`（整数）：自動的に生成されるインデックスです。入力する必要がありません。通常、後から入力されたレコードのインデックスは、先に入力されたものより大きくなります。
- `trade_date`（文字列）：取引日です。空欄にはできません。ISO 8601形式（yyyy-mm-dd）に準拠して、同日に発生した取引の順序は`posting_index`によって決定され、小さいインデックスが先に、大きいインデックスが後ろに表示されます。
- `src_account`（整数）：元のアカウントのインデックスです。空欄にはできません。[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルに存在する資産のインデックスである必要があります。
- `src_change`（浮動小数点数）：元のアカウントの変動額。空欄にはできません。値は$$ 0 $$以下でなければなりません。
- `dst_account`（整数）：目标アカウントのインデックスです。空欄にはできません。[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルに存在する資産のインデックスである必要があります。
- `comment`（文字列）：取引に関するコメントです。空欄にはできます。ビューに表示用で、計算には影響しません。

**制約**
- 同じレコード内で、`src_account`の値を`dst_account`と等しくすることはできません。（[check_same_account]({{ site.baseurl }}/tables_and_views_jp.html#check_same_account)ビューでチェックされます）
- 同じレコード内で、元のアカウントと目的アカウントが両方とも外部アカウントであることはできません。 （[check_both_external]({{ site.baseurl }}/tables_and_views_jp.html#check_both_external)ビューでチェックされます）（v1.1 の新機能）
- 同じレコード内で、元のアカウントまたは目的アカウントが外部アカウントである場合、その外部アカウントには標準資産が含まれるか、または取引相手のアカウントと同じ資産が含まれている必要があります。（[check_external_asset]({{ site.baseurl }}/tables_and_views_jp.html#check_external_asset)ビューでチェックされます）（v1.1 の新機能）

簿記を初めたばかりのユーザーは、各アカウントに既存の残高をどのようにデータベースファイルにインポートするか戸惑うかもしれません。お進めの方法は、`期首残高`という外部アカウントを作成し、各内部アカウントに対して、その`期首残高から取引記録を追加することです。
{: .notice}

## posting_extras

元のアカウントと目的アカウントに異なる資産が含まれている場合、取引詳細の目的アカウントの変動額です。[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルの関連説明を参照してください。

**フィールド**
- `posting_index`（整数）：取引のインデックスです。空欄にはできません。[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルに存在するインデックスである必要があります。
- `dst_change`（浮動小数点数）：目的アカウントの変動額です。空欄にはできません。値は$$ 0 $$以上でなければなりません。

**制約**
- 元のアカウントと目的アカウントに同じ資産が含まれている場合、取引詳細には`posting_extras`レコードを含めることはできません。この場合、目的アカウントの変動額は元のアカウントの変動額の反数になります。（[check_same_asset]({{ site.baseurl }}/tables_and_views_jp.html#check_same_asset)ビューでチェックされます）
- 元のアカウントと目的アカウントに異なる資産が含まれている場合、取引詳細には、指定された目的アカウントの変動額を`posting_extras`に記録する必要があります。 （[check_diff_asset]({{ site.baseurl }}/tables_and_views_jp.html#check_diff_asset)ビューでチェックされます）

## prices

資産の単位価格です。必要に応じて標準資産以外のものを[標準資産]({{ site.baseurl }}/tables_and_views_jp.html#standard_asset)（自国通貨）に換算するために使用されます。1日に1つのpricesレコードしか資産には存在できません。このレコードは、その日の終了時の価格を示します。1日中に価格が変動する資産（たとえば、株式）の場合、この値はその日の終値を意味します。
そのため、特定の日の取引で売買された資産の実際の取引価格（リアルタイム価格）は、その日の`prices`テーブルに記録された資産の価格（終値）一致しないことがあります。（[start_stats]({{ site.baseurl }}/tables_and_views_jp.html#start_stats)ビューの例を参照してください）

**フィールド**
- `price_date`（文字列）：日付です。空欄にはできません。ISO 8601形式（yyyy-mm-dd）に準拠しています。
- `asset_index`（整数）：資産のインデックスです。空欄にはできません，[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルに存在する資産インデックスである必要があります。
- `price`（浮動小数点数）：単位価格です (資産が標準資産に対してどれだけの価値があるかを示します)。空欄にはできません。

**制約**
- テーブル内に標準資産のレコードを設定できません。（[check_standard_prices]({{ site.baseurl }}/tables_and_views_jp.html#check_standard_prices)ビューでチェックされます）
- 同じ資産に対して、１日に1つのpricesレコードのみを持つことができます。つまり、2つのレコードにおいて`price_date`と`asset_index`が同じであることは許されません。
- すべての標準資産以外の資産には、[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)と[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)に対応する単位価格のレコードが存在する必要があります。（[check_absent_price]({{ site.baseurl }}/tables_and_views_jp.html#check_absent_price)ビューでチェックされます）
- 標準資産以外の資産を含む２つのアカウント間で取引が発生した場合、これが内部アカウントであっても外部アカウントであっても、取引当日に資産には単位価格のレコードが存在する必要があります。たとえば、香港ドルが標準資産でない場合、香港ドルを使用して香港の株を購入する際には、取引当日に香港ドルと株式の両方に対してpricesレコードが存在し、それらが標準資産に換算された価格であることが求められます。これは、２つのアカウントのROIを計算する際に、取引当日に資金が流入・流出した時点の価格で計算される必要があるためです。（[check_absent_price]({{ site.baseurl }}/tables_and_views_jp.html#check_absent_price)ビューでチェックされます）

## start_date

統計期間の開始日です。一部のビューでは統計期間の起点となります。統計期間は開始日の終了時を起点とするため、開始日の取引は統計に含まれません。そのため注意がひつようです。たとえば、2023年全体の財務データを統計的に分析する場合、`start_date`は`2022-12-31`、`end_date`は`2023-12-31`に設定する必要があります。

**フィールド**
- `val`（文字列）：开始日期，空欄にはできません。ISO 8601形式（yyyy-mm-dd）に準拠しています。

**制約**
- このテーブルには1つのレコードしか許可されません。
- 開始日は終了日よりも前でなければなりません。

## end_date

統計期間の終了日です。一部のビューでは統計期間の終点となります。終了日の取引は統計データに含まれません。そのため注意がひつようです。たとえば、2023年全体の財務データを統計的に分析する場合、`start_date`は`2022-12-31`、`end_date`は`2023-12-31`に設定する必要があります。

**フィールド**
- `val`（文字列）：終了日です。空欄にはできません。ISO 8601形式（yyyy-mm-dd）に準拠しています。

**制約**
- このテーブルには1つのレコードしか許可されません。
- 終了日は開始日より後でなければなりません。

# ビュー

## single_entries

このビューは、他のビューの中間計算結果を表示します。通常、このビューに注意を払う必要はありません。
{: .notice}

入力された複式簿記の取引記録を単式簿記に変換して表示します。このビューでは、[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルの各取引が2つの記録に分割されて表示されます。

**フィールド**
- `posting_index`：[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルの`posting_index`から取得されます。
- `trade_date`：[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルの`trade_date`から取得されます。
- `account_index`：[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルの`src_account`または`dst_account`から取得されます。
- `amount`：`account_index`に対応する取引の変動額で、[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルの`src_change`(またはその反数) 、または[posting_extras]({{ site.baseurl }}/tables_and_views_jp.html#posting_extras)テーブルの`dst_change`から取得されます。
- `target`：取引の相手方アカウントで、[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルの`src_account`または`dst_account`から取得されます。
- `comment`：[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルの`comment`から取得されます。

## statements

入力された複式簿記の取引記録を単式簿記に変換し、アカウントの関連情報とともに表示されます。

**フィールド**
- [single_entries]({{ site.baseurl }}/tables_and_views_jp.html#single_entries)ビューのすべてのフィールドに加え、以下のフィールドが含まれます。
- `src_name`、`target_name`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_name`から取得されます。
- `asset_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`asset_index`から取得されます。
- `is_external`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`is_external`から取得されます。
- `balance`：この取引後のアカウントの残高（これまでのすべての取引記録から取得されます）。外部アカウントの場合、残高の反数は、該当するタイプの収入/支出の累計を示します。

**例**

既存のテーブルの内容が次のとおりであると仮定します。

`asset_types`

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
| 1 | Gil | 0 |
| 2 | ガーロンド・アイアンワークス社の株 | 0 |

`standard_asset`

| asset_index |
|:-:|
| 1 |

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | シャーレアン銀行普通預金 | 1 | 0 |
| 2 | モーグリ証券_ガーロンドの株 | 2 | 0 |
| 3 | 飲食費用 | 1 | 1 |
| 4 | 給料 | 1 | 1 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2023-01-06 | 4 | -50000.0 | 1 | 給料をもらう |
| 2 | 2023-01-07 | 1 | -67.5 | 3 | ラストスタンドの夕食 |
| 3 | 2023-01-09 | 1 | -13000.0 | 2 | ガーロンドの株を買う |

`posting_extras`

| posting_index | dst_change |
|:-:|:-:|
| 3 | 260.0 |

`statements`ビューの内容は次のようになります。

| posting_index | trade_date | account_index | amount | target | comment | src_name | asset_index | is_external | target_name | balance |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2023-01-06 | 1 | 50000.0 | 4 | 給料をもらう | シャーレアン銀行普通預金 | 1 | 0 | 給料 | 50000.0 |
| 1 | 2023-01-06 | 4 | -50000.0 | 1 | 給料をもらう | 給料 | 1 | 1 | シャーレアン銀行普通預金 | -50000.0 |
| 2 | 2023-01-07 | 1 | -67.5 | 3 | ラストスタンドの夕食 | シャーレアン銀行普通預金 | 1 | 0 | 飲食費用 | 49932.5 |
| 2 | 2023-01-07 | 3 | 67.5 | 1 | ラストスタンドの夕食 | 飲食費用 | 1 | 1 | シャーレアン銀行普通預金 | 67.5 |
| 3 | 2023-01-09 | 1 | -13000.0 | 2 | ガーロンドの株を買う | シャーレアン銀行普通預金 | 1 | 0 | モーグリ証券_ガーロンドの株 | 36932.5 |
| 3 | 2023-01-09 | 2 | 260.0 | 1 | ガーロンドの株を買う | モーグリ証券_ガーロンドの株 | 2 | 0 | シャーレアン銀行普通預金 | 260.0 |

注: `statements`ビューは、通常使用される単式簿記の明細書に似ています。特定のアカウントの取引記録のみを確認する場合は、他のソフトウェアでデータベースファイルを開き、`account_index`または`src_name`でフィルタリングできます。たとえば、レコードを`account_index`が`1`のレコードを選別すると、シャーレアン銀行普通預金のすべての取引明細と残高の変動を確認できます。

## start_balance

このビューは、他のビューの中間計算結果を表示します。通常、このビューに注意を払う必要はありません。
{: .notice}

[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)の終了時点で、残高が$$ 0 $$でない全ての内部アカウントの残高が含まれます。

**フィールド**
- `date_val`：[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)テーブルの`val`から取得されます。
- `account_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_index`から取得されます。
- `account_name`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_name`から取得されます。
- `balance`：`start_date`の日またはその前に、`account_name`のアカウントに関連するすべての取引記録の変動額を累積して得られた残高です。
- `asset_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`asset_index`から取得されます。

## start_values

このビューは、他のビューの中間計算結果を表示します。通常、このビューに注意を払う必要はありません。
{: .notice}

[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)の終了時点で、残高が$$ 0 $$でない全ての内部アカウントの残高と、当日の単位価格に基づいて[標準資産]({{ site.baseurl }}/tables_and_views_jp.html#standard_asset)に換算された市場価値を含んでいます。

**フィールド**
- [start_balance]({{ site.baseurl }}/tables_and_views_jp.html#start_balance)ビューのすべてのフィールドに加え、次のフィールドが含まれます。
- `price`：[prices]({{ site.baseurl }}/tables_and_views_jp.html#prices)テーブルの`price`から取得されます。標準資産である場合、数値は$$ 1 $$です。
- `market_value`：$$ \text{price} \times \text{balance} $$で計算された市場価値です。

## start_stats

[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)の終了時点で、残高が$$ 0 $$でない全ての内部アカウントの残高と、当日の単位価格に基づいて[標準資産]({{ site.baseurl }}/tables_and_views_jp.html#standard_asset)に換算された市場価値、および各アカウントの市場価値がその加算に占める割合を含んでいます。

**フィールド**
- [start_values]({{ site.baseurl }}/tables_and_views_jp.html#start_values)ビューのすべてのフィールドに加え、次のフィールドが含まれます。
- `asset_order`：[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルの`asset_order`から取得されます。
- `asset_name`：[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルの`asset_name`から取得されます。
- `proportion`：このアカウントの市場価値を、すべてのアカウントの市場価値の加算に占める割合です。

**例**

[statements]({{ site.baseurl }}/tables_and_views_jp.html#statements)ビューに、既存のテーブルのほかに、以下のようなテーブルを追加すると仮定します。

`start_date`

| val |
|:-:|
| 2023-1-9 |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2023-1-9 | 2 | 51 |

`start_stats`start_statsビューの内容は次のようになります。

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-01-09 | 1 | シャーレアン銀行普通預金 | 36932.5 | 1 | Gil | 1.0 | 36932.5 | 0.7358 |
| 0 | 2023-01-09 | 2 | モーグリ証券_ガーロンドの株 | 260.0 | 2 | ガーロンド・アイアンワークス社の株 | 51.0 | 13260.0 | 0.2642 |

注: `balance`列の値は`statements`ビューでのその日付の各アカウントの残高と一致します。外部アカウントは 在`start_stats`ビューには表示されません。
`postings`テーブルにガーロンド・アイアンワークス社の株の取引記録から換算すると、その時点での取引では $$ 13000 \div 260 = 50 $$の価格で行われたことが分かります。しかし、`prices`テーブルに`2023-1-9`の単位価格（終値）のレコードは$$ 51 $$あり、その値から資産の市場価値（`market_value`の値）が計算されました。本例は、リアルタイムの取引価格が終値と異なる場合があることを示しています。

## start_assets

[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)の終了時点で、各資産の数量と、当日の単位価格に基づいて[標準資産]({{ site.baseurl }}/tables_and_views_jp.html#standard_asset)に換算された市場価値、および各資産の市場価値がその加算に占める割合を含んでいます。

**フィールド**
- `asset_order`：[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルの`asset_order`から取得されます。
- `date_val`：[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)テーブルの`val`から取得されます。
- `asset_index`：[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルの`asset_index`から取得されます。
- `asset_name`：[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルの`asset_name`から取得されます。
- `amount`：この資産を含むすべてのアカウントの残高を累積して計算された資産の数量です。
- `price`：[prices]({{ site.baseurl }}/tables_and_views_jp.html#prices)テーブルの`price`から取得されます。標準資産である場合、数値は$$ 1 $$です。
- `total_value`：$$ \text{price} \times \text{amount} $$で計算された市場価値です。
- `proportion`：この資産の市場価値を、すべての資産の市場価値の加算に占める割合です。

## diffs

このビューは、他のビューの中間計算結果を表示します。通常、このビューに注意を払う必要はありません。
{: .notice}

各アカウントにおける[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)と[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)の間の変動額を合計します。`start_date`の取引を计算されませんが、`end_date`の取引を计算されます。

**フィールド**
- `account_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_index`から取得されます。
- `account_name`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_name`から取得されます。
- `amount`：`start_date`から`end_date`までのすべての取引記録における変動額を合計して得られた数値です。
- `asset_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`asset_index`から取得されます。

## comparison

このビューは、他のビューの中間計算結果を表示します。通常、このビューに注意を払う必要はありません。
{: .notice}

[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)と[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)の終了時の各アカウントの残高と、両日付間での変動額を含んでいます。

**フィールド**
- [diffs]({{ site.baseurl }}/tables_and_views_jp.html#diffs)ビューの`account_index`、`account_name`、`asset_index`に加え、次のフィールドが含まれます。
- `start_amount`：[start_balance]({{ site.baseurl }}/tables_and_views_jp.html#start_balance)ビューの`balance`から取得されます。
- `diff`：[diffs]({{ site.baseurl }}/tables_and_views_jp.html#diffs)ビューの`amount`から取得されます。または、統計期間内のアカウント残高が変更されていない場合、数値は$$ 0 $$です。
- `end_amount`：$$ \text{start_amount} + \text{diff} $$で計算された期末残高です。

## end_values

このビューは、他のビューの中間計算結果を表示します。通常、このビューに注意を払う必要はありません。
{: .notice}

[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)の終了時点で、残高が$$ 0 $$でない全ての内部アカウントの残高と、当日の単位価格に基づいて[標準資産]({{ site.baseurl }}/tables_and_views_jp.html#standard_asset)に換算された市場価値を含んでいます。

**フィールド**
- すべてのフィールドは[start_values]({{ site.baseurl }}/tables_and_views_jp.html#start_values)ビューと同じですが、統計時点は[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)の終了時になります。

## end_stats

[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)の終了時点で、残高が$$ 0 $$でない全ての内部アカウントの残高と、当日の単位価格に基づいて[標準資産]({{ site.baseurl }}/tables_and_views_jp.html#standard_asset)に換算された市場価値、および各アカウントの市場価値がその加算に占める割合を含んでいます。

注：[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)テーブルと[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)テーブルにそれぞれ１つのレコードが必要です。これにより、`end_stats`ビューに正確な内容を表示させることができます。
{: .notice--warning}

**フィールド**
- [start_stats]({{ site.baseurl }}/tables_and_views_jp.html#start_stats)ビューと同じですが、統計時点は[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)になります。

**例**

[statements]({{ site.baseurl }}/tables_and_views_jp.html#statements)ビューに、既存のテーブルのほかに、以下のようなテーブルを追加すると仮定します。

`start_date`

| val |
|:-:|
| 2023-1-5 |

`end_date`

| val |
|:-:|
| 2023-1-9 |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2023-1-9 | 2 | 51 |

`end_stats`ビューの内容は次のようになります。

| asset_order | date_val | account_index | account_name | balance | asset_index | asset_name | price | market_value | proportion |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2023-01-09 | 1 | シャーレアン銀行普通預金 | 36932.5 | 1 | Gil | 1.0 | 36932.5 | 0.7358 |
| 0 | 2023-01-09 | 2 | モーグリ証券_ガーロンドの株 | 260.0 | 2 | ガーロンド・アイアンワークス社の株 | 51.0 | 13260.0 | 0.2642 |

注: `end_stats`ビューの内容は[start_stats]({{ site.baseurl }}/tables_and_views_jp.html#start_stats)ビューとほぼ同じですが、唯一の違いは、統計時点は`end_date`であることです。

## end_assets

[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)の終了時における各資産の数量、当日の単位価格に基づいて[標準資産]({{ site.baseurl }}/tables_and_views_jp.html#standard_asset)市場価値、および各資産の市場価値がその加算に占める割合を含んでいます。

注意：[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)テーブルと[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)テーブルにそれぞれ１つのレコードが必要です。これにより、`end_assets`ビューに正確な内容を表示させることができます。
{: .notice--warning}

**フィールド**
- [start_assets]({{ site.baseurl }}/tables_and_views_jp.html#start_assets)ビューと同じですが、統計時点は[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)になります。

## external_flows

このビューは、他のビューの中間計算結果を表示します。通常、このビューに注意を払う必要はありません。
{: .notice}

各**外部アカウント**における[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)から[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)までの取引と、取引日の対応する資産の単位価格を含んでいます。`start_date`の取引を计算されませんが、`end_date`の取引を计算されます。利子アカウント以外の各外部アカウントは、特定の収支カテゴリを表すことに注意してください。

ビューのタイトルの意味は**外部のキャッシュフロー**を意味しますが、[收益率计算方法]({{ site.baseurl }}/rate_of_return_jp.html)での定義とは異なり、このビューには利子アカウントも外部キャッシュフローの起点と見なします。

**フィールド**
- `trade_date`：[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルの`trade_date`から取得されます。
- `asset_order`：[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルの`asset_order`から取得されます。
- `account_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_index`から取得されます。
- `account_name`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_name`から取得されます。
- `amount`：[single_entries]({{ site.baseurl }}/tables_and_views_jp.html#single_entries)テーブルの`amount`から取得されます。
- `asset_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`asset_index`から取得されます。
- `asset_name`：[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルの`asset_name`から取得されます。
- `price`：[prices]({{ site.baseurl }}/tables_and_views_jp.html#prices)テーブルの`price`から取得されます。標準資産である場合、数値は$$1$$です。

## income_and_expenses

各**外部アカウント**における、[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)から[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)までの取引の変動額の統計と、それに基づいて換算された市場価値を含んでいます。`start_date`の取引を计算されませんが、`end_date`の取引を计算されます。注：利子アカウント以外の外部アカウントは、特定の収支カテゴリを表すため、このビューは統計期間の収入、支出、利子を分類して統計する役割を果たします。

**フィールド**
- [external_flows]({{ site.baseurl }}/tables_and_views_jp.html#external_flows)ビューの`asset_order`、`account_index`、`account_name`、`asset_index`、`asset_name`フィールドのほか、次のフィールドが含まれます。
- `total_amount`：`start_date`から`end_date`までの特定の外部アカウントのすべての取引記録の変動額を累積した合計値（標準資産に換算されていない金額）です。
- `total_value`：各取引の変動額をその日の单位価格で標準資産に換算し、累積して得られた市場価値の合計です。外部アカウントに$$ n $$件の取引があり、各取引の変動額がそれぞれ$$ a_1 \dots a_n $$、各取引当日の資産の单位価格がそれぞれ$$ p_1 \dots p_n $$であると仮定した場合、その合計値は$$ \displaystyle\sum_{i=1}^{n} p_ia_i $$となります。

**例**

既存のテーブルの内容が次のとおりであると仮定します。

`asset_types`

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
| 1 | ギル | 0 |
| 2 | MGP | 0 |

`standard_asset`

| asset_index |
|:-:|
| 1 |

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | シャーレアン銀行普通預金 | 1 | 0 |
| 2 | MGPアカウント | 2 | 0 |
| 3 | 給料 | 1 | 1 |
| 4 | MGP支出 | 2 | 1 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2023-02-06 | 3 | -50000.0 | 1 | 給料をもらう |
| 2 | 2023-02-07 | 1 | -30000.0 | 2 | MGPの購入 |
| 3 | 2023-02-12 | 2 | -30.0 | 4 | ゲームエンターテインメント |
| 4 | 2023-02-15 | 2 | -100.0 | 4 | アクセサリーの購入 |

`posting_extras`

| posting_index | dst_change |
|:-:|:-:|
| 2 | 300.0 |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2023-02-12 | 2 | 90.0 |
| 2023-02-15 | 2 | 110.0 |

`income_and_expenses`ビューの内容は次のようになります。

| asset_order | account_index | account_name | total_amount | asset_index | asset_name | total_value |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 3 | 給料 | -50000.0 | 1 | Gil | -50000.0 |
| 0 | 4 | MGP支出 | 130.0 | 2 | MGP | 13700.0 |

注: 外部アカウントの変動額は、内部アカウントの変動額の反数に等しいことに注意してください。たとえば、`給料`アカウントの`total_amount`が$$ -50000.0 $$である場合、内部アカウントで受け取った給料は合計$$ 50000.0 $$になります。

`ギル`などの標準資産を含む外部アカウントの場合、合計した市場価値は変動額の合計値と等しくなります。ただし、外部アカウントに非標準資産 (`MGP`など) が含まれている場合、変動額は取引当日の单位価格で標準資産に換算されてから累積されます。本例では、`MGP支出`の`total_value`は$$ 30 \times 90 + 100 \times 110 = 13700 $$で計算されます。

## portfolio_stats

レコードは1つだけ存在し、すべての内部アカウントを**ポートフォリオ**として扱い、統計期間の開始日と終了日のポートフォリオの総市場価値と、期間中の収支の合計、および投資収益を表示します。

**フィールド**
- `start_value`：統計期間の開始日における資産の総市場価値です。[start_values]({{ site.baseurl }}/tables_and_views_jp.html#start_values)ビューの`market_value`を合計して取得されます。
- `end_value`：統計期間の終了日における資産の総市場価値です。[end_values]({{ site.baseurl }}/tables_and_views_jp.html#end_values)ビューの`market_value`を合計して取得されます。
- `net_outflow`：統計期間の資産の流出額です。[income_and_expenses]({{ site.baseurl }}/tables_and_views_jp.html#income_and_expenses)ビューにおける[利子账户]({{ site.baseurl }}/tables_and_views_jp.html#interest_accounts)以外のすべての外部アカウントの`total_value`を合計して取得されます。利子は資金の流入でも流出でもないことに注意してください。統計期間中の資金の流入が流出を上回る場合、net_outflowは負の値になります。
- `interest`：統計期間中に発生した利子収益の合計額です。[income_and_expenses]({{ site.baseurl }}/tables_and_views_jp.html#income_and_expenses)ビューの[利子账户]({{ site.baseurl }}/tables_and_views_jp.html#interest_accounts)の`total_value`を合計して取得されます
- `net_gain`：統計期間中に投資から得られた総利益（または総損失）です。$$ \text{end_value} + \text{net_outflow} - \text{start_value} $$で計算されます。これは、収支による資産の変動を除外し、すべての資産変動は投資収益（または損失）と見なされます。利子収益は投資収益の一部です。
- `rate_of_return`：[ディーツ簡便法]({{ site.baseurl }}/rate_of_return_jp.html#ディーツ簡便法)を使用して計算された投資収益率です。

## flow_stats

各内部アカウントにおける、[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)から[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)まで**外部アカウント**との取引による累計変化額を示します。`start_date`の取引を计算されませんが、`end_date`の取引を计算されます。利子アカウント以外の外部アカウントは特定の収支カテゴリを表すため、このビューは統計期間中に各内部アカウントでの収入、支出、利子を分類し、集計する役割を果たします。

[income_and_expenses]({{ site.baseurl }}/tables_and_views_jp.html#income_and_expenses)ビューと比べて、次の2つの違いがあります。
1. `flow_stats`では、異なる内部アカウントは個別に集計されますが、`income_and_expenses`では、同じ外部アカウントとの異なる内部アカウントの取引額が合算されます。
1. `flow_stats`では、資産の変動額を累計した値のみが表示されますが、`income_and_expenses`では、資産の単位価格に基づいて標準資産に換算されています。

**フィールド**
- `flow_index`：外部アカウントのインデックスです。[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_index`から取得されます
- `flow_name`：外部アカウントのタイトルです。[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_name`から取得されます
- `account_index`：内部アカウントのインデックスです。[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_index`から取得されます
- `account_name`：内部アカウントのタイトルです。[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_name`から取得されます
- `amount`：この内部アカウントにおける、`start_date`から`end_date`まで外部アカウントとの取引による累計変化額です(標準資産に変換されていない金額) 。

**例**

[income_and_expenses]({{ site.baseurl }}/tables_and_views_jp.html#income_and_expenses) ビューの例の既存のテーブルに基づいて、次の２つのテーブルにレコードが追加されると仮定します。

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 5 | シャーレヤンの年金 | 1 | 0 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 5 | 2023-02-06 | 3 | -10000.0 | 5 | 給料と一緒にもらった年金 |

`flow_stats`ビューの内容は次のようになります。

| flow_index | flow_name | account_index | account_name | amount |
|:-:|:-:|:-:|:-:|:-:|
| 3 | 給料 | 1 | シャーレアン銀行普通預金 | -50000.0 |
| 3 | 給料 | 5 | シャーレヤンの年金 | -10000.0 |
| 4 | MGP支出 | 2 | MGPアカウント | 130.0 |

注: 異なる内部アカウントで`給料`が個別に集計されますが、`income_and_expenses`ビューでは`給料`に関するレコードが１つだけ表示されます (すべての内部アカウントから合算されます)。さらに、`MGP支出`の金額は標準資産の`ギル`に換算されず、`MGP`の数量として集計されます。

## share_trades

このビューは、他のビューの中間計算結果を表示します。通常、このビューに注意を払う必要はありません。
{: .notice}

非標準資産を含むすべての内部アカウントにおける、[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)から[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)までの取引の変化額が標準資産に換算された市場価値です。このデータは、非標準資産の収益率を計算するために使用されます。

非標準資産を株式と見なすと、このビューは各株式取引における購入価格や売却収入を表します。

**フィールド**
- [single_entries]({{ site.baseurl }}/tables_and_views_jp.html#single_entries)ビューの ビューのすべてのフィールドに加え、次のフィールドが含まれます。
- `account_name`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_name`から取得されます。
- `asset_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`asset_index`から取得されます。
- `asset_name`：[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルの`asset_name`から取得されます。
- `asset_order`：[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルの`asset_order`から取得されます。
- `cash_flow`：この内部アカウントに含まれる非標準資産は、その日の単位価格で標準資産に換算された市場価値です。

## share_stats

このビューは、他のビューの中間計算結果を表示します。通常、このビューに注意を払う必要はありません。
{: .notice}

非標準資産を含むすべての内部アカウントにおける、[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)から[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)まで、残高が$$ 0 $$ではない場合、取引に必要な最小初期資金と、その期間中に内部アカウントに含まれる資産の(標準資産に換算された)市場価値の増加額を示します。このビューのデータを理解するには、[最小初期資金法]({{ site.baseurl }}/rate_of_return_jp.html#最小初期資金法)を参照してください。

**フィールド**
- `asset_order`：[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルの`asset_order`から取得されます。
- `asset_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`asset_index`から取得されます。
- `asset_name`：[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルの`asset_name`から取得されます。
- `account_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_index`から取得されます。
- `account_name`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_name`から取得されます。
- `min_inflow`：統計期間中にこのアカウントに残高が$$ 0 $$ではない場合、必要な最小初期資金です。
- `cash_gained`：内部アカウントに含まれる資産の(標準資産に換算された)市場価値の増加額です。

## return_on_shares

非標準資産を含むすべての内部アカウントにおける、[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)から[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)までの、標準資産として計算された市場価値に基づく投資収益率です。`start_date`の取引を计算されませんが、`end_date`の取引を计算されます。投資収益率は、[最小初期資金法]({{ site.baseurl }}/rate_of_return_jp.html#最小初期資金法)を使用して計算されます。

**フィールド**
- `asset_order`：[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルの`asset_order`から取得されます。
- `asset_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`asset_index`から取得されます。
- `asset_name`：[asset_types]({{ site.baseurl }}/tables_and_views_jp.html#asset_types)テーブルの`asset_name`から取得されます。
- `account_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_index`から取得されます。
- `account_name`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_name`から取得されます。
- `start_amount`：統計期間の開始日の残高です。[comparison]({{ site.baseurl }}/tables_and_views_jp.html#comparison)ビューの`start_amount`から取得されます。
- `start_value`： 統計期間の開始日の市場価値です。[start_values]({{ site.baseurl }}/tables_and_views_jp.html#start_values)ビューの`market_value`取得され、またはこのアカウントが`start_values`に存在しない場合は$$ 0 $$になります。
- `diff`：統計期間中の変動額です。[comparison]({{ site.baseurl }}/tables_and_views_jp.html#comparison)ビューの`diff`から取得されます。
- `end_amount`：統計期間の終了日の残高です。[comparison]({{ site.baseurl }}/tables_and_views_jp.html#comparison)ビューの`end_amount`から取得されます。
- `end_value`：統計期間の終了日の市場価値です。[end_values]({{ site.baseurl }}/tables_and_views_jp.html#end_values)ビューの`market_value`取得され、またはこのアカウントが`end_values`に存在しない場合は$$ 0 $$になります。
- `cash_gained`：このアカウントに含まれる資産の市場価値の増加額です。[share_stats]({{ site.baseurl }}/tables_and_views_jp.html#share_stats)ビューの`cash_gained`から取得され、またはこのアカウントが`share_stats`に存在しない場合は$$ 0 $$になります。
- `min_inflow`： 最小初期資金です。[share_stats]({{ site.baseurl }}/tables_and_views_jp.html#share_stats)ビューの`min_inflow`から取得され、またはこのアカウントが`share_stats`に存在しない場合は$$ 0 $$になります。
- `profit`：このアカウントへの投資による収益率（または損失率）です。$$ \text{cash_gained} + \text{end_value} - \text{start_value} $$で計算されます。
- `rate_of_return`：使用[最小初期資金法]({{ site.baseurl }}/rate_of_return_jp.html#最小初期資金法)使用して計算された、このアカウントの投資収益率です。

**例1**

既存のテーブルの内容が次のとおりであると仮定します。

`asset_types`

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
| 1 | Gil | 0 |
| 2 | ガーロンド・アイアンワークス社の株 | 0 |

`standard_asset`

| asset_index |
|:-:|
| 1 |

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | シャーレアン銀行普通預金 | 1 | 0 |
| 2 | モーグリ証券_ガーロンドの株 | 2 | 0 |
| 3 | ギルの期首残高 | 1 | 1 |
| 4 | ガーロンド・アイアンワークス株の期首残高 | 2 | 1 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2022-12-31 | 3 | -10000.0 | 1 | ギルの期首残高 |
| 2 | 2022-12-31 | 4 | -10.0 | 2 | 株の期首残高 |
| 3 | 2023-02-08 | 1 | -60.0 | 2 | 株を買う |
| 4 | 2023-03-08 | 2 | -6.0 | 1 | 株式を売る |

`posting_extras`

| posting_index | dst_change |
|:-:|:-:|
| 3 | 5.0 |
| 4 | 90.0 |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2022-12-31 | 2 | 10.0 |
| 2023-06-30 | 2 | 11.0 |

`start_date`

| val |
|:-:|
| 2022-12-31 |

`end_date`

| val |
|:-:|
| 2023-06-30 |

`return_on_shares`ビューの内容は次のようになります。

| asset_order | asset_index | asset_name | account_index | account_name | start_amount | start_value | diff | end_amount | end_value | cash_gained | min_inflow | profit | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2 | ガーロンド・アイアンワークス社の株 | 2 | モーグリ証券_ガーロンドの株 | 10.0 | 100.0 | -1.0 | 9.0 | 99.0 | 30.0 | 60.0 | 29.0 | 0.18125 |

注：資金の流入と流出の間隔が異なる点を除いて、本例は[最小初期資金法]({{ site.baseurl }}/rate_of_return_jp.html#最小初期資金法)の**例1**と非常に似ているため、得られる収益率も同じになります。`prices`テーブルには、統計期間の開始日と終了日の単位価格のみを提供すればよく、各取引時の単位価格は提供しなくてもいいです。これは、取引自体がすでに価格情報を反映しているためです。

**例2**

既存のテーブルの内容が次のとおりであると仮定します。

`asset_types`

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
| 1 | Gil | 0 |
| 2 | MGP | 0 |

`standard_asset`

| asset_index |
|:-:|
| 1 |

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | MGPアカウント | 2 | 0 |
| 2 | MGPの期首残高 | 2 | 1 |
| 3 | MGPの利子 | 2 | 1 |

`interest_accounts`

| account_index |
|:-:|
| 3 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2022-12-31 | 2 | -1000.0 | 1 | MGPの期首残高 |
| 2 | 2023-06-21 | 3 | -10.0 | 1 | 利子 |

`prices`

| price_date | asset_index | price |
|:-:|:-:|:-:|
| 2022-12-31 | 2 | 10.0 |
| 2023-06-21 | 2 | 11.0 |
| 2023-06-30 | 2 | 12.0 |

`start_date`

| val |
|:-:|
| 2022-12-31 |

`end_date`

| val |
|:-:|
| 2023-06-30 |

`return_on_shares`ビューの内容は次のようになります。

| asset_order | asset_index | asset_name | account_index | account_name | start_amount | start_value | diff | end_amount | end_value | cash_gained | min_inflow | profit | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 2 | MGP | 1 | MGPアカウント | 1000.0 | 10000.0 | 10.0 | 1010.0 | 12120.0 | 0 | 0 | 2120.0 | 0.212 |

注:`MGP`は標準資産ではない同時に、利子収益が発生します。この場合、`return_on_shares`ビューは利子収益を含む全体的な収益を計算します。利子収益は、[interest_rates]({{ site.baseurl }}/tables_and_views_jp.html#interest_rates)ビューで個別に表示されます。`interest_accounts`テーブルに利子アカウントを追加することを忘れないでください。本例では、`interest_accounts`テーブルが欠落していると、結果に大きな差が生じます。

## interest_stats

このビューは、他のビューの中間計算結果を表示します。通常、このビューに注意を払う必要はありません。
{: .notice}

[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)から[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)までの各内部アカウントで得られた利子を含んでいます。

**フィールド**
- `account_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_index`から取得されます。
- `account_name`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_name`から取得されます。
- `asset_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`asset_index`から取得されます。
- `amount`：統計期間中にこのアカウントで得られた利子です（標準資産に換算されていない）。

## interest_rates

利子を含む各内部アカウントで、[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)から[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)までの得られた利子、日次平均残高、および[修正ディーツ法]({{ site.baseurl }}/rate_of_return_jp.html#修正ディーツ法)を使用して計算された**収益率**（ROI）を含んでいます。

このビューで表示される収益率は、利子部分限定された収益率であり、資産の単位価格の変動による収益は含まれていません。

**フィールド**
- `account_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_index`から取得されます。
- `account_name`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`account_name`から取得されます。
- `asset_index`：[accounts]({{ site.baseurl }}/tables_and_views_jp.html#accounts)テーブルの`asset_index`から取得されます。
- `avg_balance`：統計期間中のこのアカウントの平均日次残高です（標準資産に変換されていない）。
- `interest`：[interest_stats]({{ site.baseurl }}/tables_and_views_jp.html#interest_stats)ビューの`amount`から取得されます。
- `rate_of_return`：[修正ディーツ法]({{ site.baseurl }}/rate_of_return_jp.html#修正ディーツ法)を使用して計算された収益率です 。

**例**

既存のテーブルの内容が次のとおりであると仮定します。

`asset_types`

| asset_index | asset_name | asset_order |
|:-:|:-:|:-:|
| 1 | ギル | 0 |

`standard_asset`

| asset_index |
|:-:|
| 1 |

`accounts`

| account_index | account_name | asset_index | is_external |
|:-:|:-:|:-:|:-:|
| 1 | シャーレアン銀行普通預金 | 1 | 0 |
| 2 | 給料 | 1 | 1 |
| 3 | 支出 | 1 | 1 |
| 4 | ギルの利子 | 1 | 1 |

`interest_accounts`

| account_index |
|:-:|
| 4 |

`postings`

| posting_index | trade_date | src_account | src_change | dst_account | comment |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2023-03-31 | 2 | -10000.0 | 1 | 給料をもらう |
| 2 | 2023-09-30 | 1 | -10000.0 | 3 | 大型家具の購入 |
| 3 | 2023-12-21 | 4 | -100.0 | 1 | 利子をもらう |

`start_date`

| val |
|:-:|
| 2022-12-31 |

`end_date`

| val |
|:-:|
| 2023-12-31 |

`interest_rates`ビューの内容は次のようになります。

| account_index | account_name | asset_index | avg_balance | interest | rate_of_return |
|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | シャーレアン銀行普通預金 | 1 | 5016.44 | 100.0 | 0.02 |

注: 収益率の計算方法については、[修正ディーツ法]({{ site.baseurl }}/rate_of_return_jp.html#修正ディーツ法)を参照してください。`interest_rates`テーブルで計算された収益率は、このアカウントに含まれる資産の数量を基準にしており、標準資産に換算されないため、資産の単位価格の変動は収益率に反映されません。資産の単位価格の変動を含む総合的な収益率を確認するには、[return_on_shares]({{ site.baseurl }}/tables_and_views_jp.html#return_on_shares)ビューを参照してください。

## periods_cash_flows

すべての内部アカウントを**ポートフォリオ**として扱い、[start_date]({{ site.baseurl }}/tables_and_views_jp.html#start_date)から[end_date]({{ site.baseurl }}/tables_and_views_jp.html#end_date)までのこのポートフォリオの毎日の資金の純流入/流出を表示します。`start_date`の流入/流出を计算されませんが、`end_date`の流入/流出を计算されます。利子収入は投資収益として扱われるため、流入/流出として计算されません。内部アカウントと、利子アカウント以外の外部アカウント間の取引は、資金流入/流出として计算されます。統計期間の開始日には、当時のポートフォリオの資産は一回の純流入として扱われ、統計期間の終了日には、当時のポートフォリオの資産は一回の純流出として扱われます。

このビューは、[内部收益率（IRR）]({{ site.baseurl }}/rate_of_return_jp.html#内部收益率irr)を計算するために必要なデータを提供します。

**フィールド**
- `trade_date`：資産の流入/流出の日付です。
- `period`：その日は開始日から経過した日数です。
- `cash_flow`：標準資産に換算された、その日の資金の純流入/流出です。通常の定義とは異なり、この入門書における、[内部收益率（IRR）]({{ site.baseurl }}/rate_of_return_jp.html#内部收益率irr)の定義によると、流入時の数値はマイナスであり、流出時の数値はプラスであることに注意してください。

## check_standard_prices

通常、このビューにはレコードがありません。レコードが表示されている場合は、[prices]({{ site.baseurl }}/tables_and_views_jp.html#prices)テーブルに標準資産の単位価格が存在し、制約に違反していることを意味します。

## check_interest_account

通常、このビューにはレコードがありません。レコードが表示されている場合は、[利子アカウント]({{ site.baseurl }}/tables_and_views_jp.html#interest_accounts)が内部アカウントであり、制約に違反していることを意味します。

## check_same_account

通常、このビューにはレコードがありません。レコードが表示されている場合は、[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルに`src_account`と`dst_account`が同一のレコードが含まれており、制約に違反していることを意味します。

## check_both_external

これはv1.1で追加された新しいビューです。
{: .notice}

通常、このビューにはレコードがありません。レコードが表示されている場合は、[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルに`src_account`と`dst_account`の両方が外部アカウントであるレコードが含まれており、制約に違反していることを意味します。

## check_diff_asset

通常、このビューにはレコードがありません。レコードが表示されている場合は、[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルに元のアカウントと目的アカウントが異なる資産を含むレコードが存在しており、[posting_extras]({{ site.baseurl }}/tables_and_views_jp.html#posting_extras)テーブルに対応するレコードがないため、制約に違反していることを意味します。

## check_same_asset

通常、このビューにはレコードがありません。レコードが表示されている場合は、[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルに元のアカウントと目的アカウントが同じ資産を含むレコードが存在しており、[posting_extras]({{ site.baseurl }}/tables_and_views_jp.html#posting_extras)テーブルに対応するレコードがあるため、制約に違反していることを意味します。

## check_external_asset

これは v1.1で追加された新しいビューです。
{: .notice}

通常、このビューにはレコードがありません。レコードが表示されている場合は、[postings]({{ site.baseurl }}/tables_and_views_jp.html#postings)テーブルに、元のアカウントまたは目的アカウントは外部アカウントであるレコードが含まれています。その外部アカウントは標準資産を含まず、取引先のアカウントと同じ資産も含んでいないため、制約に違反していることを意味します。

## check_absent_price

通常、このビューにはレコードがありません。レコードが表示されている場合は、[prices]({{ site.baseurl }}/tables_and_views_jp.html#prices)に特定の日付に必要な資産の単位価格が欠落しており、制約に違反していることを意味します。