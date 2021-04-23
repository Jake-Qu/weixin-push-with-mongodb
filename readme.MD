# 微信模板消息推送使用Python MongoDB Redis

每两个小时获取一次token 使用另一个脚本，并且写入redis

推送脚本定期从mongodb数据库获取符合条件的数据并进行推送

添加了失败重试推送

添加了日志记录功能
