# Conda 环境管理与开发配置最佳实践（精简留存版）
本文档为**通用、稳定、可长期复用**的 Conda 环境配置规范，适用于 Web 开发、数据分析、深度学习，彻底解决环境冲突、臃肿、损坏问题，所有命令可直接复制执行。

## 一、核心原则：4 个通用环境搞定所有开发
**永远只维护 3~4 个通用环境**，不按项目创建环境，base 环境保持绝对干净，这是环境稳定的核心。

| 环境名称 | 用途 | 适用技术栈 |
|---------|------|-----------|
| base | 仅存放系统工具，不装任何项目依赖 | conda、pip、git 等工具 |
| web-dev | Web 后端开发通用 | Flask、Django、FastAPI |
| data | 数据分析/机器学习通用 | Pandas、Numpy、Jupyter |
| torch | 深度学习专用（可选） | PyTorch |

---

## 二、一键重装 Miniconda + 基础配置
适用于：环境损坏、重装系统、清理旧版 Anaconda/Miniconda

### 1. 彻底清理旧环境
```bash
# 删除安装目录
rm -rf ~/anaconda3 ~/miniconda3
# 删除配置文件
rm -rf ~/.condarc ~/.conda ~/.continuum
```

### 2. 安装 Miniconda（Linux 版）
```bash
# 下载安装包
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
# 执行安装
bash Miniconda3-latest-Linux-x86_64.sh
```
安装说明：
- 一路回车确认协议
- 安装路径默认即可
- 最后询问 `Do you wish the installer to initialize Miniconda3?` 输入 `yes`

### 3. 生效配置 + 基础优化
```bash
# 生效环境
source ~/.bashrc
# 关闭 base 自动激活（重要！保持环境干净）
conda config --set auto_activate false
```
验证：关闭终端重新打开，无 `(base)` 标识即为成功。

---

## 三、4 个通用环境一键创建命令
### 1. base 环境（默认）
**规则**：仅用于管理 conda，**绝对不安装** flask、pandas、torch 等任何项目依赖。
手动激活命令：
```bash
conda activate
```

### 2. web-dev 环境（Web 开发通用）
```bash
# 创建环境
conda create -n web-dev python=3.12 -y
# 激活环境
conda activate web-dev
# 安装通用依赖（所有 Web 项目通用）
pip install flask fastapi uvicorn requests python-dotenv pymysql psycopg2-binary flask-sqlalchemy flask-cors gunicorn
```

### 3. data 环境（数据分析/机器学习）
```bash
# 创建环境
conda create -n data python=3.14 -y
# 激活环境
conda activate data
# 安装科学计算依赖（conda 安装更稳定）
conda install pandas numpy matplotlib scikit-learn jupyter -y
```

### 4. torch 环境（深度学习，可选）
```bash
# 创建环境
conda create -n torch python=3.14 -y
# 激活环境
conda activate torch
# 安装 CPU 版 PyTorch
conda install pytorch torchvision torchaudio cpuonly -c pytorch -y
```

---

## 四、项目依赖隔离规范（关键）
通用环境共享依赖，**每个项目必须独立锁定版本**，避免互相污染：
```bash
# 进入项目目录
cd /home/你的用户名/项目文件夹

# 1. 生成项目依赖清单
pip freeze > requirements.txt

# 2. 新环境/新机器恢复依赖
pip install -r requirements.txt
```

---

## 五、核心概念：Conda 全家桶关系
| 名称 | 定义 | 体积 | 推荐场景 |
|------|------|------|----------|
| Conda | 跨语言包+环境管理器（比 pip 更强） | - | 所有开发 |
| Miniconda | Conda + 最小 Python 环境 | 100~150MB | **开发者首选（Web/数据分析/深度学习）** |
| Anaconda | Conda + 1000+预装数据分析库 | 5~6GB | 纯新手，不推荐开发者使用 |

✅ **结论**：所有开发场景**只用 Miniconda**，拒绝 Anaconda！

---

## 六、conda install vs pip install 用法指南
### 1. 核心区别
- **pip install**：Python 官方包管理器，安装 PyPI 仓库包，**Web 开发 100% 使用**
- **conda install**： Conda 专属管理器，自带系统底层依赖，**科学计算优先使用**

### 2. 混用规则
✅ **可以混用，官方推荐**
建议顺序：先 conda 安装，后 pip 安装

### 3. 必用 conda 安装的包（科学计算）
底层为 C/C++ 编写，pip 安装易缺失依赖、报错：
```text
pandas numpy scipy scikit-learn matplotlib seaborn pyarrow
```

### 4. 必用 pip 安装的包（Web 开发）
```text
flask django fastapi requests python-dotenv pymysql flask-cors
```

---

## 七、常用 Conda 命令速查
```bash
# 查看所有环境
conda env list

# 激活环境
conda activate 环境名

# 退出当前环境
conda deactivate

# 删除环境
conda remove -n 环境名 --all -y

# 导出环境备份
conda env export > environment.yml

# 从备份恢复环境
conda env create -f environment.yml
```

---

### 总结
1. **环境极简**：base(工具)+web-dev(Web)+data(数据分析)+torch(深度学习) 4 个环境足够
2. **base 净土**：绝不安装项目依赖，关闭自动激活
3. **安装分工**：Web 用 pip，科学计算用 conda
4. **项目隔离**：每个项目必须生成 `requirements.txt` 锁定依赖
5. **工具首选**：开发者只用 Miniconda，拒绝 Anaconda