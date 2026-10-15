---
tags: [python, flask, web, ajax, pymysql, echarts, 接口]
created: 2026-10-15
updated: 2026-10-15
status: draft
source: D:/Projects/Python/old/Python/{flaskProject, py_home, homework, MyHTML, Project/flaskProject}
---

# Flask 入门：从 Hello World 到"前端 + 数据库 + 图表"全链路

> 原练习有 5~6 个 Flask 小项目，本质是同一条链路的反复打磨：**路由 → 请求 → 数据库 → JSON → 前端渲染**。
> 这里把它整理成一条"从零到能跑"的路线。前置：[[01-速查手册]]、[[03-面向对象]]。

---

## 0. 最小可运行骨架

```python
from flask import Flask

app = Flask(__name__)        # 创建应用

@app.route("/")              # 路由：访问 / 时执行下面的函数
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True)      # debug=True 改代码自动重启
```

---

## 1. 路由与请求取值

```python
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# 路径参数
@app.route("/user/<int:uid>")
def get_user(uid):
    return f"用户 {uid}"

# GET 查询串：/search?name=kian&page=1
@app.route("/search")
def search():
    name = request.args.get("name", "")
    page = int(request.args.get("page", 1))
    return f"{name} 第 {page} 页"

# POST 表单：request.values 同时兼容 form 和 args
@app.route("/ajax", methods=["GET", "POST"])
def ajax():
    name = request.values.get("name")
    age = request.values.get("age")
    return "success"

# POST JSON
@app.route("/api/add", methods=["POST"])
def api_add():
    info = request.get_json()        # 解析请求体 JSON
    return {"code": 20000, "data": info}
```

| 参数来源 | 取法 |
| --- | --- |
| URL 查询串 `?a=1` | `request.args.get("a")` |
| 表单 body | `request.form.get("a")` |
| 两者都要 | `request.values.get("a")` |
| JSON body | `request.get_json()` |
| 路径占位 `/u/<id>` | 函数参数 |

> ⚠️ `/u/<id>` 里 `id` 是 **str**，要数字就写 `<int:id>` 或手动 `int()`。

---

## 2. 返回：字符串 / 模板 / JSON

```python
@app.route("/text")
def text():
    return "纯文本"

@app.route("/page")
def page():
    return render_template("index.html", title="首页", items=[1, 2, 3])   # 渲染模板

@app.route("/api/users")
def api_users():
    users = [{"id": 1, "name": "kian"}]
    return jsonify(users)         # ★ 传数据给前端 ajax，必须返回 JSON
```

> 那句注释来自原始代码，值得记住：**"要把数据传输到 ajax 里，必须返回 json 类型的数据"**。
> Flask 1.1+ 里直接 `return dict` 也行，`jsonify` 更显式。

---

## 3. 模板 Jinja2（把数据填进 HTML）

`templates/index.html`：

```html
<h1>{{ title }}</h1>
<ul>
  {% for it in items %}
    <li>{{ it }}</li>
  {% endfor %}
</ul>
```

- `{{ 变量 }}` 输出值；`{% for %}` / `{% if %}` 写逻辑。
- 静态文件（js/css/img）放 `static/`，模板里用 `{{ url_for('static', filename='js/echarts.min.js') }}` 引用。

**标准目录结构**：

```
项目/
├── app.py            # 路由 + 视图
├── utils.py / my.py  # 数据访问层（查数据库）
├── templates/        # HTML 模板
│   └── index.html
├── static/           # js / css / 图片
│   ├── js/echarts.min.js
│   └── css/main.css
└── requirements.txt
```

---

## 4. 接数据库：pymysql 增删改查

**数据访问层**（`utils.py` / `Getdb.py`）：把连接与查询封装好，视图层只管调。

```python
import pymysql

def get_conn():
    conn = pymysql.connect(
        host="127.0.0.1", port=3306, user="root", password="***",
        database="hdsx", charset="utf8",
        cursorclass=pymysql.cursors.DictCursor,   # ★ 查出来是 dict，不是 tuple
    )
    return conn, conn.cursor()

def close(conn, cursor):
    cursor.close(); conn.close()

def query_all(table):
    conn, cur = get_conn()
    try:
        cur.execute(f"SELECT * FROM {table}")
        return cur.fetchall()
    finally:
        close(conn, cur)
```

**参数化查询（防注入，必须）**：

```python
sql = "SELECT * FROM student WHERE name=%s"     # %s 占位，不要用 f-string 拼
cur.execute(sql, (name,))                       # 参数用元组传
```

**增删改要 commit**：

