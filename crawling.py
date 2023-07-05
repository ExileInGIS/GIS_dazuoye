import requests
import threading
import pandas as pd
from lxml import etree
import itertools
import numpy
import json
AK="iNcU8nqYs08Le0v8k9zehlCIOEXWEw7o"
#AK= "LZomarHPjAy7GZcZQVEcMNDTGsiQKq6B"
output = "json"

# 全部信息列表
count=list()
average=list()

def WGS_to_bd(coord):
    x = coord[0]
    y = coord[1]
    service = "http://api.map.baidu.com/geoconv/v1/?"
    f = 1; t = 5
    parameters = f"coords={x},{y}&from={f}&to={t}&ak={AK}"
    url = service + parameters
    response = requests.get(url)
    s=response.text
    dic=json.loads(s)
    return [dic["result"][0]["x"],dic["result"][0]["y"]]

#坐标纠差
def rectify(lng,lat):
    #对地理编码得到的坐标进行转换，并计算偏差
    d_lng = lng - WGS_to_bd([lng,lat])[0]
    d_lat = lat - WGS_to_bd([lng,lat])[1]
    #根据偏差对坐标进行纠偏
    WGS_lng = lng + d_lng
    WGS_lat = lat + d_lat
    return [WGS_lng,WGS_lat]

def get_location(address):
    service ="http://api.map.baidu.com/geocoding/v3/?"
    city="上海市"
    parameters = f"address={address}&output={output}&ak={AK}&city={city}"
    url = service + parameters
    response = requests.get(url)
    text=response.text
    dic=json.loads(text)
    status = dic["status"]
    if status==0:
        lng = dic["result"]["location"]["lng"]
        lat = dic["result"]["location"]["lat"]
        [WGS_lng,WGS_lat]=rectify(lng,lat)
        return [WGS_lng,WGS_lat]
    else:
        print(f"{address}:地理编码不成功")
        return["unknown","unknown"]
        
    

#生成1-10页url
def url_creat(url):
    #基础url
    #url= "https://sh.lianjia.com/ershoufang/minhang/"
    #生成url列表
    links=[url+"pg"+str(i) for i in range(1,2)]
    #实际因为额度限制，无法完全爬完，用的是range(1,100,4)
    return links

