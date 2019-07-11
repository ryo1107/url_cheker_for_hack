import requests
import subprocess
from datetime import datetime, timedelta, timezone
from datetime import datetime as dt
import pprint
import numpy as np
import sys, time
import re

#警告表示の回避
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

#表の表示のためのライブラリ
from tabulate import tabulate

pp = pprint.PrettyPrinter(indent=4)

url_path = "./url_list.txt"
result_path = "./get_http_ssl_result.txt"

class pycolor:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RETURN = '\033[07m' #反転
    ACCENT = '\033[01m' #強調
    FLASH = '\033[05m' #点滅
    RED_FLASH = '\033[05;41m' #赤背景+点滅
    END = '\033[0m'
# 使い方の例 print(pycolor.RED + "RED TEXT" + pycolor.END)

# openssl s_client -connect www.google.com:443 -servername www.google.com < /dev/null 2> /dev/null | openssl x509 -text | grep Not
def check_ssl_limit(url_list):
    url=[]
    for __url in url_list:
        if __url[:5]=="https":
            url.append("https://"+re.sub('/.*$', '',__url.replace("https://","")))#https://ドメイン の形に変形
            # url.append(__url.replace("https://",""))
        else:
            url.append("http://"+re.sub('/.*$', '',__url.replace("http://","")))#http://ドメイン の形に変形
    
    __result=[]
    __result_certs=[]
    for i in url:
        if i[:5]=="http:":
            __result.append(pycolor.RETURN + " No ssl " + pycolor.END)
        elif i[:5]=="https":
            i=i[8:]#.replace("https://","")
            #ssl証明書の期限取得
            p1 = subprocess.Popen(["openssl s_client -connect "+ i +":443 -servername "+ i +" < /dev/null 2> /dev/null"], shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            p2 = subprocess.Popen(["openssl x509 -text"], stdin=p1.stdout, stdout=subprocess.PIPE,shell=True,stderr=subprocess.PIPE)
            p1.stdout.close()
            p3 = subprocess.Popen(["grep Not"],stdin=p2.stdout,stdout=subprocess.PIPE,shell=True,stderr=subprocess.PIPE)
            p2.stdout.close()
            #ssl証明書チェック???
            # pp1 = subprocess.Popen(["bash check_ssl_certs.sh "+i+" |tail"], shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            # stdout_data, stderr_data = pp1.communicate()
            # print(stdout_data.decode("utf8"))
            # print(stderr_data.decode("utf8"))
            # # print(list(pp1.stderr))
            # # print(list(pp1.stdout)[1].decode("utf8"))
            try:
                date_ = list(p3.stdout)[1].decode("utf8").replace("\n","").replace("   ","").replace("Not After : ","")
                date_ = dt.strptime(date_,"%b %d %H:%M:%S %Y %Z")
                date_limit = dt(date_.year,date_.month,date_.day,date_.hour,date_.minute,date_.second,0,timezone.utc)
                # try:
                if dt.now(timezone.utc)>date_limit:#ssl証明書の期限が切れているときに実行される
                    __result.append(pycolor.RED_FLASH + " Date Expired " + pycolor.END)
                else:
                    __result.append(date_limit)
                # except:
                #     __result.append(pycolor.RED + "ssl error" + pycolor.END)
            except: #httpsから始まるが、ドメインに問題があった際に出るエラー　date_が作成できないときに実行される
                __result.append(pycolor.RED_FLASH + " Domain error " + pycolor.END)
            p3.stdout.close()
        else:
            pass
    return __result

if __name__ == "__main__":
    with open(url_path) as f:
        url_list = [s.strip() for s in f.readlines()]
    with open(result_path) as f:
        result_list = [s.strip() for s in f.readlines()]

    pre_http_codes=result_list[0].replace(" ","").split(",")[:-1]
    pre_ssl_results=result_list[2].split(",")[:-1]
    # pp.pprint(pre_http_codes)
    # pp.pprint(pre_ssl_results)
    
    http_codes=[]
    ssl_results=[]

    for j in pre_http_codes:
        if j[:2] == "20":
            http_codes.append(j)
        elif j=="000":
            http_codes.append(pycolor.RED_FLASH+" 000 "+pycolor.END)
        else:
            http_codes.append(pycolor.RED_FLASH+" "+j+" "+pycolor.END)

    for i in pre_ssl_results:
        if i=="Verify return code: 0 (ok)" or i==" Verify return code: 0 (ok)":
            ssl_results.append("OK")
        elif i==" ":
            ssl_results.append(pycolor.RED_FLASH+" Domain Error "+pycolor.END)
        else:
            ssl_results.append(pycolor.RED_FLASH+" SSL Error "+pycolor.END)
    
    table_url=[]

    for url_ in url_list:
        try:
            table_url.append(url_[:40])
        except:
            table_url.append(url_)
    result = np.array([table_url,http_codes,ssl_results,check_ssl_limit(url_list)])
    table = result.T
    headers = ["URL", "http","SSL","Date Limit"]
    ans_table=tabulate(table, headers, tablefmt="grid")
    ans_table = ans_table + "\033["+str(len(ans_table.split("\n")))+"A" #末尾に'\033[nA'を追記し、カーソル位置をansの一番最初に移動
    time.sleep(5)
    print(ans_table)