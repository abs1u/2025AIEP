user_count=$(ps -eo user,comm | awk '
BEGIN {
    # 将字段分隔符设置为空格
    FS=" "
    # 忽略大小写
    IGNORECASE=1
}
# 匹配以python开头的命令
$2 ~ /^python/ {
    # 打印用户名
    print $1
}' | sort | uniq | wc -l)

# 输出结果
echo $user_count