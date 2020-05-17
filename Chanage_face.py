import requests
import json
import simplejson
import base64
import random
import cv2
import time
import os
from moviepy.editor import *

#第一步：获取人脸关键点
def find_face(imgpath):
    """
    :param imgpath: 图片的地址
    :return: 一个字典类型的人脸关键点 如：{'top': 156, 'left': 108, 'width': 184, 'height': 184}
    """
    http_url = 'https://api-cn.faceplusplus.com/facepp/v3/detect' #获取人脸信息的接口
    data = {
        "api_key":"x2NyKaa6vYuArYwat4x0-NpIbM9CrwGU",#访问url所需要的参数
        "api_secret":"OuHx-Xaey1QrORwdG7QetGG5JhOIC8g7",#访问url所需要的参数
        "image_url":imgpath, #图片地址
        "return_landmark":1
    }


    files = {'image_file':open(imgpath,'rb')} #定义一个字典存放图片的地址
    response = requests.post(http_url,data=data,files=files)
    res_con1 = response.content.decode('utf-8')
    res_json = simplejson.loads(res_con1)
    faces = res_json['faces']
    list = faces[0]
    rectangle = list['face_rectangle']
    return rectangle

#第二步：实现换脸
def merge_face(image_url1, image_url2, number, num):
    """
    :param image_url1: 被换脸的图片路径
    :param image_url2: 换脸的图片路径
    :param image_url: 换脸后生成图片所保存的路径
    :param number: 换脸的相似度
    """
    f1 = open(image_url1, 'rb')
    f1_64 = base64.b64encode(f1.read())
    f1.close()
    f2 = open(image_url2, 'rb')
    f2_64 = base64.b64encode(f2.read())
    f2.close()
    url_add = 'https://api-cn.faceplusplus.com/imagepp/v1/mergeface'  # 实现换脸的接口
    try:
        #首先获取两张图片的人脸关键点
        face1 = find_face(image_url1)
        face2 = find_face(image_url2)
        #将人脸转换为字符串的格式
        rectangle1 = str(str(face1['top']) + "," + str(face1['left']) + "," + str(face1['width']) + "," + str(face1['height']))
        rectangle2 = str(str(face2['top']) + "," + str(face2['left']) + "," + str(face2['width']) + "," + str(face2['height']))
        data = {
            "api_key": "x2NyKaa6vYuArYwat4x0-NpIbM9CrwGU",
            "api_secret": "OuHx-Xaey1QrORwdG7QetGG5JhOIC8g7",
            "template_base64": f1_64,
            "template_rectangle": rectangle1,
            "merge_base64": f2_64,
            "merge_rectangle": rectangle2,
            "merge_rate": number
        }
    except:
        data = {
            "api_key": "x2NyKaa6vYuArYwat4x0-NpIbM9CrwGU",
            "api_secret": "OuHx-Xaey1QrORwdG7QetGG5JhOIC8g7",
            "template_base64": f1_64,
            "merge_base64": f2_64,
            "merge_rate": number
        }
    response1 = requests.post(url_add,data=data)
    res_con1 = response1.content.decode('utf-8')
    res_dict = json.JSONDecoder().decode(res_con1)
    try:
        result = res_dict['result']
        imgdata = base64.b64decode(result)
        file = open('img\\' + str(num) + 'res.jpg', 'wb')
        file.write(imgdata)
        file.close()
    except:
        print(res_dict)

def merge_vedio_face(face, video_path):
    cap=cv2.VideoCapture(video_path)#视频文件的读取
    if cap.isOpened()!=True:
        exit(-1)
    num = 0
    while True:
        #一一卤的捕获
        ret, img=cap.read()
        if ret!=True:
            break
        cv2.imwrite('img\\body.jpg', img)
        merge_face('img\\body.jpg', face, 90, num)#完成换脸，保存到本地
        num += 1
        time.sleep(random.random()+1)#随机延时，保证不超过并发限制，

def pic_2_video(shape):
        file=os.listdir('img')#获收所有的换脸后的图片文件名
        # filelist=['{}.png'.format(i)for i in range(100, 100+len(file))]
        # print(filelist)
        fps=30
        video_save_path='result.avi' #导出路径
        fourcc=cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')#不同视频缩码对应不同视频格式(例:
        video=cv2.VideoWriter(video_save_path, fourcc, fps, shape)
        for img in file:#开始拼接视频
            print('img\\' + img)
            pho = cv2.imread('img\\' + img)
            video.write(pho)#把图片写进视频
        video.release()#释放
        # final=VideoFileClip(video_save_path)
        # final_vedio=final.set_audio(AudioFileClip(self.video_path))#捕获原先视频中的音频信息
        # final_vedio.write_videofile('./final_vedio.mp4')

if __name__ == '__main__':
    merge_vedio_face('face.jpg', 'video.mp4')
    pic_2_video((720, 960))