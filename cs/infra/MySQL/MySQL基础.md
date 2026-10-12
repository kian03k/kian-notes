---
tags: [MySQL, 数据库, SQL]
created: 2026-10-12
updated: 2026-10-12
status: ok
---

<font color=blue size=40 face="黑体">MySQL</font>

[TOC]

# 基础篇

## SQL基本概念

关系型数据库

|      | 关系型数据库 | 非关系型数据库 |
| :--: | :----------- | -------------- |
| 代表 | MySQL        | redis          |
|      |              |                |



## SQL

**utf8** occupies 3 bytes ,recommend to use **utf8mb4** foramt

DML:Data Manipulation Language 数据 操作语言/məˌnɪp.jəˈleɪ.ʃən/。Definition Query Control

### **DML**

```sql
[数据库操作 ]                                        
show databases;
select db();查看当前数据库                              
create db [if not exists] db_name [default charset ?][collate ?];
drop db [if exists] db_name;                                
use db_name;                                            
[数据表操作]                                                 
show tables;                                                
desc tb_name; describle                                    
show create table tb_name ;                                  
create table tb_name();                                      
alter table tb_n add 字段名 类型（长度）[comment][约束]； 
alter table tb_n modify 字段名 新数据类型（长度）;       
alter table tb_n change 旧字段名 新名 类型 [comment] [约束]; 
alter table tb_n drop 字段名；                           
alter table tb_n rename to 新字段名；                    
drop table [if exists] 表名；                               
truncate table 表名；删除指定表，并新建该表。                
```

```sql
create table tb_name(
    字段1 字段1类型[comment '注释']，
    id int comment '编号'，
    字段2 字段2类型[comment '注释']
) comment ’user_table‘;[comment 可省略]
```

### **DDL**

```sql
insert into tb_n (字段名1，字段名2，...)values(值1，值2，...);
insert into  tb_n values (值1，值2，...);
insert into tb_na (字段名1，字段名2，...)values(值1，值2，...),(值1，值2，...),(值1，值2，...);
insert into tb_na values (值1，值2，...),(值1，值2，...),(值1，值2，...);
update tb_na set 字段名1=value1，字段名2=val2,...[where 条件];
delete from tb_na [where 条件];
```

### **DQL**

```sql
select 字段列表			   4
from 表名列表  			   1（dql的执行顺序，用别名验证）
where 条件列表			   2
group by 分组字段列表		  3	
having 分组后条件列表
order by 排序字段列表		  5
limit 分页参数			    6
```

```sql
select 字段1，字段2,...from 表名；
select * from 表名；
select 字段1 [as 别名]，字段2[as 别名2]... from 表名；
select distinct 字段列表 from tb_na; 去除重复数据
```

```sql
比较运算符：>,<,<=,,>=,=,<>/!=,between...and...[包含最大最小值],in(...)[在in之后的列表中的值，多选1],like 占位符[模糊匹配,_匹配单个字符，%匹配任意个字符],is null,
逻辑运算符：and/&&,or/||,not/!
年龄在18或20或22： where age in(18,20,22);use by or
名字为2个字的人： where name like '__';
身份证最后一位为X： where idcard like '%X';
```

| 聚合函数 | 功能     |
| -------- | -------- |
| count    | 统计数量 |
| max      | 最大值   |
| min      | 最小值   |
| avg      | 平均值   |
| sum      | 求和     |

```sql
select 聚合函数（字段列表）from 表名；
select count（*）from tb_na；
null 不参与聚合运算

select 字段列表 from tb_na [where ]group by 分组字段名 [having ];
where :分组前过滤，不会聚合函数判断。having反之。

select gender，count(*）from tb_na group by gender;查询男女人数
女 7
男 9
查询年龄<45,并且按照地址分组，输出员工数>=3的地址。                    
select address ,count (*) from tb_na where age<45 group by address having count(*)>=3;
别名使用：
select address ,count (*) address_ count from tb_na where age<45 group by address having address_ count>=3; 
```

```sql
select 字段列表 from tb_na order by 字段1 排序方式1，字段2，排序方式2；
asc:升序（默认）ascending order
desc:降序      descending oeder

select * from tb_na order by age asc , time1 desc; 先按照年龄升序，再按照时间降序。
```

