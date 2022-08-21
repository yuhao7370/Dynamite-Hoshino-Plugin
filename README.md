# Dynamite-Hoshino-Plugin

适用于HoshinoBot的Dynamite(Explode)查分插件

项目地址：https://github.com/yuhao7370/Dynamite-Hoshino-Plugin

主播的b站：[yuhao7370](https://space.bilibili.com/275661582)

特别感谢[@Crazy___Bull](https://space.bilibili.com/335803482)提供的R值拟合公式以及[@Taskeren-3](https://space.bilibili.com/27656565)的Explode后端


**该插件不保证后续更新**

# 使用方法

1. 将该项目放在HoshinoBot插件目录 `modules` 下，或者clone本项目 `git clone https://github.com/yuhao7370/Dynamite-Hoshino-Plugin.git`
2. pip安装依赖，缺啥装啥就行，善用百度
3. 将插件文件夹改名为`Dynamite`并在`config/__bot__.py`模块列表中添加`Dynamite`
4. 解压res.zip

# 更新说明

**2022-8-21*

1. 添加了喵拜语音包功能

2. 添加了绑定功能

# 指令

| 指令              | 功能     | 可选参数              | 说明                            |
| :---------------- | :------- | :-------------------- | :------------------------------ |
| /dybind            | 绑定账号        |  [playerid]          | 绑定自己的账号(昵称)      |
| /dyb20            | 查询B20        |  [playerid]          | 查询自己的B20成绩(图片)      |
| /textdyb20        | 查询B20(文字版) |  [playerid]         | 查询自己的B20成绩(文字)      |
| /dyR        | 计算R值 |  [Rating acc] [Rating Perfect Good Miss]     | 通过定数+acc或者定数+误差计算R值     |
| /NyaBye130          | 发送喵拜语音包       |  [overdose]          | 随机发送喵拜语音包      |
