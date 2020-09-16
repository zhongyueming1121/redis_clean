# redis_clean
Find and clean up keys that have not been accessed for a long time in Redis

查找并清理Redis中长时间没有访问的键

使用scan命令步进遍历所有的key，找出上次Redis重启以来，大于N秒没有访问的key，写入文件中。

在项目中可以用来检查哪些key是没有设置过期时间或者过期时间过长导致无必要积压的。
使用object idletime 获取key空转时间。

支持从文件中读取，通过管道删除文件中包含的key。

说明：

必须配置maxmemory 和 maxmemory-policy，否则整数value中使用共享整数对象[0-10000]时，会使idletime互相关联，导致查找不准确。
