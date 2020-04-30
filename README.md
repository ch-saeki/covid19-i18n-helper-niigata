# covid19-i18n-helper-niigata
新潟県のWebサイトのi18n対応自動化用スクリプトです。

# Requirement
Python3

# Usage
```

# google spread sheetからjson生成
i18n_helper.py createjson

# ローカルリソースとgoogle spread sheetの差分チェック
i18n_helper.py diffjson ./resource_dir

# ローカルリソース一貫性チェック
i18n_helper.py checkjson ./resource_dir

# ローカルのvueソース - json i18nリソースを比較、利用されていないリソース有無のチェック
i18n_helper.py unusedlist ./vue_project_dir ./resource_dir

```    