~~~sql
select 字段列表 from tb_na limit 起始索引【（页码-1）*每页记录数】，查询记录数；
（DBMS不互通,limit为mysql）
select * from tb_na limit 0，10;查询第一页，每页数据量为10，0可省略.
select * from tb_na limit 10,10;查询第二页，每页数据量为10.
~~~

~~~sql
查询前n条数据
sqlserver支持top关键字
select top 5 * from table;// 返回前5行数据
Oracle需要使用rownum。
select * from table where rownum<=5; //返回前5条数据
mysql支持limit，只能适用于mysql。limit子句用于强制select语句返回置顶的记录数，接受一个或两个数字参数，必须是整数常量。一个参数是返回前几条记录；两个参数时，第一个参数指定第一个返回记录行的偏移量（初始记录行的偏移量是0），第二个参数指定返回记录的最大数目。
一个参数：select * from table limit 10; //返回前10行记录
两个参数：select * from table limit 5,10; //返回第6-15行的记录
select * from table limit 5,-1; //返回第6行到最后一行的记录（从某一个偏移量到记录集的结束所有的记录行，可以指定第二个参数为 -1）
select * from table limit 0,10 //返回前10行记录，和limit10的结果一样，即limit0,n=limit n
~~~



### **DCL**

```sql
管理数据库用户的访问权限
用户管理
use mysql;select * from user;查询用户
create user '用户名'@'主机名' identified by 'password';创建用户
alter user '用户名'@'主机名' identified with mysql_native_password by 'new_pwd';
drop user '用户名'@'主机名';

create user 'u1'@'localhost' identified by '123456';
create user 'u2'@'%' identified by '123456';可以在任意主机访问的账户
```

| 权限               | 说明               |
| ------------------ | ------------------ |
| all,all privileges | 所有权限           |
| select             | 查询数据           |
| insert             | 插入数据           |
| update             | 修改数据           |
| delete             | 删除数据           |
| alter              | 修改表             |
| drop               | 删除数据库/表/视图 |
| create             | 创建数据库/表      |

~~~sql
show grants for '用户名'@'主机名';
grant 权限列表 on 数据库名.表名 to '用户名'@'主机名';    *.*表示所有数据库的权限
revoke 权限列表 on 数据库名.表名 from '用户名'@'主机名';
~~~


### 数据类型
#### 数值类型

| 类型        | byte       | 描述                         |
| ----------- | ---------- | ---------------------------- |
| tinyint     | 1          | （-128，127）/（0，255）     |
| smallint    | 2          | (-32768，32767) / (0，65535) |
| mediumint   | 3          |                              |
| int/integer | 4          |                              |
| bigint      | 8          |                              |
| float       | 4          | 单精度浮点数值               |
| double      | 8          | 双精度浮点数值               |
| decimal     | 由M和D决定 | 小数值（精确定点数）         |

~~~
age TINYINT UNSIGNED(unsigned表示使用无符号数)；
score double(4,1),4表示整体长度，1为小数位数；
M（精度），D（标度）
~~~

#### 字符串类型

| 类型       | 大小                  | 描述                         |
| ---------- | --------------------- | ---------------------------- |
| CHAR       | 0-255 bytes           | 定长字符串                   |
| VARCHAR    | 0-65535 bytes         | 变长字符串                   |
| TINYBLOB   | 0-255 bytes           | 不超过255个字符的二进制数据  |
| TINYTEXT   | 0-255 bytes           | 短文本字符串                 |
| BLOB       | 0-65 535 bytes        | 二进制形式的长文本数据       |
| TEXT       | 0-65 535 bytes        | 长文本数据                   |
| MEDIUMBLOB | 0-16 777 215 bytes    | 二进制形式的中等长度文本数据 |
| MEDIUMTEXT | 0-16 777 215 bytes    | 中等长度文本数据             |
| LONGBLOB   | 0-4 294 967 295 bytes | 二进制形式的极大文本数据     |
| LONGTEXT   | 0-4 294 967 295 bytes | 极大文本数据                 |

~~~
char(10) -----------> 性能好	用户名  username  varchar(50)
varchar(10) ---------> 性能较差	性别  gender  char(1)
~~~

####  日期类型

