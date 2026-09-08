---
tags: []
created: 2026-09-08
updated: 2026-09-08
status: ok
---

#  CUDA安装教程

## 1.1 查看适合的cuda版本

![img-01](assets/CUDA安装教程/img-01.png)

![img-02](assets/CUDA安装教程/img-02.png)

![img-03](assets/CUDA安装教程/img-03.png)

 我电脑上支持的cuda是11.6的

## 1.2 cuda [toolkit](https://so.csdn.net/so/search?q=toolkit&spm=1001.2101.3001.7020)下载

[​​​​​kCUDA Toolkit Archive | NVIDIA Developer](https://developer.nvidia.com/cuda-toolkit-archive "​​​​​kCUDA Toolkit Archive | NVIDIA Developer")

进入上述网页，找到适合的cuda

![img-04](assets/CUDA安装教程/img-04.png)

![img-05](assets/CUDA安装教程/img-05.png)

## 1.3 cuda toolkit安装

双击exe文件进行安装即可

![img-06](assets/CUDA安装教程/img-06.jpg)

![img-07](assets/CUDA安装教程/img-07.jpg)

![img-08](assets/CUDA安装教程/img-08.jpg)

![img-09](assets/CUDA安装教程/img-09.jpg)

![img-10](assets/CUDA安装教程/img-10.jpg)

![img-11](assets/CUDA安装教程/img-11.jpg)

![img-12](assets/CUDA安装教程/img-12.jpg)

![img-13](assets/CUDA安装教程/img-13.jpg)

![img-14](assets/CUDA安装教程/img-14.jpg)

![img-15](assets/CUDA安装教程/img-15.jpg)

![img-16](assets/CUDA安装教程/img-16.jpg)

![img-17](assets/CUDA安装教程/img-17.jpg)

## 1.4 配置环境

 打开 设置->高级系统设置->环境变量 

![img-18](assets/CUDA安装教程/img-18.png)

        红框里的是系统自动添加的，蓝框里的有些情况系统不会自动添加，需要手动添加，添加时注意自己的路径。

```cobol
NVCUDASAMPLES_ROOT  C:\ProgramData\NVIDIA Corporation\CUDA Samples\v11.6 NVCUDASAMPLES11_6_ROOT  C:\ProgramData\NVIDIA Corporation\CUDA Samples\v11.6
```

##  1.4 验证

 win+R，输入cmd，输入[nvcc](https://so.csdn.net/so/search?q=nvcc&spm=1001.2101.3001.7020) --version查看版本号，输入set cuda查看设置的环境变量

![img-19](assets/CUDA安装教程/img-19.png)

# 2 cuANN下载及安装 

## 2.1 cuDNN下载

 下载地址如下，下载之前需要注册一下  
[https://developer.nvidia.com/rdp/cudnn-download](https://developer.nvidia.com/rdp/cudnn-download "https://developer.nvidia.com/rdp/cudnn-download")

![img-20](assets/CUDA安装教程/img-20.png)

![img-21](assets/CUDA安装教程/img-21.png)

![img-22](assets/CUDA安装教程/img-22.png)

 如下链接，有适合自己的版本

[cuDNN Archive | NVIDIA Developer](https://developer.nvidia.com/rdp/cudnn-archive "cuDNN Archive | NVIDIA Developer")

![img-23](assets/CUDA安装教程/img-23.png)

## 2.2 cuDNN配置

将cuDNN解压到D盘

![img-24](assets/CUDA安装教程/img-24.png)

 将三个文件夹拷贝到到cuda的安装目录下。默认的安装路径为

```cobol
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.6
```

## 2.3 添加环境变量

```cobol
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.6\binC:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.6\includeC:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.6\libC:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.6\libnvvp
```

![img-25](assets/CUDA安装教程/img-25.png)

## 2.4 验证

       win+R cmd进入安装目录下，再进入到 extras\demo_suite下，执行.\bandwidthTest.exe和.\deviceQuery.exe，得到下图。

![img-26](assets/CUDA安装教程/img-26.png)

![img-27](assets/CUDA安装教程/img-27.png)

# 3 安装GPU版的torch（不需要torch的忽略）

当跑深度学习代码时，会出现如下错误，原因是原先安装的是GPU版本的torch。

![img-28](assets/CUDA安装教程/img-28.png)

## 3.1 安装GPU版torch

进入官网[Start Locally | PyTorch](https://pytorch.org/get-started/locally/#no-cuda-1 "Start Locally | PyTorch")

选择各配置，复制红线链接

![img-29](assets/CUDA安装教程/img-29.png)

![img-30](assets/CUDA安装教程/img-30.png)

打开torch和torchvision选择适合自己的版本

![img-31](assets/CUDA安装教程/img-31.png)

 进入该路径下执行pip

```cobol
pip install torch-1.12.1+cu116-cp38-cp38-win_amd64.whl pip install torchvision-0.13.1+cu116-cp38-cp38-win_amd64.whl
```

![img-32](assets/CUDA安装教程/img-32.png)

 ![img-33](assets/CUDA安装教程/img-33.png)

 cuda可以用，代码已经可以正常执行

![img-34](assets/CUDA安装教程/img-34.png)
