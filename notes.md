# Flask笔记

## 创建虚拟环境

* windows：

`py -3 -m venv venv`

* else：

`python3 -m venv venv`



## 进入虚拟环境

* windows:

`venv\Scripts\activate`

* else:

`. venv/bin/activate`

---

## 导出 FLASK_APP 环境变量

* powershell:

`$env:FLASK_APP = "hello.py"`

* cmd:

`set FLASK_APP=flaskr`

* else:

`export FLASK_APP=flaskr`

---

## 运行应用

`flask run`

`python -m flask run`

`python -m flask run --host=0.0.0.0`

---

## 开启调试模式

* powershell：

`$env:FLASK_ENV="development"`

* cmd:

`set FLASK_ENV=development`

* else:

`export FLASK_ENV=development`

这样可以实现以下功能：

* 激活调试器。

* 激活自动重载。

* 打开 Flask 应用的调试模式。

---

## 开启发开模式

`$env:FLASK_ENV="production"`

---