| 类型      | 大小 | 范围                                       | 格式                | 描述                     |
| --------- | ---- | ------------------------------------------ | ------------------- | ------------------------ |
| DATE      | 3    | 1000-01-01 至 9999-12-31                   | YYYY-MM-DD          | 日期值                   |
| TIME      | 3    | -838:59:59 至 838:59:59                    | HH:MM:SS            | 时间值或持续时间         |
| YEAR      | 1    | 1901 至 2155                               | YYYY                | 年份值                   |
| DATETIME  | 8    | 1000-01-01 00:00:00 至 9999-12-31 23:59:59 | YYYY-MM-DD HH:MM:SS | 混合日期和时间值         |
| TIMESTAMP | 4    | 1970-01-01 00:00:01 至 2038-01-19 03:14:07 | YYYY-MM-DD HH:MM:SS | 混合日期和时间值，时间戳 |

## 函数

一段可以直接被另一段程序调用的程序或代码（MySQL中已经内置）

#### 字符串函数

| **函数**                 | 功能                                                      |
| ------------------------ | --------------------------------------------------------- |
| concat(S1,S2,...Sn)      | 字符串拼接，将S1，S2，... Sn拼接成一个字符串              |
| lower(str)               | 将字符串str全部转为小写                                   |
| upper(str)               | 将字符串str全部转为大写                                   |
| LPAD(str,n,pad)          | 左填充，用字符串pad对str的左边进行填充，达到n个字符串长度 |
| RPAD(str,n,pad)          | 右填充，用字符串pad对str的右边进行填充，达到n个字符串长度 |
| TRIM(str)                | 去掉字符串头部和尾部的空格                                |
| substring(str,start,len) | 返回从字符串str从start位置起的len个长度的字符串           |

```sql
select concat('hello','mysql');   hellomysql
select lpad('01',5,'-');           ---01
select substring('hello mysql',1,5); hello
update tb_na set id1=lpad(id1,5,'0');  id 扩展到5位，不足前面补0.
```

#### 数值函数

| 函数       | 功能                               |
| ---------- | ---------------------------------- |
| ceil(x)    | 向上取整                           |
| floor(x)   | 向下取整                           |
| mod(x,y)   | 返回x/y的模                        |
| rand()     | 返回0~1内的随机数                  |
| round(x,y) | 求参数x的四舍五入的值，保留y位小数 |
|            |                                    |

~~~sql
生成6位随机数
select lpad(round(rand()*1000000,0),6,'0');
~~~



#### 日期函数

| **函数**                           | 功能                                              |
| ---------------------------------- | ------------------------------------------------- |
| curdate()                          | 返回当前日期                                      |
| curtime()                          | 返回当前时间                                      |
| NOW()                              | 返回当前日期和时间                                |
| YEAR(date)                         | 获取指定date的年份                                |
| MONTH(date)                        | 获取指定date的月份                                |
| DAY(date)                          | 获取指定date的日期                                |
| DATE_ADD(date, INTERVAL expr type) | 返回一个日期/时间值加上一个时间间隔expr后的时间值 |
| DATEDIFF(date1,date2)              | 返回起始时间date1 和 结束时间date2之间的天数      |
|                                    |                                                   |

```sql
select date_add(now(),interval 70 day/month/year);当前时间后70天/月/年的时间。
select datediff('2021-10-01','2021-12-01');  -61  可以返回负数
查询员工入职天数，并按照天数倒叙排序
select name,datediff（curdate(),entrydate) as 'b1' from tb_na order by b1 desc;
```



#### 流程函数

| 函数                                                         | 功能                                                      |
| ------------------------------------------------------------ | --------------------------------------------------------- |
| IF(value , t , f)                                            | 如果value为true，则返回t，否则返回f                       |
| IFNULL(value1 , value2)                                      | 如果value1不为空，返回value1，否则返回value2              |
| case when [ val1 ] then [res1] ...else [ default ] END       | 如果val1为true，返回res1，... 否则返回default默认值       |
| CASE [ expr ] WHEN [ val1 ] THEN [res1] ... ELSE [ default ] END | 如果expr的值等于val1，返回res1，... 否则返回default默认值 |

~~~sql
select if (true, 'aaa','bbb');
select ifnull('aaa','bbb'); aaa
select ifnull('','bbb');    返回空字符串，不会返回bbb
select ifnull(null,'bbb');  bbb
查询员工姓名，地址，北京/上海返回一线城市，其他返回二线城市
select
	name,
	case address when '北京' then '一线城市' when'上海' then '一线城市' else '二线城市'
