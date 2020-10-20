import socket
import json
import threading
import records #操作数据库的第三方库

# code : 0登录   1注册
#登录（返回码： 0登录成功    -1未找到    -2密码错误）
#注册(返回码：0注册成功    3已存在)

class UserAuthentication:
    def __init__(self):
        self.s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.s.bind(("192.168.1.2",666))
        #self.s.bind(("127.0.0.1", 666))
        self.s.listen(100)
        self.connects=None
        self.db=records.Database('mysql://root:123456789@127.0.0.1:3306/test?charset=utf8')
        print("初始化完成...")


    def conn(self):
        while True:

            client, (client_host, client_port) = self.s.accept()
            # 加入线程池
            #self.connects.append(client)
            # 用子线程来处理客户端接下来的操作
            thread = threading.Thread(target=self.recevice, args=(client, client_host, client_port))
            thread.setDaemon(True)
            thread.start()
    def recevice(self,client,client_host,client_port):
        print()
        data=client.recv(1024)
        data=data.decode()
        print(data)
        data=self.toDic(data)
        code=data["code"]

        if code==1:#注册(返回码：0注册成功    3已存在)
            print("注册")
            users=self.db.query("select * from userInfo").all()
            flagExist=False
            for i in users:
                if i.userid==data['userid']:
                    flagExist=True
            if flagExist==True:
                print("已存在")
                client.send("3\n".encode());
            else:
                print("注册成功")
                self.db.query("insert into userInfo (userid,password,email,username) values (:userid,:password,:email,:username)",**data)
                client.send("0\n".encode());
        elif code==0:#账号密码登录（返回码： 0登录成功    -1未找到    -2密码错误）
            print("账号密码登录")
            users = self.db.query("select * from userInfo").all()
            flag=False
            for i in users:
                if i.userid == data['userid']:
                    if i.password==data['password']:
                        flag=True
                        print("登陆成功")
                        client.send(("{'code':0,"+'userid:'+i.userid+',username:'+i.username+',email:'+i.email+"}\n").encode())
                        break
                    flag=True
                    print("密码错误")
                    client.send("-2\n".encode())
                    break
            if flag==False:
                print("不存在该用户")
                client.send("-1\n".encode())
        elif code==3:#绑定人脸
            print("绑定人脸")
            users = self.db.query("select * from userInfo").all()
            flag1 = False
            flag3=False
            for j in users:
                if j.face_token==data['face_token']:
                    flag3=True
                    break
            if flag3==True:
                print("已存在")
                client.send("3\n".encode())
            else:
                for i in users:
                    if i.userid==data['userId']:
                        flag1=True
                        self.db.query("update userInfo set face_token=\""+data['face_token']+"\" where userid=\""+data['userId']+'\"')
                        client.send('0\n'.encode())
                if flag1==False:
                    print("不存在该用户")
                    client.send("-1\n".encode())

        elif code==4:#人脸登录
            users = self.db.query("select * from userInfo").all()
            flag2 = False
            for i in users:
                if i.face_token==data['face_token']:
                    print("登陆成功")
                    flag2=True
                    client.send(("{'code':0,"+'userid:'+i.userid+',username:'+i.username+',email:'+i.email+"}\n").encode())
            if flag2==False:
                print("不存在该用户")
                client.send("-1\n".encode())
        elif code==5:#绑定QQ
            print("绑定QQ")
            users = self.db.query("select * from userInfo").all()
            flag1 = False
            flag3 = False
            for j in users:
                if j.qq_token == data['qq_token']:
                    flag3 = True
            if flag3 == True:
                print("已存在")
                client.send("3\n".encode())
            else:
                for i in users:
                    if i.userid == data['userId']:
                        flag1 = True
                        self.db.query(
                            "update userInfo set qq_token=\"" + data['qq_token'] + "\" where userid=\"" + data[
                                'userId'] + '\"')
                        client.send('0\n'.encode())
                        print("绑定成功")
                if flag1 == False:
                    print("不存在该用户")
                    client.send("-1\n".encode())
        elif code==6:
            print("qq登录")
            users = self.db.query("select * from userInfo").all()
            flag = False
            for i in users:
                if i.qq_token == data['userid']:
                    flag = True
                    print("登陆成功")
                    client.send(("{'code':0," + 'userid:' + i.userid + ',username:' + i.username + ',email:' + i.email + "}\n").encode())
                    break
            if flag == False:
                print("不存在该用户")
                client.send("-1\n".encode())

        # if email=="":#登录（返回码： 0登录成功    -1未找到    -2密码错误）
        #     with open("user.text") as f:
        #         userInfo=f.read()
        #         print(userInfo)
        #         f.close()
        #     userInfo=self.toDic(userInfo)
        #     userInfo=userInfo["data"]
        #     if code==0:
        #         for i in userInfo:
        #             if i["username"]==username and i["password"]==password:
        #                 client.send("0\n".encode())
        #             if i["username"]==username and i["password"]!=password:
        #                 client.send("-2\n".encode())
        #         client.send("-1\n".encode())
        #     elif code==1:
        #         flagExist=False
        #         for i in userInfo:
        #             if i["username"] == username:
        #                 flagExist=True
        #         if flagExist==False:
        #             with open("user.text") as f:
        #                 userInfo = f.read()
        #                 print(userInfo)
        #                 userInfo = self.toDic(userInfo)
        #                 # 暂时没有检验账户是否已存在
        #                 f.close()
        #             with open("user.text", "w+") as f:
        #                 userInfo["data"].append({"email": "", "username": username, "password": "","code":1})
        #                 print(json.dumps(userInfo), file=f)
        # else:#注册(返回码：0注册成功    3已存在)
        #     flag=True
        #     if email == "":
        #         client.send("\n".encode())
        #         flag=False
        #     if username == "":
        #         client.send("\n".encode())
        #         flag=False
        #     if password == "":
        #         client.send("\n".encode())
        #         flag=False
        #     if flag==True:
        #         with open("user.text") as f:
        #             userInfo = f.read()
        #             print(userInfo)
        #             userInfo=self.toDic(userInfo)
        #             #暂时没有检验账户是否已存在
        #             f.close()
        #         flagExist=False
        #         for i in userInfo["data"]:
        #             if username==i["username"]:
        #                 flagExist=True
        #         if flagExist==True:
        #             client.send("3\n".encode())
        #         else:
        #             with open("user.text","w+") as f:
        #
        #                 userInfo["data"].append({"email": email, "username": username, "password": password,"code":0})
        #                 print(json.dumps(userInfo), file=f)
        #             client.send("0\n".encode())

    def close(self):
        self.s.close()
        self.db.close()


    """
        把json格式转化为字典格式（转化为的字典类型的数据必须包含key：msg）
        data：json格式数据
        return:返回字典类型
    """

    def toDic(self,data):
        dataToDic = json.loads(data)
        return dataToDic



if __name__=="__main__":

    user=UserAuthentication()
    user.conn()