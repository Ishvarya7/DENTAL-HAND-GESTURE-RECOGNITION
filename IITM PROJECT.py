from flask import Flask,render_template,Response,jsonify
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
def check(l):
    std_dev=np.std(l)
    if 9<=std_dev<=26:
        return 1
    else:
        return 0
def stop(lmlist,hand):
    l=[8,12,16,20]
    if((lmlist[4][0]<lmlist[3][0] and hand['type']=="Right") or(lmlist[4][0]>lmlist[3][0] and hand['type']=="Left")) :
        return 0
    for i in l:
        if(lmlist[i][1]>lmlist[i-1][1]):
            return 0
    return 1
def deep_stop(lmlist,hand):
    l=[8,12,16,20]
    if((lmlist[4][0]<lmlist[3][0] and hand['type']=="Right") or(lmlist[4][0]>lmlist[3][0] and hand['type']=="Left")) :
        return 0
    for i in l:
        if(lmlist[i][1]>lmlist[i-3][1]):
            return 0
    return 1
detector=HandDetector(minTrackCon=0.8,detectionCon=0.8,maxHands=1)
cap=cv2.VideoCapture(0)
#out=cv2.VideoWriter("output.avi",cv2.VideoWriter_fourcc(*'MJPG'), 25, (640,480))
app=Flask(__name__)
gestures=["Invalid Gesture","Stop","Pain","I am okay","Hurts a little","Hurts a lot","I want to talk","Rinse/Suction my mouth","I want to scratch my face","No Hand Found"]
index=0
flag_voice="False"
length=0
flag=0
counter=0
angle=0
ch=0
list=[]
act=0
cap=cv2.VideoCapture(0)
def gen_frames():
    global length,act,flag,index,angle,ch,counter,flag_voice,list
    while True:
        ret,image=cap.read()
        if ret:
            hands=detector.findHands(image,draw=False)
            if hands:
                hand=hands[0]
                lmlist=hand["lmList"]
                fingers=detector.fingersUp(hand)
                if flag==0:
                        if stop(lmlist,hand):
                            index=1
                        elif (not stop(lmlist,hand)) and deep_stop(lmlist,hand):
                            flag=3
                        elif fingers==[0,0,0,0,0]:
                            index=2
                        elif fingers==[0,0,1,1,1] or fingers==[1,0,1,1,1]:
                            index=3
                        else:
                            x1,y1=lmlist[8][0],lmlist[8][1]
                            x2,y2=lmlist[4][0],lmlist[4][1]
                            length=math.hypot(x2-x1,y2-y1)
                            if fingers==[0,1,0,0,0]:
                                flag=2
                                list.append(lmlist[8][0])
                            elif fingers[2:]==[0,0,0] and fingers[0]==1:    
                                if(43<=length<=65) and fingers[1]==1:
                                    index=5
                                elif(25<length<43):
                                    index=4
                                else:
                                    if fingers[1]==0:
                                        flag=1
                                        ch=0
                                    else:
                                        index=0
                            else:
                                index=0            
                else:
                    l_prev=length
                    x1,y1=lmlist[8][0],lmlist[8][1]
                    x2,y2=lmlist[4][0],lmlist[4][1]
                    length=math.hypot(x2-x1,y2-y1)
                    if flag==2 and fingers==[0,1,0,0,0]:
                        counter+=1
                        list.append(lmlist[8][0])
                        if (counter>=52):
                            flag=0
                            if check(list)==1:                            
                                index=7
                                list=[]
                                counter=0
                    elif (flag==1 and fingers[2:]==[0,0,0] and fingers[0]==1 and 0<=length<=65):
                        if abs(length-l_prev)>=4:
                            ch+=1
                        counter+=1
                        if (counter>=13):
                            counter=0
                            flag=0
                            if (ch>=4):
                                index=8
                                list=[]
                                ch=0
                    elif (flag==3 and (not stop(lmlist,hand)) and deep_stop(lmlist,hand)):
                        counter+=1
                        if(counter>=5):
                            flag=0
                            index=6
                            list=[]
                            counter=0
                    else:
                        list=[]
                        counter=0
                        flag=0
                        ch=0
            else:
                flag=0
                counter=0
                list=[]
                index=9
            image=cv2.putText(image,gestures[index],(50,50),cv2.FONT_HERSHEY_PLAIN,2,(255,0,0),2)
            cv2.imshow("Image",image)
            success,final_img=cv2.imencode('.jpg',image)
            frame=final_img.tobytes()
            if(index==0 or index==9):
                flag_voice="False"
            else:
                flag_voice="True"
            yield(b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n'+frame+b'\r\n')
            if(index==8):
                cv2.waitKey(100)

            #out.write(image)
        act=index
        if cv2.waitKey(1)==ord('q'):
                break
        flag_voice="False"
    cap.release()
    #out.release()
    cv2.destroyAllWindows()
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),mimetype='multipart/x-mixed-replace;boundary=frame')
@app.route('/get_text')
def get_text():
    text = gestures[act]
    return jsonify(text=text)
@app.route('/get_voice_flag')
def get_voice_flag():
    tt=flag_voice
    return jsonify(text=tt)
if __name__=="__main__": 
    app.run(host='http://dentalsign.42web.io',debug=True) 