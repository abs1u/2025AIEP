# 所有进程列表
ps aux > all_process.txt

# 找到python进程
awk 'tolower($11) ~ /^python/' all_process.txt > python_process.txt

# 提取用户名，去重
awk '{print $1}' python_process.txt | sort | uniq > python_users.txt

# 统计
count=$(wc -l < python_users.txt)

# 输出
echo $count