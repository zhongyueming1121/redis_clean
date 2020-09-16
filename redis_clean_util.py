# coding=utf-8
"""
Redis死键检查
@author: ymz
@date: 2019/07/10
"""
from redis.client import Redis
from redis.sentinel import Sentinel


def get_redis():
    """
    连接redis，返回Redis对象
    :return: 成功：返回redis对象
            失败：返回None
    """
    redis_mode = "0"
    print("redis run with mode:" + redis_mode)
    # 主从模式哨兵
    if redis_mode is "1":
        sentinel_host_list = []
        sentinel_host = "redis1.safedog.cn:26379,redis2.safedog.cn:26379,redis3.safedog.cn:26379"
        split = sentinel_host.split(",")
        for host_ip in split:
            sentinel_host_list.append(host_ip.split(':'))
        # 哨兵中定义的master的名称
        mymaster = "mymaster"
        # 密码
        password = "xxxxxxx"
        try:
            sentinel = Sentinel(sentinel_host_list, socket_timeout=0.5)
            return sentinel.master_for(mymaster, socket_timeout=0.5, password=password)
        except Exception as e:
            print("Redis sentinel connect error", e)
            return None

    # 单机模式
    if redis_mode is "0":
        redis_host_port = "redis.safedog.cn:6379"
        host_port_split = redis_host_port.split(':')
        ip = host_port_split[0]
        port = host_port_split[1]
        password = "xxxxxxx"
        try:
            print "ip,port,passport", ip, port, password
            return Redis(host=ip, port=port, db=0, password=password)
        except Exception as e:
            print("Redis connect error", e)
            return None


def check_redis():
    """
    检查redis
    将空转时间大于配置值（单位：秒）的key写入文件中
    :return:
    """
    # 最大空闲时间，单位：秒 30天 2592000
    max_idle_time = 2592000
    r = get_redis()
    it = 0
    f = open('dead_keys.txt', 'a')
    try:
        while True:
            # 每次步进5000个
            next_num, keys = r.scan(it, "*", 5000)
            it = next_num
            for key in keys:
                idletime = r.object("idletime", key)
                if long(max_idle_time) < long(idletime):
                    # print "key:" + key + "  idletime:" + str(idletime)
                    f.write(key)
                    f.write("\n")
            if next_num is None or next_num == 0L:
                break
    except Exception as e:
        print("check_redis error. %s" % e)


def del_keys(run_del):
    """
    从文件中读取key，然后删除，慎用
    :return:
    """
    if not run_del:
        print "not run del"
        return

    r = get_redis()
    pipeline = r.pipeline(transaction=False)
    i = 0
    f = open('dead_keys.txt', "r")
    try:
        for row_value in f.readlines():
            row_value = row_value.replace("\n", "")
            pipeline.delete(row_value)
            # 每5000个命令提交一下
            if i % 5000 == 0:
                pipeline.execute()
            i = i + 1
        pipeline.execute()
    except Exception as ex:
        print("del_keys error. %s" % ex)


if __name__ == "__main__":
    # 检查上次访问时间大于30天的键名
    check_redis()
    # 删除检测出的key
    # del_keys(False)
