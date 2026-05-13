import json
import sys
import datetime
import hashlib
import hmac
import argparse
import os
import requests
import time
from dotenv import load_dotenv
from pathlib import Path


method = 'POST'
host = 'visual.volcengineapi.com'
region = 'cn-north-1'
endpoint = 'https://visual.volcengineapi.com'
service = 'cv'

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(key.encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'request')
    return kSigning


def formatQuery(parameters):
    request_parameters_init = ''
    for key in sorted(parameters):
        request_parameters_init += key + '=' + parameters[key] + '&'
    request_parameters = request_parameters_init[:-1]
    return request_parameters


def signV4Request(access_key, secret_key, service, req_query, req_body):
    if access_key is None or secret_key is None:
        print('No access key is available.')
        sys.exit()

    t = datetime.datetime.utcnow()
    current_date = t.strftime('%Y%m%dT%H%M%SZ')
    # current_date = '20210818T095729Z'
    datestamp = t.strftime('%Y%m%d')  # Date w/o time, used in credential scope
    canonical_uri = '/'
    canonical_querystring = req_query
    signed_headers = 'content-type;host;x-content-sha256;x-date'
    payload_hash = hashlib.sha256(req_body.encode('utf-8')).hexdigest()
    content_type = 'application/json'
    canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + host + \
                        '\n' + 'x-content-sha256:' + payload_hash + \
                        '\n' + 'x-date:' + current_date + '\n'
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + \
                        '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
    # print(canonical_request)
    algorithm = 'HMAC-SHA256'
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'request'
    string_to_sign = algorithm + '\n' + current_date + '\n' + credential_scope + '\n' + hashlib.sha256(
        canonical_request.encode('utf-8')).hexdigest()
    # print(string_to_sign)
    signing_key = getSignatureKey(secret_key, datestamp, region, service)
    # print(signing_key)
    signature = hmac.new(signing_key, (string_to_sign).encode(
        'utf-8'), hashlib.sha256).hexdigest()
    # print(signature)

    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + \
                           credential_scope + ', ' + 'SignedHeaders=' + \
                           signed_headers + ', ' + 'Signature=' + signature
    # print(authorization_header)
    headers = {'X-Date': current_date,
               'Authorization': authorization_header,
               'X-Content-Sha256': payload_hash,
               'Content-Type': content_type
               }
    # print(headers)

    # ************* SEND THE REQUEST *************
    request_url = endpoint + '?' + canonical_querystring

    try:
        response = requests.post(request_url, headers=headers, data=req_body)
    except Exception as err:
        print(f'error occurred: {err}')
        raise
    else:
        return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="使用即梦AI生成封面图")
    parser.add_argument("--title", required=True, help="文章标题")
    parser.add_argument("--description", required=True, help="文章描述")
    parser.add_argument("--output", default=".", help="输出目录")

    args = parser.parse_args()

    # 从环境变量获取密钥
    current_file_path = Path(__file__).resolve()
    # 获取当前文件所在目录
    current_dir = current_file_path.parent.parent
    env_path = os.path.join(str(current_dir), '.env')
    load_dotenv(dotenv_path=env_path)

    # 读取环境变量
    access_key = os.getenv("VOLCENGINE_ACCESS_KEY")
    secret_key = os.getenv("VOLCENGINE_SECRET_KEY")

    # 请求Query，按照接口文档中填入即可
    query_params = {
        'Action': 'CVSync2AsyncSubmitTask',
        'Version': '2022-08-31',
    }
    formatted_query = formatQuery(query_params)

    # 请求Body，按照接口文档中填入即可
    prompt = f"一篇标题为'{args.title}'的文章的专业封面图。{args.description}。图像应该视觉吸引力强，与内容相关，适合作为博客或文章标题的头部图片。"

    body_params = {
        "req_key": "jimeng_t2i_v40",
        "force_single":True,
        "prompt": prompt
    }
    formatted_body = json.dumps(body_params)

    response = signV4Request(access_key, secret_key, service,
                  formatted_query, formatted_body)
    task_id=""
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 10000:
            task_id = data.get("data", {}).get("task_id")

    if task_id =="":
        sys.exit()

    image_urls=[]
    # 请求Query，按照接口文档中填入即可
    query_params = {
        'Action': 'CVSync2AsyncGetResult',
        'Version': '2022-08-31',
    }
    formatted_query = formatQuery(query_params)
    body_params = {
        "req_key": "jimeng_t2i_v40",
        "task_id": task_id,
        "req_json": '{"return_url": true}'
    }
    formatted_body = json.dumps(body_params)

    for _ in range(10):  # 最多查询30次
        response = signV4Request(access_key, secret_key, service,
                                 formatted_query, formatted_body)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 10000:
                task_data = data.get("data", {})
                status = task_data.get("status")
                if status == "done":
                    image_urls =  task_data.get("image_urls", [])
                    break
                elif status in ["in_queue", "generating"]:
                    print("任务处理中...")
                    time.sleep(5)
                    continue
        time.sleep(5)

    if not image_urls:
        sys.exit()

    # 创建输出目录（如果不存在）
    os.makedirs(args.output, exist_ok=True)

    # 生成文件名
    output_path = os.path.join(args.output, f"cover.png")

    # 下载并保存图像
    image_response = requests.get(image_urls[0])
    image_response.raise_for_status()

    with open(output_path, 'wb') as f:
        f.write(image_response.content)

    print(f"封面图生成成功: {output_path}")