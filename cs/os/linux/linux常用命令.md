---
tags: []
created: 2026-04-22
updated: 2026-04-22
status: ok
---

关闭服务进程  
sudo fuser -k 5000/tcp

/tmp 临时目录  
系统重启、会话断开（如 VS Code 重连）都会自动清空 /tmp —— 重进后看不到之前的安装包不是误删，是机制如此。
