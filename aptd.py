#!/usr/bin/python
# -*- coding: UTF-8 -*-

#import urllib.request
#from Download import request
import re
from mongodb_queue import MogoQueue
import threading
import os
import sys

PREFIX_STR = 'Filename: '
BASE_DIR = '~/KYLIN-ALL/'
BASE_URL = 'http://archive.kylinos.cn/kylin/KYLIN-ALL/'

class download(threading.Thread):
    def __init__(self,que):
        threading.Thread.__init__(self)
        self.que=que

    def run(self):
        while True:
            try:
                url = self.que.pop()
            except KeyError:
                print('队列没有数据了')
                break
            else:
                url = url.strip()
                pos = url.rindex('/')
                path =  url[0:pos]
                fileName = url[pos:]
                #print 'url ' + url + '   path ' + path + ' fn ' + fileName
                path = BASE_DIR + path
                mkdir(path)
                rfile = BASE_URL + url
                lfile = path + fileName
                print 'wget  -O  ' + lfile + ' ' + rfile
                os.system('wget  -O  ' + lfile + ' ' + rfile)
                self.que.complete(url) ##设置为完成状态
                print('download ok')
    
     

def mkdir(path):
    path = path.strip()
    isExists = os.path.exists(os.path.join(BASE_DIR, path))
    if not isExists:
        os.makedirs(os.path.join(BASE_DIR, path))
        return True
    else:
        return False    

def startDown(url,rule,num,start,decoding=None):
    if not decoding:
        decoding='utf8'
    #req=urllib.request.urlopen(url)
    #response= request.get(url, 3)
    #body=response.text #req.read().decode(decoding)
    
    f = open(url)
    body = f.read()
    f.close()
    debs = body.split('\n')

    rule=re.compile(rule)
    #debs=rule.findall(body)
    crawl_queue = MogoQueue('cetc15-apt', 'crawl_queue')   
    crawl_queue.clear() #
    for l in debs:
        l = l.strip()
        if (len(l)==0 or not l.startswith(PREFIX_STR)):
            continue
        print 'deb:'  + l[start:]
        crawl_queue.push(l[start:], 'a')
    for i in range(num):
        d=download(crawl_queue)
        d.start()

if __name__=='__main__':
    if len(sys.argv) < 3:
        print 'usage is -'
        print sys.argv[0] + ' baseDir  file [threads]'
    else:
        try:
            BASE_DIR = sys.argv[1] + '/'
            file = sys.argv[2]
            threads=10
            if (len(sys.argv)>3) :
                threads = sys.argv[3]
            rule=PREFIX_STR + '*'
            startDown(file,rule, threads, len(PREFIX_STR),-1)
        except ValueError, e:
            print 'error: ' + str(e)
            print ''