#!/usr/bin/env bash
# 我们课上已经实践过了ssh命令，这里我们熟悉一下scp命令
# 实验：scp 批量下载 → 本地按后缀归类 → 打包上传到远端“组名”目录
# 实验目的
# 会用 scp：把服务器的/data/shenzm/workshop路径下的所有文件拉到本地。
# 会用 mkdir/mv/find/tar：按照后缀把文件分门别类，再整体打包。
# 会用 ssh + scp：把打好的包传回远端自己组名的目录（若目录不存在就创建）。
# 实验要求（一步步）
# 远端（目标服务器）上已有一堆文件，后缀包含 .a、.b、.c（可能数量不一样）。
# 把它们都下载到你本机一个工作目录（比如 work/），注意 scp 通配符写法：要让远端来匹配，防止本地提前展开。
# 在本地 work/ 里新建 a/ b/ c/ 三个文件夹，把 .a → a/，.b → b/，.c → c/。
# 把 a/ b/ c/ 三个文件夹一起打包成 abc_<你的组名>.tar.gz。
# 在远端提交目录下创建你们组名的文件夹（比如 /data/submit/<你的组名>/），把 tar 包上传到那里。
# 输出每一步的提示信息；如果某类后缀一个都没有，也要友好提示，但流程继续进行。

# 题目：scp 下载 .a/.b/.c → 本地按后缀归类 → 打包上传到远端组名目录
# 目的：
# - 从远端把/data/shenzm/workshop路径下的三类后缀文件拉回本地；
# - 在本地分三类存放；
# - 打一个总包；
# - 再把包传回远端你们组名目录。
# 只用 bash 基础命令 + scp + ssh + tar。

#!/usr/bin/env bash
# 题目：scp 下载 .a/.b/.c → 本地按后缀归类 → 打包上传到远端组名目录



# TODO: 使用mkdir命令创建本地目录
echo "创建本地工作目录: /work"
mkdir work
# TODO: 使用cd命令进入本地目录
cd work

# TODO: 远端 → 本地下载（让远端匹配通配符，故把远端路径整体加引号）
# scp（远端 → 本地） 
# 注意：1. scp下载过程中可以使用正则表达式表示文件，请查询如何基于后缀写对应文件正则
# 注意：2. scp命令基于ssh，也需要考虑访问端口
# 参考 scp <user>@<host>:<remote_path> <local_dest_dir>/
echo "从远程服务器下载文件..."
scp -P 20205 "gpu-user10@10.214.242.192:/data/shenzm/workshop/*.a" . 2>/dev/null || echo "没有 .a 文件"
scp -P 20205 "gpu-user10@10.214.242.192:/data/shenzm/workshop/*.b" . 2>/dev/null || echo "没有 .b 文件"
scp -P 20205 "gpu-user10@10.214.242.192:/data/shenzm/workshop/*.c" . 2>/dev/null || echo "没有 .c 文件"
echo "下载完成"

# 本地创建分类目录
mkdir a
mkdir b
mkdir c

# TODO: 本地按后缀归类，将所有的.a/.b/.c文件分别移动到对应目录
# 参考 mv work/downloads/*.a a/
mv *.a a/
mv *.b b/
mv *.c c/
echo "文件分类完成"

# TODO: 打包（注意用 -C 避免把绝对路径打进包内）
# 参考 tar -czf <output.tar.gz> -C <work_dir> <item1> <item2> ...
tar -czf ly_3240104515.tar.gz -C . a b c
echo "打包完成"

# TODO: scp（本地 → 远端）
# scp <local_path_of_file> "<user>@<host>:<remote_dest_dir>/"
scp -P 20205 ly_3240104515.tar.gz "gpu-user10@10.214.242.192:/home/shenzm/workspace/home/gpu-user10/"
echo "上传完成"







