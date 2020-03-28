import pandas as pd
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

import os, sys
import math
import json
import glob
import pprint
import pickle
from collections import OrderedDict

def i18n_read_json(json_path):
    '''　i18njsonを順序保持したまま読込。 
    '''
    with open(json_path, 'r', encoding='utf-8') as lj:
        return json.loads(lj.read(), object_pairs_hook=OrderedDict)

def i18n_get_gs(google_spread_sheet_url):
    ''' i18n google spread sheetをdfとして取得。 
    '''    
    return pd.read_csv(google_spread_sheet_url)

def i18n_get_gs_words(json_fname, gs):
    ''' 翻訳spread sheetから対象言語の文言リストを取得。
    '''
    gscolumns = gs.columns.values.tolist()
    if 'ja.json' in json_fname:
        gs_words = gs[gscolumns[0]].values.tolist()
        gs_words.extend(gs[gscolumns[1]].values.tolist()) 
    # elif 'ja_Hira.json' in json_fname:
    #     gs_words = gs[gscolumns[3]].values.tolist()
    elif 'en.json' in json_fname:
        gs_words = gs[gscolumns[3]].values.tolist()
    # elif 'ko.json' in json_fname:
    #     gs_words = gs[gscolumns[3]].values.tolist()
    elif 'zh_CN.json' in json_fname:
        gs_words = gs[gscolumns[4]].values.tolist()
    elif 'zh_TW.json' in json_fname:
        gs_words = gs[gscolumns[5]].values.tolist()
    elif 'vi.json' in json_fname:
        gs_words = gs[gscolumns[6]].values.tolist()        
    return gs_words

def i18n_translated_check(source_json, target_json):
    """ source_jsonにある文章が翻訳されているかチェックし、
        target_jsonに存在しなければログ出力。 
    """
    src_lang = i18n_read_json(source_json)
    target_lang = i18n_read_json(target_json)
    for src_word in src_lang.keys():
        if src_word not in target_lang.keys():
            print(f"{os.path.basename(target_json)} \"{src_word}\" Translation not found.")

def i18n_find_word_from_json(gs, json_path):
    """　spread sheetにあってjsonにない該当言語の文章を探す。
    """        
    print(f'Find google spread sheet words from {json_path}... ')

    json_words = i18n_read_json(json_path)
    json_fname = os.path.basename(json_path)    
    gs_words = i18n_get_gs_words(json_fname, gs)
    for gw in gs_words:
        if gw not in json_words:
            """ TODO spread sheet側文章には「,」がない？"""
            print(f"\"{gw}\" not found in {json_fname}.")

def i18n_find_word_from_gs(json_path, gs):
    """ jsonにあってspread sheetにない文章を探す。    
        新潟県版翻訳が存在しないケースもあるので、ja.jsonの場合は2列から検索。 
    """    
    print(f'Find {json_path} words from spread sheet... ')    
    
    json_words = i18n_read_json(json_path).items()
    json_fname = os.path.basename(json_path)    
    gs_words = i18n_get_gs_words(json_fname, gs)    
    for jw in json_words:
        if jw[1] not in gs_words:
            """ TODO spread sheet側文章には「,」がない？"""
            print(f"{json_fname} \"{jw[1]}\" not found in spread sheet.")

def i18n_json_words_check(resource_files):
    """ localesディレクトリ配下のi18njsonについて、
        各言語で同じリソースがリストされているかチェックする。
    """
    for resource in resource_files:
        if 'ja.json' in resource:
            continue
        i18n_translated_check('./locales/ja.json', resource)

def i18n_diff_json_and_gs(google_spread_sheet_url, json_files):
    """ ローカルのjson,google_spread_sheetのリソース差分(文言有無)を表示する。 
    """
    gs = i18n_get_gs(google_spread_sheet_url)
    for resource in json_files:
        i18n_find_word_from_json(gs, resource)
        i18n_find_word_from_gs(resource, gs)

def i18n_unused_check(vue_root, json_file):
    """ 指定ディレクトリ配下のvueソースから、
        使用されていない文言をリストアップ。
    """
    abspath = os.path.abspath(vue_root)
    vues = glob.glob(abspath+'/**/*.vue', recursive=True)
    
    target_words = i18n_read_json(json_file)
    unused_list = list(target_words.keys())
    for vue in vues:
        ld = open(vue, encoding='utf-8')
        lines = ld.readlines()
        ld.close()        
        for word in unused_list:            
            for line in lines:
                if line.find(word) >= 0:
                    unused_list.pop(unused_list.index(word))
                    break        
    print(unused_list)

def i18n_create_json():
    pass

def i18n_update_spreadsheet():
    pass

def main():
    sheet_url = "https://docs.google.com/spreadsheets/d/1hcU7fT2peAlKNH5Dcp9xufuXH4vf5FGsRKxcF9WC9zc/export?format=csv&gid=17066585"
    # upload_test_url = "https://docs.google.com/spreadsheets/d/14283nuNCBeSNe4M6HSdar_9oVug2p15mkCNLwRrb4JQ/edit#gid=0"
    # upload_test_sheet_id = "14283nuNCBeSNe4M6HSdar_9oVug2p15mkCNLwRrb4JQ"
    resource_files = glob.glob('./locales/*.json')
    
    # ローカルリソース一貫性チェック
    #i18n_json_words_check(resource_files)
    
    # ローカルリソースとgoogle spread sheet差分チェック
    #i18n_diff_json_and_gs(sheet_url, resource_files)
    
    # ローカルのvueソース - json i18nリソースを比較、利用されていないリソース有無のチェック
    i18n_unused_check('/Users/saeki/dev/covid19', 'locales/ja.json')

if __name__ =='__main__':
    main()