from tb_na;
~~~

## 约束

作用于表中字段上的规则，用于限制存储在表中的数据。

~~~sql
not null      限制该字段的数据不能为null
unique        保证该字段的所有数据都是唯一、不重复的
primary key   主键是一行数据的唯一标识，要求非空且唯一
default       保存数据时，如果未指定该字段的值，则采用默认值
check         保证字段值满足某一个条件(8.0.16版本之后)
foreign key   用来让两张表的数据之间建立连接，保证数据的一致性和完整性
~~~

~~~sql
alter table tb_na add constraint 外键名称 foreign key(外键字段名) references 主表（主列表名）;
alter table 表名 drop foreign key 外键名称；
~~~



| 行为        | 说明                                                         |
| ----------- | ------------------------------------------------------------ |
| NO ACTION   | 当在父表中删除/更新对应记录时，首先检查该记录是否有对应外键，如果有则不 允许删除/更新。 (与 RESTRICT 一致) 默认行为 |
| RESTRICT    | 当在父表中删除/更新对应记录时，首先检查该记录是否有对应外键，如果有则不 允许删除/更新。 (与 NO ACTION 一致) 默认行为 |
| CASCADE     | 当在父表中删除/更新对应记录时，首先检查该记录是否有对应外键，如果有，则 也删除/更新外键在子表中的记录。 |
| SET NULL    | 当在父表中删除对应记录时，首先检查该记录是否有对应外键，如果有则设置子表 中该外键值为null（这就要求该外键允许取null）。 |
| SET DEFAULT | 父表有变更时，子表将外键列设置成一个默认的值 (Innodb不支持)  |

  ~~~sql
  alter table tb_na add constraint 外键名称 foreign key(外键字段名) references 主表（主列表名）on update cascade on delete cascade;
  ~~~

## 多表查询

~~~sql
select * from tb_1,tb_2; 笛卡尔积
select * from tb_1,tb_2 where tb1.id=tb2.id;
~~~

### 连接查询 

内连接：相当于查询A、B交集部分数据 

外连接： 

​		左外连接：查询左表所有数据，以及两张表交集部分数据 

​		右外连接：查询右表所有数据，以及两张表交集部分数据 

自连接：当前表与自身的连接查询，自连接必须使用表别名

~~~sql
隐式内连接
select 字段列表 from 表1，表2 where 条件；
显示外连接
select 字段列表 from 表1 [inner] join 表2 on 连接条件；

查询员工姓名，部门名称，一对一的多表。
select b.name,d.id from base b,detail d where b.d_id=d.id;
select b.name,d.id from base b inner join detail d on b.d_id =d.id;
~~~

~~~sql
左外连接
SELECT 字段列表 FROM 表1 LEFT [ OUTER ] JOIN 表2 ON 条件 ... ; 
右外连接(可自由转为左外)
SELECT 字段列表 FROM 表1 RIGHT [ OUTER ] JOIN 表2 ON 条件 ... ;

查询员工姓名，部门名称(相比内连接，会查询到如员工目前未划分部门情况下的员工信息)
select b.name,d.id from base b left outer join detail d on b.d_id =d.id;
查询部门表的全部信息，和对应员工信息
select d.*，b.* from base b right outer join detail d on b.d_id =d.id;
~~~

~~~sql
自连接
SELECT 字段列表 FROM 表A 别名A JOIN 表A 别名B ON 条件 ... ;

查询员工姓名及其领导姓名
select a.name,b.name from base a, base b where a.manager_id=b.id;
如果员工没有领导也查询出来
select a.name b.name from base a left join base b on a.manager_id=b.id;
~~~

### 联合查询

对于union查询，就是把多次查询的结果合并起来，形成一个新的查询结果集。

~~~sql
SELECT 字段列表 FROM 表A ...
UNION [ ALL ]
SELECT 字段列表 FROM 表B ....;
~~~




# 问题合集

[mysql8.0 ERROR 1045 (28000): Access denied for user ‘ODBC‘@‘localhost‘ (using password: NO)_error 1045 (28000): access denied for user 'odbc'](https://blog.csdn.net/m0_47505062/article/details/122342121)

