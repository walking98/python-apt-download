#! -coding:utf8 -*-
import threading,sys
import requests
import time
import os
from mongodb_queue import MogoQueue

PREFIX_STR = 'Filename: '
BASE_DIR = '~/KYLIN-ALL/'
BASE_URL = 'http://archive.kylinos.cn/kylin/KYLIN-ALL/'

class MulThreadDownload(threading.Thread):
    def __init__(self,url,startpos,endpos,f):
        super(MulThreadDownload,self).__init__()
        self.url = url
        self.startpos = startpos
        self.endpos = endpos
        self.fd = f

    def download(self):
        print("start thread:%s at %s" % (self.getName(), time.time()))
        #headers = {"Range":"bytes=%s-%s"%(self.startpos,self.endpos)}
        res = requests.get(self.url)#,headers=headers)
        # res.text 是将get获取的byte类型数据自动编码，是str类型， res.content是原始的byte类型数据
        # 所以下面是直接write(res.content)
        self.fd.seek(self.startpos)
        self.fd.write(res.content)
        print("stop thread:%s at %s" % (self.getName(), time.time()))
        # f.close()

    def run(self):
        self.download()

def downloadOne(lfile, rfile):
    #print("lfile %s rfile:%s"%(lfile,rfile))
    #获取文件的大小和文件名
    filename = lfile.split('/')[-1]
    #print  requests.head(rfile).headers
    filesize = 100#int(requests.head(rfile).headers['Content-Length'])
    #print("%s filesize:%s"%(filename,filesize))

    #线程数
    threadnum = 1
    #信号量，同时只允许3个线程运行
    #threading.BoundedSemaphore(threadnum)
    # 默认3线程现在，也可以通过传参的方式设置线程数
    step = filesize // threadnum
    mtd_list = []
    start = 0
    end = -1

    # 请空并生成文件
    tempf = open(lfile,'w')
    tempf.close()
    # rb+ ，二进制打开，可任意位置读写
    with open(lfile,'rb+') as  f:
        fileno = f.fileno()
        # 如果文件大小为11字节，那就是获取文件0-10的位置的数据。如果end = 10，说明数据已经获取完了。
        while end < filesize -1:
            start = end +1
            end = start + step -1
            if end > filesize:
                end = filesize
            # print("start:%s, end:%s"%(start,end))
            # 复制文件句柄
            dup = os.dup(fileno)
            # print(dup)
            # 打开文件
            fd = os.fdopen(dup,'rb+',-1)
            # print(fd)
            t = MulThreadDownload(rfile,start,end,fd)
            t.start()
            mtd_list.append(t)

        for i in  mtd_list:
            i.join()

def mkdir(path):
    path = path.strip()
    isExists = os.path.exists(os.path.join(BASE_DIR, path))
    if not isExists:
        os.makedirs(os.path.join(BASE_DIR, path))
        return True
    else:
        return False    

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
                rfile = BASE_URL + url
                lfile = path + fileName
                try:
                    f =open(lfile,'r')
                    f.close()
                    print('download skip')
                except IOError:
                    mkdir(path)
                    downloadOne(lfile, rfile)
                    print('download ok')
                self.que.complete(url) ##设置为完成状态

def startDown(url,rule,num,start,decoding=None):
    if not decoding:
        decoding='utf8'
    #req=urllib.request.urlopen(url)
    #response= request.get(url, 3)
    #body=response.text #req.read().decode(decoding)
    
    print('file='+url)
    f = open(url)
    body = f.read()
    f.close()
    debs = body.split('\n')

    #rule=re.compile(rule)
    #debs=rule.findall(body)
    crawl_queue = MogoQueue('cetc15-apt', 'crawl_queue')   
    #crawl_queue.clear() # CCCCC
    for l in debs:
        l = l.strip()
        if (len(l)==0 or not l.startswith(PREFIX_STR)):
            continue
        print 'deb:'  + l[start:]
        crawl_queue.push(l[start:], 'a')
    for i in range(num):
        d=download(crawl_queue)
        d.start()

if __name__ == "__main__":
    url = sys.argv[1]
    if len(sys.argv) < 3:
        print 'usage is -'
        print sys.argv[0] + ' baseDir  file [threads]'
    else:
        try:
            BASE_DIR = sys.argv[1] + '/'
            file = sys.argv[2]
            threads=10
            if (len(sys.argv)>3) :
                threads = int(sys.argv[3])
            rule=PREFIX_STR + '*'
            startDown(file,rule, threads, len(PREFIX_STR),-1)
        except ValueError, e:
            print 'error: ' + str(e)
            print ''