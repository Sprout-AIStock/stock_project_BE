# 네이버 증권 API를 통해서 시총, 가격, 차트를 받아옵니다.
import json
import urllib.request

#종목 코드
item_code = "373220"
url = "https://m.stock.naver.com/api/stock/%s/integration"%(item_code)
#urllib.request를 통해 링크의 결과를 가져옵니다.
raw_data = urllib.request.urlopen(url).read()
#추후, 데이터 가공을 위해 json 형식으로 변경 합니다.
json_data = json.loads(raw_data)

def print_structure(data, indent=0):
    prefix = " " * indent
    if isinstance(data, dict):
        for key in data:
            print(f"{prefix}- {key}")
            print_structure(data[key], indent + 2)
    elif isinstance(data, list):
        print(f"{prefix}[List with {len(data)} elements]")
        if data:
            print_structure(data[0], indent + 2)
    else:
        print(f"{prefix}{type(data).__name__}: {str(data)[:50]}")

print_structure(json_data)


#종목명 가져오기
stock_name = json_data['stockName']
print("종목명 : %s"%(stock_name))

#가격 가져오기
current_price = json_data['dealTrendInfos'][0]['closePrice']
print("가격 : %s"%(current_price))

#시총 가져오기
for code in json_data['totalInfos']:
    if 'marketValue' == code['code']:
        marketSum_value = code['value']
        print("시총 : %s"%(marketSum_value))

#PER 가져오기
for i in json_data['totalInfos']:
    if 'per' == i['code']:
        per_value_str = i['value']
        print("PER : %s"%(per_value_str))


#PBR 가져오기
for v in json_data['totalInfos']:
    if 'pbr' == v['code']:
        pbr_value_str = v['value']
        print("PBR : %s"%(pbr_value_str))