#对url进行解析
def url_parse(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'lianjia_uuid=7e346c7c-5eb3-45d9-8b4f-e7cf10e807ba; UM_distinctid=17a3c5c21243a-0c5b8471aaebf5-6373267-144000-17a3c5c21252dc; _smt_uid=60d40f65.47c601a8; _ga=GA1.2.992911268.1624510312; select_city=370200; lianjia_ssid=f47906f0-df1a-49e2-ad9b-648711b11434; CNZZDATA1253492431=1056289575-1626962724-https%253A%252F%252Fwww.baidu.com%252F%7C1626962724; CNZZDATA1254525948=1591837398-1626960171-https%253A%252F%252Fwww.baidu.com%252F%7C1626960171; CNZZDATA1255633284=1473915272-1626960625-https%253A%252F%252Fwww.baidu.com%252F%7C1626960625; CNZZDATA1255604082=1617573044-1626960658-https%253A%252F%252Fwww.baidu.com%252F%7C1626960658; _jzqa=1.4194666890570963500.1624510309.1624510309.1626962867.2; _jzqc=1; _jzqy=1.1624510309.1626962867.2.jzqsr=baidu|jzqct=%E9%93%BE%E5%AE%B6.jzqsr=baidu; _jzqckmp=1; _qzjc=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2217a3c5c23964c1-05089a8de73cbf-6373267-1327104-17a3c5c23978b3%22%2C%22%24device_id%22%3A%2217a3c5c23964c1-05089a8de73cbf-6373267-1327104-17a3c5c23978b3%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.baidu.com%2Flink%22%2C%22%24latest_referrer_host%22%3A%22www.baidu.com%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_utm_source%22%3A%22baidu%22%2C%22%24latest_utm_medium%22%3A%22pinzhuan%22%2C%22%24latest_utm_campaign%22%3A%22wyyantai%22%2C%22%24latest_utm_content%22%3A%22biaotimiaoshu%22%2C%22%24latest_utm_term%22%3A%22biaoti%22%7D%7D; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1624510327,1626962872; _gid=GA1.2.134344742.1626962875; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1626962889; _qzja=1.1642609541.1626962866646.1626962866646.1626962866647.1626962872770.1626962889355.0.0.0.3.1; _qzjb=1.1626962866646.3.0.0.0; _qzjto=3.1.0; _jzqb=1.3.10.1626962867.1; srcid=eyJ0Ijoie1wiZGF0YVwiOlwiNzQ3M2M3OWQyZTQwNGM5OGM1MDBjMmMxODk5NTBhOWRhNmEyNjhkM2I5ZjNlOTkxZTdiMDJjMTg0ZGUxNzI0NDQ5YmZmZGI1ZjZmMDRkYmE0MzVmNmNlNDIwY2RiM2YxZTUzZWViYmQwYmYzMDQ1NDcyMzYwZTQzOTg3MzJhYTRjMTg0YjNhYjBkMGMyZGVmOWZiYjdlZWQwMDcwNWFkZmI5NzA5MjM1NmQ1NDg0MzQ3NGIzYjkwY2IyYmEwMjA2NjBjMjI2OWRjNjFiNDE3ZDc1NGViNjhlMzIzZmI0MjFkNzU5ZGNlMzAzMDhlNDAzYzIzNjllYWFlMzYxZGYxYjNmZmVkNGMxYTk1MmQ3MGY2MmJhMTQ1NWI4ODIwNTE5ODI2Njg2MmVkZTk4OWZiMDhjNTJhNzE3OTBlNDFiZDQzZTlmNDNmOGRlMTFjYTAwYTRlZTZiZWY5MTZkMTcwN1wiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCI3ZjI1NWI1ZlwifSIsInIiOiJodHRwczovL3FkLmxpYW5qaWEuY29tL2Vyc2hvdWZhbmcvMTAzMTE2MDkzOTU5Lmh0bWwiLCJvcyI6IndlYiIsInYiOiIwLjEifQ==',
        'Host': 'sh.lianjia.com',
        'Pragma': 'no-cache',
        'Referer': 'https://sh.lianjia.com/',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'}
    response=requests.get(url=url,headers=headers).text
    tree=etree.HTML(response)
    #ul列表下的全部li标签+
    li_List=tree.xpath("//*[@class='sellListContent']/li")
    #创建线程锁对象
    lock = threading.RLock()
    #上锁
    lock.acquire()
    for li in li_List:
        #标题
        title=li.xpath('./div/div/a/text()')[0]
        #网址
        link=li.xpath('./div/div/a/@href')[0]
        #位置
        postion=li.xpath('./div/div[2]/div/a/text()')[0]+li.xpath('./div/div[2]/div/a[2]/text()')[0]
        #户型
        types=li.xpath('./div/div[3]/div/text()')[0].split(' | ')[0]
        #面积
        area=li.xpath('./div/div[3]/div/text()')[0].split(' | ')[1]
        #房屋信息
        info=li.xpath('./div/div[3]/div/text()')[0].split(' | ')[2:-1]
        info=''.join(info)
        #总价
        total_price=li.xpath('.//div/div[6]/div/span/text()')[0]+'万'
        #单价
        unit_price=li.xpath('.//div/div[6]/div[2]/span/text()')[0]
        dic={'位置':postion,'户型':types,'面积':area,'单价':unit_price,'总价':total_price,'标题':title,'相关信息':info,'链接':link}
        #print(url)
        #将房屋信息加入总列表中
        count.append(dic)
    #解锁
    lock.release()
def run(url):
    links = url_creat(url)
    thread_list = []
    #多线程爬取
    for i in links:
        x=threading.Thread(target=url_parse,args=(i,))
        thread_list.append(x)

    for t in thread_list:
        t.start()

    for t in thread_list:
        t.join()

    #将全部房屋信息转化为excel
    count.sort(key = lambda x:x["位置"])
    #print(len(count))
    for key, group in itertools.groupby(count, key=lambda x:x['位置']):
        groupList = list(group)
        priceList = []
        positionList=[]
        for h in groupList:
            l = h['单价'].replace('元/平','')
            l = l.replace(',','')
            l = float(l)
            priceList.append(l)
            positionList.append(get_location(h['位置']))
        average_price = ("%.2f" % numpy.mean(priceList))
        average.append({'位置':key,'number':len(groupList),'平均房价（元/平）':average_price,"lng,lat":positionList[0]})
    data1=pd.DataFrame(count)
    data2=pd.DataFrame(average)
    #保存文件到本地
    with pd.ExcelWriter('./houseInfo2.xlsx') as writer:  
        data1.to_excel(writer, index=False, sheet_name='Sheet1')
        data2.to_excel(writer, index=False, sheet_name='Sheet2')
    return data1,data2
#if __name__ == '__main__':
    run(url)
