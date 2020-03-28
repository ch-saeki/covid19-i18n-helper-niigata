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

GSCOL_ORG = 0
GSCOL_JA = 1
GSCOL_EN = 3
GSCOL_ZH_CN = 4
GSCOL_ZH_TW = 5
GSCOL_VI = 6
GSCOL_NE = 7
GSCOL_RU = 8

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
    gs_original_words = gs[gscolumns[GSCOL_ORG]].values.tolist()
    if 'ja.json' in json_fname:
        gs_words = gs[gscolumns[GSCOL_JA]].values.tolist()
        for i in range(0, len(gs_words)):
             if gs_words[i] != gs_words[i]:
                gs_words[i] = gs_original_words[i]
    # elif 'ja_Hira.json' in json_fname:
    #     gs_words = gs[gscolumns[3]].values.tolist()
    elif 'en.json' in json_fname:
        gs_words = gs[gscolumns[GSCOL_EN]].values.tolist()
    # elif 'ko.json' in json_fname:
    #     gs_words = gs[gscolumns[3]].values.tolist()
    elif 'zh_CN.json' in json_fname:
        gs_words = gs[gscolumns[GSCOL_ZH_CN]].values.tolist()
    elif 'zh_TW.json' in json_fname:
        gs_words = gs[gscolumns[GSCOL_ZH_TW]].values.tolist()
    elif 'vi.json' in json_fname:
        gs_words = gs[gscolumns[GSCOL_VI]].values.tolist()
    return gs_words

def i18n_translated_check(source_json, target_json):
    """ source_jsonにある文章が翻訳されているかチェックし、
        target_jsonに存在しなければログ出力。 
    """
    not_translation_list = []
    src_lang = i18n_read_json(source_json)
    target_lang = i18n_read_json(target_json)
    for src_word in src_lang.keys():
        if src_word not in target_lang.keys():
            print(f"{os.path.basename(target_json)} \"{src_word}\" Translation not found.")
            not_translation_list.append(src_word)
    return not_translation_list

def i18n_find_word_from_json(gs, json_path):
    """　spread sheetにあってjsonにない該当言語の文章を探す。
    """        
    print(f'Find google spread sheet words from {json_path}... ')
    not_found_lsit = []

    json_words = i18n_read_json(json_path)
    json_fname = os.path.basename(json_path)    
    gs_words = i18n_get_gs_words(json_fname, gs)
    for gw in gs_words:
        if gw not in json_words:
            """ TODO spread sheet側文章には「,」がない？"""
            print(f"\"{gw}\" not found in {json_fname}.")
            not_found_lsit.append(gw)
    return not_found_lsit

def i18n_find_word_from_gs(json_path, gs):
    """ jsonにあってspread sheetにない文章を探す。    
        新潟県版翻訳が存在しないケースもあるので、ja.jsonの場合は2列から検索。 
    """    
    print(f'Find {json_path} words from spread sheet... ')  
    not_found_lsit = []  
    
    json_words = i18n_read_json(json_path).items()
    json_fname = os.path.basename(json_path)    
    gs_words = i18n_get_gs_words(json_fname, gs)    
    for jw in json_words:
        if jw[1] not in gs_words:
            """ TODO spread sheet側文章には「,」がない？"""
            print(f"{json_fname} \"{jw[1]}\" not found in spread sheet.")
            not_found_lsit.append(jw[1])
    return not_found_lsit

def i18n_json_words_check(resource_files):
    """ localesディレクトリ配下のi18njsonについて、
        各言語で同じリソースがリストされているかチェックする。
    """
    not_translation_lists = []
    for resource in resource_files:
        if 'ja.json' in resource:
            continue
        not_translation_lists.append(i18n_translated_check('./locales/ja.json', resource))
    return not_translation_lists

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

def i18n_create_json(dst_json_path, base_words, gs):
    target_words = i18n_get_gs_words(dst_json_path, gs)
    od = OrderedDict()
    for i, word in enumerate(base_words):
        ''' nan chrck. '''
        if target_words[i] == target_words[i]:            
            ''' multi trans. '''
            if word not in od:
                od[word] = target_words[i]
            else:
                if type(od[word]) == list:
                    od[word].append(target_words[i])
                else:                    
                    wl = [od[word], target_words[i]]
                    od[word] = wl
        else:
            od[word] = ''

    ''' output json''' 
    with open(dst_json_path, 'w') as f:
        json.dump(od, f, indent=4, ensure_ascii=False)

def i18n_create_json_from_gs(google_spread_sheet_url, dst_dir):
    ''' google spread sheetから各言語向けi18n jsonを出力。 
        json出力後に、vueで使用されていないリソースのcheckも行う。
    '''
    dst_jsons = ['ja.json', 'en.json', 'zh_CN.json', 'zh_TW.json', 'vi.json']
    gs = i18n_get_gs(google_spread_sheet_url)
    base_words = i18n_get_gs_words("ja.json", gs)
    for dst_json in dst_jsons:
        dst_json = os.path.join(dst_dir, dst_json)
        i18n_create_json(dst_json, base_words, gs)
    
    # i18n_unused_check('/Users/saeki/dev/covid19', 'locales/ja.json')
    return

def main():
    sheet_url = "https://docs.google.com/spreadsheets/d/1hcU7fT2peAlKNH5Dcp9xufuXH4vf5FGsRKxcF9WC9zc/export?format=csv&gid=17066585"
    # upload_test_url = "https://docs.google.com/spreadsheets/d/14283nuNCBeSNe4M6HSdar_9oVug2p15mkCNLwRrb4JQ/edit#gid=0"
    # upload_test_sheet_id = "14283nuNCBeSNe4M6HSdar_9oVug2p15mkCNLwRrb4JQ"
    resource_files = glob.glob('./locales/*.json')
    
    # ローカルリソース一貫性チェック
    # i18n_json_words_check(resource_files)
    
    # ローカルのvueソース - json i18nリソースを比較、利用されていないリソース有無のチェック
    # i18n_unused_check('/Users/saeki/dev/covid19', 'locales/ja.json')

    # ローカルリソースとgoogle spread sheet差分チェック
    # i18n_diff_json_and_gs(sheet_url, resource_files)

    # google spread sheet から各言語リソースjson出力
    dst_dir = './out_locales'
    i18n_create_json_from_gs(sheet_url, dst_dir)

if __name__ =='__main__':
    main()