```python
cur.execute("INSERT INTO student(name,age) VALUES(%s,%s)", (name, age))
conn.commit()                                   # ← 忘了就白改了
```

> `DictCursor` 让每行直接是字典，前端 JSON 化更顺——原项目几乎都这么用。
> 完整 CRUD 见 [[#6-综合实战学生管理系统]]。

---

## 5. 前后端联调：jQuery ajax + ECharts

**前端发请求（jQuery）**：

```html
<script src="{{ url_for('static', filename='js/jquery-3.4.1.min.js') }}"></script>
<script>
  $.ajax({
    url: "/api/users", type: "get", dataType: "json",
    success: function (res) {
      // res 就是后端 jsonify 出来的数据
      console.log(res);
    }
  });
</script>
```

**后端给图表喂数据，ECharts 画图**：

```python
@app.route("/get_content")
def get_content():
    res = query("SELECT ds, confirm FROM history")   # [(日期, 数值), ...]
    day  = [r[0].strftime("%m-%d") for r in res]
    data = [r[1] for r in res]
    return jsonify({"day": day, "data": data})       # 拆成两个数组给前端
```

```javascript
// 前端拿这两个数组直接贴进 ECharts 配置
option = {
  xAxis: { data: res.day },
  series: [{ type: "line", data: res.data }]
};
```

> 原 `MyHTML` / `flaskProject` 就是**疫情数据大屏**：Flask 从 `cov7` 库读 history/details，后端算好，前端 ECharts 出折线图 + 地图 + 表格。

---

## 6. 综合实战：学生管理系统

> 这是 `old/` 里**功能最完整**的一个（控制台版 + Web 版双形态），已整理迁移到 WSL：`~/workspace/demo/python/student-manage/`。

**控制台版**（`console_app.py`）：菜单循环 + 本地列表操作，退出时统一写回数据库。

```python
menu()                                   # 打印 1~7 项菜单
conn, cursor = get_conn()
student_list = read(conn, cursor)        # 从库读进内存列表
while True:
    num = int(input("请选择操作:"))
    get_season(num, student_list)        # 增/删/改/查/显示/排序/统计
    if num < 1:
        break
clear(conn, cursor)                      # 清空表
write(conn, cursor, student_list)        # 内存数据整体写回
close(conn, cursor)
```

**Web 版**（`app.py`）：前端表格 + ajax 增删改查，后端维护一个内存列表并同步落库。

```python
@app.route("/")
def index():
    global student_list
    conn, cursor = homework3.get_conn()
    student_list = homework3.read(conn, cursor)     # 读库填充内存
    return render_template("homework3.html")

@app.route("/insert", methods=["get", "post"])
def insert():
    id1 = int(request.values.get("id1"))
    student_list.append({"id": id1, "name": request.values.get("name1"), ...})
    return "success"

@app.route("/delete", methods=["get", "post"])
def delete():
    id2 = int(request.values.get("id2"))
    for i, item in enumerate(student_list):
        if item["id"] == id2:
            del student_list[i]; break
    return "success"

@app.route("/true", methods=["get", "post"])        # 提交：整表写回
def commit_all():
    conn, cursor = homework3.get_conn()
    homework3.clear(conn, cursor)
    homework3.write(conn, cursor, student_list)
    homework3.close(conn, cursor)
    return "success"
```

字段：`id / name / age / math`；功能：增、删、改、查、显示全部、**按成绩排序**、**最高/最低/平均分**。

**排序技巧**（原代码亮点）：

```python
new_list = [list(item.values()) for item in student_list]   # dict -> list
new_list.sort(key=lambda x: x[3], reverse=True)             # 按下标 3（math）排
```

---

## 7. 起步清单（新项目照着搭）

```bash
pip install flask pymysql flask-cors
```

```python
# app.py 顶部常备
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS          # 前后端分离时解决跨域
app = Flask(__name__)
CORS(app)                            # 允许跨域，Vue/React 前端才连得上
```

| 场景 | 关键点 |
| --- | --- |
| 只有页面 | `render_template` + Jinja2 |
| 给前端喂数据 | `jsonify` 返回 dict/list |
| 前后端分离 | `flask_cors` 开 CORS |
| 不要重启 | `app.run(debug=True)` |
| 上线 | 别用 `app.run`，用 `gunicorn`/`uwsgi` |

> **延伸**：`old/Flask/app.py`（390 行）是 WSL `music-platform/music-server-flask/` 的**早期练习版**——同一套"用户管理 + 菜单权限 + 数据看板"接口，后者已重构成 233 行 + JWT。想学"真实项目怎么组织 Flask 后端"，看那个更值。
