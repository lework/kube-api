# -*- coding: utf-8 -*-

# @Version : 1.0
# @Time    : 2021/05/26 20:12
# @Author  : lework
# @File    : update.py
# @Desc    : 用于更新k8s新版本的api信息

import os
import json
import requests
import argparse

data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static/data/data.json')
docs_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../docs/static/data/data.json')


def get_api_data(version="v1.21.1"):
    data_url = "https://github.com/kubernetes/kubernetes/blob/{version}/api/openapi-spec/swagger.json".format(
        version=version)
    file_name = "{version}-swagger.json".format(version=version)

    if not os.path.exists(file_name):
        req = requests.get(url=data_url)
        req_json = req.json()
        with open(file_name, 'w+') as f:
            f.write(json.dumps(req_json))

    with open(file_name, 'r') as f:
        api_json_data = json.loads(f.read())

    return api_json_data


def generate_kind_data(version, data):
    group_data = []
    kinds = {}
    for i in data['definitions']:
        if 'x-kubernetes-group-version-kind' not in data['definitions'][i]:
            continue
        group_data.extend(data['definitions'][i]['x-kubernetes-group-version-kind'])

    for i in group_data:
        if 'kind' not in i or not i['kind']:
            continue
        if 'group' not in i or not i['group']:
            continue
        if 'version' not in i or not i['version']:
            continue

        if i['kind'] not in kinds:
            kinds[i['kind']] = {
                i['group']: [i['version']]
            }
        if i['group'] not in kinds[i['kind']]:
            kinds[i['kind']][i['group']] = [i['version']]
        else:
            if i['version'] not in kinds[i['kind']][i['group']]:
                kinds[i['kind']][i['group']].append(i['version'])
    return kinds


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='获取 k8s 版本 group api 信息')
    parser.add_argument('-v', dest='version', type=str, help='k8s 版本列表，多个以逗号分隔', required=True)
    args = parser.parse_args()

    version_list = args.version.split(',')
    print("【Version List】", version_list)
    
    api_json_data = {}
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            api_json_data = json.loads(f.read())

    kind_data = None
    for v in version_list:
        if v in api_json_data:
            print("【K8S Version】", v , "跳过")
            continue

        a = get_api_data(v)
        kind_data = generate_kind_data(v, a)
        api_json_data[v] = kind_data

    if kind_data:
        print("【更新文件】")
        with open(data_file, 'w+') as f:
            f.write(json.dumps(api_json_data))
        with open(docs_data_file, 'w+') as f:
            f.write(json.dumps(docs_data_file))
            
    print("【执行结束】")
