from bs4 import BeautifulSoup
import requests
import time

def extracthtml(fname,tag,isall=False):     #从书签指定文件夹内提取有效链接
    with open(fname,encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(),'lxml')
    
    hdir_arr = soup.find_all('h3')          #提取全部h3标签
    for hdir in hdir_arr:
        if hdir.string == tag:
             rootnode = hdir.parent.next_sibling    #rootnode为第一个非目录元素的标签
            #print(rootnode)
    if not isall and str(rootnode.contents[-1]) != '<p>\n</p>': #本层结构倒数第一个元素为链接组
        rootnode = rootnode.contents[-1]
    snd_list=[]
    for subnode in rootnode.find_all('a'):
        if subnode['href'] != 'about:blank':
            snd_list.append({'title':subnode.string,'href':subnode['href']})
    return snd_list

def links_filter(link_list):                  #将链接组过滤
    fltd = {'white':[],'grey':[],'black':[],'blocked':[]}
    headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36 QIHU 360SE',
    'Connection':'close'
    }
    
    for link in link_list:
        try:
            rps = requests.get(link['href'],headers=headers,timeout = 7)
            if rps.status_code == 200:
                fltd['white'].append(link)
                print('OK      : '+link['href'])
            #print(rps.status_code)
        except Exception as e:
            if str(e).find('10054') != -1:
                fltd['blocked'].append(link)
                print('Blocked : '+link['href'])
            elif str(e).find('timed out') != -1 or str(e).find('ConnectTimeoutError') != -1:
                fltd['grey'].append(link)
                print("Timeout : "+link['href'])
            else:
                fltd['black'].append(link)
                print("Expired : "+link['href'])
        time.sleep(1)
    print('Done!')
    return fltd
if __name__ == '__main__':
#参数部分
    filename = r'D:\Projects\[Python]HTMLParser\bookmarks_2018_10_9.html'
    fldname = 'About H'
    print('start parsing...')
    links = extracthtml(filename,fldname,True)
    fltd = links_filter(links)
    '''
    print('links to check')
    for el in fltd['grey']:
        print(el['title'])
        print(el['href'])
        print("")
    print('blocked links')
    for el in fltd['blocked']:
        print(el['title'])
        print(el['href'])
        print("")
'''
    with open(fldname+'-解析结果.html','w',encoding='utf-8') as f:
        htmlbase = r'''
    <!DOCTYPE html><html lang="cn"><head><meta charset="UTF-8"><title>Results</title><style type="text/css">table{position:absolute;top:0;left:0;right:0;width:70%%;margin:3em auto 5em}table th{background:#9cc;font-weight:400;line-height:30px;font-size:14px;color:#FFF}table tr:nth-child(odd){background:#F4F4F4}table tr:nth-child(even){background:#FFF}</style></head><body><table>%s</table></body></html>
'''
        stunit = ''
        for el in fltd['grey']:
            stunit =''.join([stunit,'<tr><td>',el['title'],'</td><td><a href="%s" target="_blank">' % el['href'],el['href'],'</a></td></tr>'])
        stall = ''.join(['<tr><th colspan=2>超时待确认</th></tr>',stunit])
        
        stunit = ''
        for el in fltd['blocked']:
            stunit =''.join([stunit,'<tr><td>',el['title'],'</td><td><a href="%s" target="_blank">' % el['href'],el['href'],'</a></td></tr>'])
        stall = ''.join([stall,'<tr><th colspan=2>被墙</th></tr>',stunit])
        
        stunit = ''
        for el in fltd['black']:
            stunit =''.join([stunit,'<tr><td>',el['title'],'</td><td><a href="%s" target="_blank">' % el['href'],el['href'],'</a></td></tr>'])
        stall = ''.join([stall,'<tr><th colspan=2>失效</th></tr>',stunit])
        
        f.write(htmlbase % stall)
    f.close()