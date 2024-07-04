# niu-control-tencent-cloud-scf
## 介绍
Apple Watch Ultra 侧边有个 Action Button，我一直想用他来快速开关小牛电动车。尽管小牛官方提供了一些快捷指令动作，但这些快捷指令无法脱离手机执行，因此在手表上运行这些快捷指令执行速度会比较慢。然而直接用手表上可原生运行的快捷指令指令，实现对小牛服务器的请求又太过复杂。

本 Repo 提供一个若干 HTTP API，请求容易通过手表原生快捷指令构造。服务将在收到这些请求后，转化为对小牛服务器的请求。这样我们就能够在手表上制作相应较为快速的，开关小牛电动车的快捷指令了。

这个 Repo 是一个可以在腾讯云云函数环境下运行的特化版本。换言之他没有跨请求的内存状态。所有状态均存储在腾讯云对象存储上。

目前程序默认操作的是你车辆列表里边的第一辆爱车。

## 不太详尽的使用教程
首先请尽量把所有云上资源都开在广州。这是因为腾讯云大陆只有广州 region 有免费的个人镜像服务。为了最快的**请求处理速度**，云资源都放在广州比较好。
1. docker build . -f docker/Dockerfile -t ccr.ccs.tencentyun.com/<你的腾讯云镜像服务个人版命名空间>/niu-control:0.0.1
2. docker push ccr.ccs.tencentyun.com/<你的腾讯云镜像服务个人版命名空间>/niu-control:0.0.1
3. 在腾讯云对象存储服务里边新建好你的 bucket，配置好 secret id 和 secret key。
4. 新建云函数
    - 建议开启镜像加速
    - 环境变量请参考 Dockerfile，根据你的实际情况填写。注意 NIU_ACCOUNT_MD5 填写你的小牛账号密码 md5hash 之后的值。
    - 镜像选取刚刚 push 的。
    - 为你的云函数生成一个 url。
5. 根据快捷指令模板进行修改
    - NiuToggleAcc https://www.icloud.com/shortcuts/2baf790628344b0aaefd32210d26a122
        - 请根据你在第四步环境变量的配置替换其中的 "default_salt"。
        - 请根据你在第四步生成的云函数 url 替换 "云函数url"。
        - 修改完后运行一下，如果电动车本来是开机状态，那么电动车会关闭，如果本来是关机状态，应该会返回 NIU not connected。
    - NiuConn https://www.icloud.com/shortcuts/d35e9eef30a9424bbad3668fbdcc4320
        - 请根据你在第四步环境变量的配置替换其中的 "default_salt"。
        - 请根据你在第四步生成的云函数 url 替换 "云函数url"。
        - 修改完运行一下，无报错即可。运行完后不要立刻再次运行 NiuToggleAcc，否则有意外打开电动车电源风险。
6. 在 iOS 手机上配置自动化，链接上电动车蓝牙设备之后，以无需确认立即运行模式运行 NiuConn
7. 将 NiuToggleAcc 绑定到手表 Action Button 上。

你现在应该能通过按动 Action Button 切换电动车电源状态。出于安全考虑，整个流程被设计成在手机靠近电动车 30s 内通过 Action Button 可以打开电动车电源，在任意时刻都可以通过 Action Button 关闭电动车电源。

## 感谢
我的小牛服务器交互代码，是修改自这位仁兄的
https://github.com/marcelwestrahome/home-assistant-niu-component