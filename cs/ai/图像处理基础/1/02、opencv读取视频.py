import cv2

#读取视频
# # rstp = 'rstp://admin:admin@192.168.1.23'
# cap = cv2.VideoCapture('data/car.mp4')
#
# if cap.isOpened():  #判断是否捕获成功
#
#     while True:  #循环读取每一帧
#         ret,frame = cap.read() #读取视频的每一帧
#
#         if ret:  #判断是否读取到数据
#             cv2.imshow('img',frame)
#             if cv2.waitKey(20) == 27:  #判断  如果键盘输入的是 esc，则提前结束视频读取
#                 break
#         else:  #视频读取完成，结束while循环
#             break
# else:
#     print('视频捕获失败')
#
# cap.release()  #释放资源
# cv2.destroyAllWindows() #销毁所有窗口

#2、视频保存
# rstp = 'rstp://admin:admin@192.168.1.23'
cap = cv2.VideoCapture('data/car.mp4')
# cap = cv2.VideoCapture(0)
# fourcc = cv2.VideoWriter_fourcc('M','P','4','V')
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = cap.get(cv2.CAP_PROP_FPS)

w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

video_writer = cv2.VideoWriter('data/car_save.mp4',fourcc=fourcc,fps=fps,frameSize=(w,h),apiPreference=0)

if cap.isOpened():  #判断是否捕获成功

    while True:  #循环读取每一帧
        ret,frame = cap.read() #读取视频的每一帧

        if ret:  #判断是否读取到数据
            cv2.imshow('img',frame)

            video_writer.write(frame)
            if cv2.waitKey(20) == 27:  #判断  如果键盘输入的是 esc，则提前结束视频读取
                break
        else:  #视频读取完成，结束while循环
            break
else:
    print('视频捕获失败')

cap.release()  #释放资源
cv2.destroyAllWindows() #销毁所有窗口