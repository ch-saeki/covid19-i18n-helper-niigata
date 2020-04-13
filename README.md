# covid19-i18n-helper-niigata
新潟県のWebサイトのi18n対応自動化用スクリプトです。

# Requirement
Python3

# Usage
```
resource_files = glob.glob('./out_locales/*.json')

# ローカルのvueソース - json i18nリソースを比較、利用されていないリソース有無のチェック
i18n_unused_check('/Users/saeki/dev/covid19', 'locales/ja.json')

# ローカルリソース一貫性チェック
i18n_json_words_check(resource_files)

# ローカルリソースとgoogle spread sheet差分チェック
i18n_diff_json_and_gs(sheet_url, resource_files)

# google spread sheet から各言語リソースjson出力
dst_dir = './out_locales'
i18n_create_json_from_gs(sheet_url, dst_dir)
```    
