# SQL Injection Keywords Reference

A comprehensive, categorized list of keywords, functions, operators, symbols, and identifiers commonly encountered in SQL injection contexts. This is a **keyword reference**, not a payload collection.

---

## 1. Special Characters & Symbols

```
'
"
;
,
.
(
)
[
]
{
}
@
@@
\
/
:
=
>
<
!
?
$
&
|
^
~
`
%
+
-
*
_
#
```

### Whitespace & Encoding Variants

```
%20      (URL-encoded space)
%09      (URL-encoded horizontal tab)
%0a      (URL-encoded line feed)
%0b      (URL-encoded vertical tab)
%0c      (URL-encoded form feed)
%0d      (URL-encoded carriage return)
%a0      (URL-encoded non-breaking space)
\t       (horizontal tab)
\n       (line feed)
\r       (carriage return)
\v       (vertical tab)
\f       (form feed)
\x0b     (vertical tab byte)
```

### Null & Other Control

```
%00      (null byte)
\0       (null byte)
\N       (null, MySQL specific)
```

---

## 2. Comment Styles

```
-- (double-dash, requires trailing space or control char: --%20)
--+
-- -
#
/**/
/*!*/           MySQL conditional / versioned comment
/*!50000*/      MySQL version-specific comment (e.g. 5.00.00+)
/*!50000SELECT*/
;%00            Null byte termination
`
``
```

---

## 3. Logical Operators

```
AND
&&
OR
||
NOT
!
XOR
```

---

## 4. Comparison Operators

```
=
>
<
>=
<=
<>  (not equal, SQL standard)
!=  (not equal)
!>  (not greater than)
!<  (not less than)
<=> (NULL-safe equal, MySQL)
LIKE
NOT LIKE
IN
NOT IN
BETWEEN
NOT BETWEEN
IS
IS NOT
IS NULL
IS NOT NULL
ISNULL
NOTNULL
EXISTS
NOT EXISTS
REGEXP
NOT REGEXP
RLIKE
NOT RLIKE
SOUNDS LIKE
SIMILAR TO
DISTINCT
ALL
ANY
SOME
```

---

## 5. Arithmetic & Bitwise Operators

### Arithmetic

```
+
-
*
/
%
MOD
DIV
```

### Bitwise

```
&       (AND)
|       (OR)
^       (XOR)
~       (NOT)
<<      (left shift)
>>      (right shift)
```

---

## 6. String Operators & Concatenation

```
||                          (ANSI concatenation)
CONCAT
CONCAT_WS
GROUP_CONCAT
+
```

---

## 7. Core SQL Keywords

```
SELECT
INSERT
UPDATE
DELETE
FROM
WHERE
AS
SET
VALUES
INTO
CREATE
ALTER
DROP
TRUNCATE
RENAME
REPLACE
MERGE
UPSERT
EXEC
EXECUTE
CALL
DO
HANDLER
LOAD
LOAD DATA
LOAD FILE
DUMPFILE
OUTFILE
IMPORT
EXPORT
BULK
BACKUP
RESTORE
USE
SHOW
DESCRIBE
DESC
EXPLAIN
ANALYZE
CHECK
REPAIR
OPTIMIZE
FLUSH
RESET
PURGE
KILL
SHUTDOWN
GRANT
REVOKE
DENY
COMMIT
ROLLBACK
SAVEPOINT
BEGIN
START TRANSACTION
LOCK
UNLOCK
PREPARE
DEALLOCATE
SIGNAL
RESIGNAL
GET DIAGNOSTICS
RETURNING
DEFAULT
CHECK
CONSTRAINT
PRIMARY KEY
FOREIGN KEY
REFERENCES
INDEX
KEY
UNIQUE
FULLTEXT
SPATIAL
AUTO_INCREMENT
IDENTITY
SERIAL
ENGINE
STORAGE
PARTITION
TABLESPACE
VIEW
MATERIALIZED VIEW
TRIGGER
PROCEDURE
FUNCTION
ROUTINE
EVENT
SCHEDULE
CURSOR
DECLARE
OPEN
FETCH
CLOSE
TEMPORARY
TEMPORARY TABLE
GLOBAL
SESSION
LOCAL
```

---

## 8. UNION / JOIN Related

```
UNION
UNION ALL
UNION DISTINCT
INTERSECT
INTERSECT ALL
EXCEPT
EXCEPT ALL
MINUS
JOIN
INNER JOIN
LEFT JOIN
LEFT OUTER JOIN
RIGHT JOIN
RIGHT OUTER JOIN
FULL JOIN
FULL OUTER JOIN
CROSS JOIN
NATURAL JOIN
STRAIGHT_JOIN
ON
USING
```

---

## 9. Subquery & Clause Keywords

```
WHERE
GROUP BY
ORDER BY
HAVING
LIMIT
OFFSET
FETCH
NEXT
ROWS
ONLY
TOP
PERCENT
ASC
DESC
ASCENDING
DESCENDING
WITH
WITH RECURSIVE
LATERAL
WINDOW
OVER
PARTITION BY
ROWNUM
ROW_NUMBER
RANK
DENSE_RANK
NTILE
LEAD
LAG
FIRST_VALUE
LAST_VALUE
NTH_VALUE
CUME_DIST
PERCENT_RANK
PERCENTILE_CONT
PERCENTILE_DISC
```

---

## 10. String Functions

### Character / ASCII

```
ASCII
CHAR
NCHAR
UNICODE
ORD
CHR
CHARINDEX
INSTR
LOCATE
POSITION
PATINDEX
```

### Concatenation

```
CONCAT
CONCAT_WS
GROUP_CONCAT
STRING_AGG
LISTAGG
WM_CONCAT
FOR XML PATH
STUFF
XMLAGG
```

### Case Conversion

```
UPPER
UCASE
LOWER
LCASE
INITCAP
```

### Length

```
LENGTH
LEN
CHAR_LENGTH
CHARACTER_LENGTH
BIT_LENGTH
OCTET_LENGTH
DATALENGTH
```

### Substring & Trimming

```
SUBSTR
SUBSTRING
SUBSTRING_INDEX
MID
LEFT
RIGHT
TRIM
LTRIM
RTRIM
LPAD
RPAD
SPACE
REPEAT
REVERSE
REPLACE
INSERT
TRANSLATE
OVERLAY
STR
SPLIT_PART
REGEXP_SUBSTR
REGEXP_REPLACE
REGEXP_INSTR
REGEXP_COUNT
REGEXP_LIKE
REGEXP_SPLIT_TO_TABLE
REGEXP_SPLIT_TO_ARRAY
REGEXP_MATCHES
```

### Search & Comparison

```
STRCMP
SOUNDEX
DIFFERENCE
LEVENSHTEIN
METAPHONE
DMETAPHONE
FIND_IN_SET
FIELD
ELT
LOCATE
POSITION
INSTR
LIKE
ILIKE
```

### Encoding / Conversion

```
HEX
UNHEX
BIN
OCT
CONV
TO_BASE64
FROM_BASE64
QUOTE
CHAR
FORMAT
PARSE
TRY_PARSE
TO_CHAR
TO_NCHAR
TO_NUMBER
TO_DATE
TO_TIMESTAMP
TO_CLOB
TO_BLOB
TO_LOB
RAWTOHEX
HEXTORAW
UTL_RAW.CAST_TO_VARCHAR2
UTL_RAW.CAST_TO_RAW
UTL_I18N.STRING_TO_RAW
UTL_I18N.RAW_TO_CHAR
UNISTR
ASCIISTR
COMPOSE
DECOMPOSE
NLSSORT
```

### XML / HTML

```
EXTRACTVALUE
UPDATEXML
XMLTYPE
SYS_XMLGEN
SYS_XMLAGG
DBMS_XMLGEN.GETXML
XMLTABLE
XMLQUERY
XMLCAST
XMLELEMENT
XMLFOREST
XMLAGG
XMLPARSE
XMLSERIALIZE
XMLCOMMENT
XMLPI
XMLROOT
PATH
XMLEXISTS
```

---

## 11. Numeric Functions

### Basic Math

```
ABS
CEIL
CEILING
FLOOR
ROUND
TRUNC
TRUNCATE
SIGN
MOD
DIV
POW
POWER
SQRT
EXP
LN
LOG
LOG10
LOG2
GREATEST
LEAST
```

### Trigonometric

```
SIN
COS
TAN
ASIN
ACOS
ATAN
ATAN2
COT
SINH
COSH
TANH
DEGREES
RADIANS
PI
```

### Random

```
RAND
RANDOM
NEWID
UUID
GEN_RANDOM_UUID
UUID_SHORT
SYS_GUID
```

---

## 12. Aggregate Functions

```
COUNT
SUM
AVG
MIN
MAX
GROUP_CONCAT
ARRAY_AGG
STRING_AGG
LISTAGG
JSON_ARRAYAGG
JSON_OBJECTAGG
STDDEV
STDDEV_POP
STDDEV_SAMP
VARIANCE
VAR_POP
VAR_SAMP
BIT_AND
BIT_OR
BIT_XOR
BOOL_AND
BOOL_OR
EVERY
SOME
CHECKSUM_AGG
MEDIAN
PERCENTILE_CONT
PERCENTILE_DISC
STATS_MODE
CORR
COVAR_POP
COVAR_SAMP
REGR_SLOPE
REGR_INTERCEPT
REGR_COUNT
REGR_R2
REGR_AVGX
REGR_AVGY
REGR_SXX
REGR_SYY
REGR_SXY
```

---

## 13. Conditional / Control Flow Functions

```
IF
IFNULL
NULLIF
COALESCE
NVL
NVL2
ISNULL
IS NULL
IS NOT NULL
CASE
WHEN
THEN
ELSE
END
DECODE
IIF
CHOOSE
GREATEST
LEAST
NULLIF
TYPE
SQLNULL
```

---

## 14. Date / Time Functions

```
NOW
CURRENT_DATE
CURRENT_TIME
CURRENT_TIMESTAMP
LOCALTIME
LOCALTIMESTAMP
SYSDATE
SYSTIMESTAMP
GETDATE
GETUTCDATE
UTC_DATE
UTC_TIME
UTC_TIMESTAMP
CURDATE
CURTIME
DATE
TIME
TIMESTAMP
YEAR
MONTH
DAY
DAYNAME
DAYOFMONTH
DAYOFWEEK
DAYOFYEAR
HOUR
MINUTE
SECOND
MICROSECOND
QUARTER
WEEK
WEEKDAY
WEEKOFYEAR
LAST_DAY
MAKEDATE
MAKETIME
DATE_FORMAT
TIME_FORMAT
STR_TO_DATE
TO_DATE
DATEADD
DATEDIFF
DATESUB
DATEPART
DATENAME
TIMEDIFF
TIMESTAMPADD
TIMESTAMPDIFF
FROM_UNIXTIME
UNIX_TIMESTAMP
FROM_DAYS
TO_DAYS
PERIOD_ADD
PERIOD_DIFF
EXTRACT
DATE_TRUNC
AGE
JUSTIFY_DAYS
JUSTIFY_HOURS
JUSTIFY_INTERVAL
CLOCK_TIMESTAMP
STATEMENT_TIMESTAMP
TRANSACTION_TIMESTAMP
PG_SLEEP
SLEEP
WAITFOR DELAY
DBMS_LOCK.SLEEP
DBMS_PIPE.RECEIVE_MESSAGE
```

---

## 15. Conversion / Cast Functions

```
CAST
CONVERT
CONVERT_TZ
TRY_CAST
TRY_CONVERT
TRY_PARSE
PARSE
STR
TO_NUMBER
TO_CHAR
TO_DATE
TO_TIMESTAMP
TO_CLOB
TO_BLOB
TO_NCLOB
TO_BINARY_FLOAT
TO_BINARY_DOUBLE
TO_DSINTERVAL
TO_YMINTERVAL
TO_SINGLE_BYTE
TO_MULTI_BYTE
NUMTODSINTERVAL
NUMTOYMINTERVAL
ASCIISTR
BIN_TO_NUM
CHARTOROWID
ROWIDTOCHAR
ROWIDTONCHAR
COMPOSE
DECOMPOSE
HEXTORAW
RAWTOHEX
RAWTONHEX
UNISTR
VSIZE
SET
ENUM
BINARY
VARBINARY
SIGNED
UNSIGNED
ZEROFILL
NATIONAL
VARYING
LARGE
PRECISION
DOUBLE PRECISION
REAL
FLOAT
INT
INTEGER
SMALLINT
TINYINT
MEDIUMINT
BIGINT
DECIMAL
NUMERIC
BIT
BOOLEAN
BOOL
CHAR
VARCHAR
NCHAR
NVARCHAR
TEXT
TINYTEXT
MEDIUMTEXT
LONGTEXT
BLOB
TINYBLOB
MEDIUMBLOB
LONGBLOB
DATE
DATETIME
TIMESTAMP
TIME
YEAR
JSON
XML
GEOMETRY
POINT
LINESTRING
POLYGON
SERIAL
BIGSERIAL
UUID
INTERVAL
MONEY
SMALLMONEY
UNIQUEIDENTIFIER
ROWVERSION
HIERARCHYID
SQL_VARIANT
IMAGE
NTEXT
```

---

## 16. Encoding / Encryption / Hashing Functions

```
MD5
SHA
SHA1
SHA2
SHA256
SHA384
SHA512
CRC32
AES_ENCRYPT
AES_DECRYPT
DES_ENCRYPT
DES_DECRYPT
ENCRYPT
DECRYPT
ENCODE
DECODE
PASSWORD
OLD_PASSWORD
COMPRESS
UNCOMPRESS
UNCOMPRESSED_LENGTH
UUID
UUID_SHORT
GEN_RANDOM_UUID
SYS_GUID
RANDOM_BYTES
PGP_SYM_ENCRYPT
PGP_SYM_DECRYPT
PGP_PUB_ENCRYPT
PGP_PUB_DECRYPT
PGP_KEY_ID
DIGEST
HMAC
HASHBYTES
CERT_ID
CERTENCODED
CERTPRIVATEKEY
PWDCOMPARE
PWDENCRYPT
SIGNBYCERT
SIGNBYASYMKEY
DECRYPTBYCERT
DECRYPTBYKEY
DECRYPTBYASYMKEY
ENCRYPTBYCERT
ENCRYPTBYKEY
ENCRYPTBYASYMKEY
KEY_ID
KEY_GUID
SYMKEYPROPERTY
```

---

## 17. Information / System Functions

```
VERSION
@@VERSION
@@VERSION_COMMENT
@@VERSION_COMPILE_MACHINE
@@VERSION_COMPILE_OS
SERVERPROPERTY
DATABASE
SCHEMA
DB_NAME
DB_ID
USER
CURRENT_USER
SYSTEM_USER
SESSION_USER
CURRENT_ROLE
USER_NAME
SUSER_NAME
SUSER_SNAME
SUSER_ID
HOST_NAME
APP_NAME
CONNECTION_ID
CONNECTION_ID()
LAST_INSERT_ID
@@IDENTITY
SCOPE_IDENTITY
IDENT_CURRENT
ROW_COUNT
FOUND_ROWS
SQL_CALC_FOUND_ROWS
LASTVAL
CURRVAL
NEXTVAL
OBJECT_ID
OBJECT_NAME
TYPE_ID
TYPE_NAME
COL_LENGTH
COL_NAME
INDEX_COL
DATABASEPROPERTYEX
FILE_ID
FILE_NAME
FILEGROUP_ID
FILEGROUP_NAME
FILEGROUPPROPERTY
FULLTEXTCATALOGPROPERTY
FULLTEXTSERVICEPROPERTY
ROWCOUNT_BIG
ERROR_NUMBER
ERROR_MESSAGE
ERROR_SEVERITY
ERROR_STATE
ERROR_LINE
ERROR_PROCEDURE
SQLCODE
SQLERRM
SQLSTATE
DIAGNOSTICS
@@ROWCOUNT
@@ERROR
@@TRANCOUNT
@@SPID
@@PROCID
@@CONNECTIONS
@@MAX_CONNECTIONS
@@CPU_BUSY
@@IDLE
@@IO_BUSY
@@PACK_RECEIVED
@@PACK_SENT
@@PACKET_ERRORS
@@TOTAL_READ
@@TOTAL_WRITE
@@TOTAL_ERRORS
@@TIMETICKS
@@DBTS
@@SERVERNAME
@@SERVICENAME
@@INSTANCENAME
@@LANGUAGE
@@LANGID
@@LOCK_TIMEOUT
@@MAX_PRECISION
@@NESTLEVEL
@@OPTIONS
@@REMSERVER
@@TEXTSIZE
@@DATEFIRST
@@CURSOR_ROWS
@@FETCH_STATUS
PROCESSLIST
SHOW PROCESSLIST
SHOW FULL PROCESSLIST
```

---

## 18. System Metadata Tables / Views

### MySQL / MariaDB

```
information_schema
information_schema.SCHEMATA
information_schema.TABLES
information_schema.COLUMNS
information_schema.VIEWS
information_schema.TRIGGERS
information_schema.ROUTINES
information_schema.EVENTS
information_schema.PARTITIONS
information_schema.STATISTICS
information_schema.TABLE_CONSTRAINTS
information_schema.KEY_COLUMN_USAGE
information_schema.REFERENTIAL_CONSTRAINTS
information_schema.CHECK_CONSTRAINTS
information_schema.USER_PRIVILEGES
information_schema.SCHEMA_PRIVILEGES
information_schema.TABLE_PRIVILEGES
information_schema.COLUMN_PRIVILEGES
information_schema.PROCESSLIST
information_schema.ENGINES
information_schema.PLUGINS
information_schema.FILES
information_schema.PARAMETERS
information_schema.PROFILING
information_schema.GLOBAL_VARIABLES
information_schema.SESSION_VARIABLES
information_schema.GLOBAL_STATUS
information_schema.SESSION_STATUS
information_schema.INNODB_BUFFER_PAGE
information_schema.INNODB_TRX
information_schema.INNODB_LOCKS
information_schema.INNODB_LOCK_WAITS
information_schema.INNODB_CMP
information_schema.INNODB_CMP_RESET
information_schema.INNODB_CMPMEM
information_schema.INNODB_CMPMEM_RESET
information_schema.INNODB_CMP_PER_INDEX
information_schema.INNODB_CMP_PER_INDEX_RESET
information_schema.INNODB_TABLESTATS
information_schema.INNODB_INDEX_STATS
information_schema.INNODB_FT_DEFAULT_STOPWORD
information_schema.INNODB_FT_DELETED
information_schema.INNODB_FT_INDEX_TABLE
information_schema.INNODB_FT_INDEX_CACHE
information_schema.INNODB_FT_CONFIG
information_schema.INNODB_FT_BEING_DELETED
information_schema.INNODB_METRICS
information_schema.INNODB_TEMP_TABLE_INFO
information_schema.INNODB_VIRTUAL

mysql
mysql.user
mysql.db
mysql.tables_priv
mysql.columns_priv
mysql.procs_priv
mysql.proxies_priv
mysql.general_log
mysql.slow_log

performance_schema
sys
sys.version
sys.schema_auto_increment_columns
sys.schema_index_statistics
sys.schema_object_overview
sys.schema_redundant_indexes
sys.schema_table_statistics
sys.schema_tables_with_full_table_scans
sys.schema_unused_indexes
sys.statements_with_errors_or_warnings
sys.statements_with_full_table_scans
sys.statements_with_runtimes_in_95th_percentile
sys.statements_with_sorting
sys.statements_with_temp_tables
sys.user_summary
sys.host_summary
```

### PostgreSQL

```
pg_catalog
pg_class
pg_attribute
pg_index
pg_namespace
pg_database
pg_tables
pg_views
pg_indexes
pg_roles
pg_user
pg_shadow
pg_group
pg_authid
pg_auth_members
pg_stat_activity
pg_stat_user_tables
pg_stat_user_indexes
pg_locks
pg_settings
pg_file_settings
pg_hba_file_rules
pg_available_extensions
pg_extension

information_schema.schemata
information_schema.tables
information_schema.columns
information_schema.views
information_schema.routines
information_schema.table_constraints
information_schema.key_column_usage
```

### Microsoft SQL Server

```
master
master..sysdatabases
master..syslogins
master..sysprocesses
master..sysservers
master..sysremotelogins
master..sysmessages
master..sysconfigures
sysobjects
syscolumns
systypes
sysusers
sysindexes
sysdatabases
sysprocesses
sysservers
sysremotelogins
sysperfinfo
sysfiles
sysfilegroups
sys.tables
sys.columns
sys.views
sys.procedures
sys.triggers
sys.indexes
sys.database_principals
sys.server_principals
sys.sql_logins
sys.database_permissions
sys.schemas
sys.parameters
sys.types
sys.assemblies
sys.certificates
sys.asymmetric_keys
sys.symmetric_keys
sys.credentials
sys.crypt_properties
sys.database_files
sys.fulltext_catalogs
sys.fulltext_indexes
msdb
tempdb
model
fn_my_permissions
fn_builtin_permissions
xp_cmdshell
xp_dirtree
xp_fileexist
xp_subdirs
xp_regread
xp_regwrite
xp_regdeletekey
xp_regdeletevalue
xp_regaddmultistring
xp_regremovemultistring
xp_enumgroups
xp_logininfo
xp_grantlogin
xp_revokelogin
xp_msver
sp_configure
sp_help
sp_helptext
sp_helpdb
sp_helpserver
sp_helplogins
sp_who
sp_who2
sp_executesql
sp_sqlexec
sp_oacreate
sp_oamethod
sp_oadestroy
sp_oagetproperty
sp_oasetproperty
sp_oageterrorinfo
sp_oastop
sp_addsrvrolemember
sp_dropsrvrolemember
sp_addrolemember
sp_droprolemember
sp_password
OPENROWSET
OPENQUERY
OPENDATASOURCE
BULK INSERT
xp_sendmail
sp_send_dbmail
sp_addmessage
sp_altermessage
fn_xe_file_target_read_file
```

### Oracle

```
dual
all_tables
all_tab_columns
all_views
all_tab_comments
all_col_comments
all_objects
all_procedures
all_source
all_triggers
all_users
all_sequences
all_synonyms
all_ind_columns
all_indexes
all_constraints
all_cons_columns
all_db_links
all_directories
all_errors
all_tab_privs
all_sys_privs
all_role_privs
all_java_classes
all_mviews
all_part_tables
all_part_key_columns
all_external_tables
all_clusters
all_types
all_type_attrs
all_type_methods

user_tables
user_tab_columns
user_objects
user_source
user_procedures
user_views
user_users
user_sequences
user_indexes
user_ind_columns
user_constraints
user_cons_columns
user_tab_privs
user_sys_privs
user_role_privs
user_triggers
user_errors
user_types
user_tab_comments
user_col_comments

dba_tables
dba_tab_columns
dba_objects
dba_users
dba_roles
dba_sys_privs
dba_tab_privs
dba_role_privs
dba_profiles
dba_data_files
dba_temp_files
dba_segments
dba_extents
dba_free_space
dba_directories
dba_source
dba_triggers
dba_views

v$version
v$instance
v$database
v$session
v$process
v$sql
v$sqlarea
v$sqltext
v$sqltext_with_newlines
v$parameter
v$system_parameter
v$spparameter
v$option
v$pwfile_users
v$tablespace
v$datafile
v$logfile
v$controlfile
v$fixed_table
gv$session
gv$sql
gv$instance
gv$database

sys
SYSTEM
CTXSYS
MDSYS
OLAPSYS
ORDSYS
WKSYS
WMSYS
XDB
DBSNMP
OUTLN
sys.user$
sys.obj$
sys.tab$
sys.col$
sys.source$
sys.procedure$
sys.trigger$
sys.v_$parameter
sys.x$ksppcv
ctxsys.drithsx
ctxsys.CTX_REPORT
utl_http
utl_file
utl_tcp
utl_smtp
utl_mail
dbms_lob
dbms_xmlquery
dbms_xmlgen
dbms_xmldom
dbms_xmlparser
dbms_xmlsave
dbms_assert
dbms_pipe
dbms_lock
dbms_ldap
dbms_java
dbms_java_test
dbms_scheduler
dbms_sql
dbms_utility
dbms_metadata
dbms_random
dbms_obfuscation_toolkit
dbms_crypto
dbms_network_acl_admin
owa_util
owa
htp
htf
```

### SQLite

```
sqlite_master
sqlite_temp_master
sqlite_sequence
sqlite_version
sqlite_source_id
```

---

## 19. Privilege / User / Role Related

```
GRANT
REVOKE
DENY
ADMIN
ADMIN OPTION
WITH GRANT OPTION
CREATE USER
ALTER USER
DROP USER
CREATE ROLE
ALTER ROLE
DROP ROLE
CREATE LOGIN
ALTER LOGIN
DROP LOGIN
IDENTIFIED BY
PASSWORD
SET PASSWORD
OLD_PASSWORD
AUTHENTICATION
AUTHID
CURRENT_USER
DEFINER
INVOKER
SQL SECURITY DEFINER
SQL SECURITY INVOKER
ROLE
ROLES
PRIVILEGES
ALL PRIVILEGES
SUPER
SUPERUSER
CREATEDB
CREATEROLE
CREATEUSER
LOGIN
NOLOGIN
INHERIT
NOINHERIT
REPLICATION
BYPASSRLS
CONNECT
RESOURCE
DBA
USAGE
SELECT
INSERT
UPDATE
DELETE
EXECUTE
ALTER
REFERENCES
INDEX
CREATE
DROP
TRIGGER
CREATE VIEW
SHOW VIEW
CREATE ROUTINE
ALTER ROUTINE
CREATE TABLESPACE
CREATE TEMPORARY TABLES
LOCK TABLES
FILE
PROCESS
RELOAD
REPLICATION CLIENT
REPLICATION SLAVE
SHOW DATABASES
SHUTDOWN
SUPER
EVENT
CREATE ROLE
DROP ROLE
BYPASS_RLS
ASSUME
ADMIN
IMPERSONATE
CONTROL
TAKE OWNERSHIP
VIEW DEFINITION
VIEW CHANGE TRACKING
VIEW SERVER STATE
VIEW DATABASE STATE
CONNECT SQL
ALTER TRACE
ALTER ANY
CREATE ANY
DROP ANY
EXECUTE ANY
sysadmin
securityadmin
serveradmin
setupadmin
processadmin
diskadmin
dbcreator
bulkadmin
public
db_owner
db_accessadmin
db_securityadmin
db_ddladmin
db_backupoperator
db_datareader
db_datawriter
db_denydatareader
db_denydatawriter
```

---

## 20. File / OS Interaction

```
LOAD_FILE
OUTFILE
DUMPFILE
INTO OUTFILE
INTO DUMPFILE
LOAD DATA INFILE
BULK INSERT
OPENROWSET(BULK)
OPENROWSET
OPENDATASOURCE
xp_cmdshell
xp_dirtree
xp_fileexist
xp_subdirs
sp_oacreate
sp_oagetproperty
sp_oamethod
OACreate
utl_file
DBMS_LOB
UTL_FILE.FOPEN
UTL_FILE.GET_LINE
UTL_FILE.PUT_LINE
UTL_FILE.FCLOSE
utl_http
utl_tcp
HTTPURITYPE
DBUriType
XDBUriType
pg_read_file
pg_read_binary_file
pg_ls_dir
pg_ls_waldir
pg_ls_archive_statusdir
pg_stat_file
pg_read_file_old
pg_logdir_ls
COPY
\copy
sys_exec
sys_eval
sys_get
sys_set
readfile
writefile
editnote_source
```

---

## 21. XML Functions

```
EXTRACTVALUE
UPDATEXML
XMLTYPE
SYS_XMLGEN
SYS_XMLAGG
DBMS_XMLGEN
XMLTABLE
XMLQUERY
XMLCAST
XMLELEMENT
XMLFOREST
XMLAGG
XMLPARSE
XMLSERIALIZE
XMLCOMMENT
XMLPI
XMLROOT
XMLCONCAT
XMLExists
XMLCOLATTVAL
XMLSEQUENCE
XMLTRANSFORM
XMLPATCH
XMLDIFF
DEPTH
PATH
XMLNAMESPACES
XMLATTRIBUTES
.query
.value
.exist
.modify
.nodes
```

---

## 22. JSON Functions

```
JSON_EXTRACT
JSON_UNQUOTE
JSON_VALUE
JSON_QUERY
JSON_MODIFY
JSON_OBJECT
JSON_OBJECTAGG
JSON_ARRAY
JSON_ARRAYAGG
JSON_SET
JSON_INSERT
JSON_REPLACE
JSON_REMOVE
JSON_MERGE
JSON_MERGE_PATCH
JSON_MERGE_PRESERVE
JSON_DEPTH
JSON_LENGTH
JSON_KEYS
JSON_CONTAINS
JSON_CONTAINS_PATH
JSON_VALID
JSON_TYPE
JSON_PRETTY
JSON_STORAGE_SIZE
JSON_STORAGE_FREE
JSON_TABLE
ISJSON
JSON_SCHEMA_VALID
JSON_QUERY
jsonb
jsonb_extract_path
jsonb_extract_path_text
jsonb_set
jsonb_insert
jsonb_pretty
jsonb_strip_nulls
jsonb_build_object
jsonb_build_array
jsonb_object_keys
jsonb_each
jsonb_each_text
jsonb_array_elements
jsonb_array_elements_text
jsonb_typeof
jsonb_path_exists
jsonb_path_match
jsonb_path_query
jsonb_path_query_array
jsonb_path_query_first
to_json
to_jsonb
row_to_json
array_to_json
json_build_object
json_build_array
json_object_keys
json_each
json_each_text
json_array_elements
json_array_elements_text
```

---

## 23. Error-Based Injection Functions (Oracle)

```
CTXSYS.DRITHSX.SN
CTXSYS.CTX_REPORT.TOKEN_TYPE
UTL_INADDR.GET_HOST_NAME
UTL_INADDR.GET_HOST_ADDRESS
DBMS_UTILITY.FORMAT_ERROR_BACKTRACE
DBMS_UTILITY.SQLID_TO_SQLHASH
DBMS_UTILITY.GET_PARAMETER_VALUE
DBMS_UTILITY.GET_TIME
DBMS_UTILITY.COMPILE_SCHEMA
DBMS_UTILITY.ANALYZE_SCHEMA
DBMS_UTILITY.ANALYZE_DATABASE
DBMS_UTILITY.ANALYZE_PART_OBJECT
DBMS_UTILITY.EXPAND_SQL_TEXT
DBMS_XDB_VERSION.MAKEVERSIONED
DBMS_XDB_VERSION.CHECKIN
DBMS_XDB_VERSION.CHECKOUT
DBMS_XDB_VERSION.UNCHECKOUT
DBMS_XDB_CONFIG.GETSETTINGS
DBMS_XDB_VERSION.GETVERSION
DBMS_XDB_VERSION.GETPREDECESSORS
DBMS_XDB_VERSION.GETSUCCESSORS
DBMS_XDB.GETXDB_TABLESPACE
DBMS_XDB.ISXDBCONNECTED
DBMS_XDB.CFG_GET
DBMS_XDB.CFG_UPDATE
DBMS_XSLPROCESSOR.READ2CLOB
DBMS_XSLPROCESSOR.valueOf
DBMS_STREAMS.ADM_UTL.GET_SYS_HANDLER_SETTING
DBMS_STREAMS_AUTH.GRANT_ADMIN_PRIVILEGE
CTX_USER_DATA.CREATE_INDEX_SET
CTX_USER_DATA.ADD_ATTR
CTX_USER_DATA.SET_ATTRIBUTE
BANNER
BANNER_FULL
BANNER_LEGACY
```

---

## 24. Stored Procedures & Dynamic Execution

```
EXEC
EXECUTE
CALL
sp_executesql
PREPARE
EXECUTE IMMEDIATE
DEALLOCATE PREPARE
EXECUTE ... USING
EVAL
sys_exec
sys_eval
exec sp_executesql
DBMS_SQL.PARSE
DBMS_SQL.EXECUTE
DBMS_SQL.EXECUTE_AND_FETCH
DBMS_SQL.RETURN_RESULT
DBMS_SQL.TO_CURSOR_NUMBER
DBMS_SQL.TO_REFCURSOR
IMMEDIATE
```

---

## 25. Collation / Charset Keywords

```
COLLATE
COLLATION
CHARACTER SET
CHARSET
UTF8
UTF8MB4
LATIN1
ASCII
GBK
GB2312
BIG5
UCS2
UTF16
UTF32
BINARY
NOCASE
RTRIM
```

---

## 26. Miscellaneous Keywords & Constants

```
TRUE
FALSE
NULL
UNKNOWN
DEFAULT
AUTO_INCREMENT
CURRENT_USER
CURRENT_ROLE
SYSTEM_USER
SESSION_USER
USER
VERSION
@@global
@@session
@@local
@@GLOBAL
@@SESSION
@@LOCAL
@@sql_mode
@@datadir
@@basedir
@@tmpdir
@@hostname
@@hostname
@@port
@@socket
@@log_error
@@general_log_file
@@slow_query_log_file
@@plugin_dir
@@character_set_server
@@collation_server
@@innodb_data_home_dir
GLOBAL
SESSION
LOCAL
PERSIST
PERSIST_ONLY
READ UNCOMMITTED
READ COMMITTED
REPEATABLE READ
SERIALIZABLE
ISOLATION LEVEL
DEFERRABLE
NOT DEFERRABLE
INITIALLY DEFERRED
INITIALLY IMMEDIATE
FOR UPDATE
FOR SHARE
LOCK IN SHARE MODE
NOWAIT
SKIP LOCKED
WAIT
DISTINCTROW
HIGH_PRIORITY
LOW_PRIORITY
DELAYED
QUICK
IGNORE
FORCE
STRAIGHT_JOIN
SQL_BUFFER_RESULT
SQL_CACHE
SQL_NO_CACHE
SQL_CALC_FOUND_ROWS
SQL_SMALL_RESULT
SQL_BIG_RESULT
SQL_BUFFER_RESULT
ALL
DISTINCT
DISTINCTROW
TOP
LIMIT
OFFSET
FETCH FIRST
FETCH NEXT
WITH TIES
SAMPLE
TABLESAMPLE
BUCKETS
PERCENT
ROWS
RANGE
GROUPS
UNBOUNDED
PRECEDING
FOLLOWING
CURRENT ROW
FILTER
RECURSIVE
MATERIALIZED
NOT MATERIALIZED
LATERAL
PIVOT
UNPIVOT
CUBE
ROLLUP
GROUPING SETS
GROUPING
CROSS APPLY
OUTER APPLY
MERGE
MATCHED
NOT MATCHED
BY TARGET
BY SOURCE
OUTPUT
INSERTED
DELETED
INSTEAD OF
AFTER
BEFORE
FOR EACH ROW
FOR EACH STATEMENT
REFERENCING
OLD
NEW
TG_OP
TG_TABLE_NAME
TG_TABLE_SCHEMA
TG_NARGS
TG_ARGV
BODY
LANGUAGE
DETERMINISTIC
NOT DETERMINISTIC
CONTAINS SQL
NO SQL
READS SQL DATA
MODIFIES SQL DATA
RETURNS
RETURN
RETURNS NULL ON NULL INPUT
CALLED ON NULL INPUT
STRICT
IMMUTABLE
STABLE
VOLATILE
LEAKPROOF
COST
ROWS
PARALLEL
SAFE
UNSAFE
RESTRICTED
SECURITY DEFINER
SECURITY INVOKER
WINDOW
```

---

## 27. OOB (Out-of-Band) Channel Functions

```
utl_http.request
utl_http.request_pieces
HTTPURITYPE
DBUriType
utl_tcp
utl_smtp
utl_mail
utl_inaddr
DBMS_LDAP
OWA_UTIL
SYS.DBMS_LDAP.INIT
DNS
nslookup
ping
LOAD_FILE // UNC path for SMB
xp_dirtree // UNC path for SMB
xp_subdirs // UNC path for SMB
xp_fileexist // UNC path for SMB
OPENROWSET // UNC path
sp_oacreate
fn_xe_file_target_read_file
fn_get_audit_file
fn_trace_gettable
copy // PostgreSQL COPY from program
pg_read_file
pg_read_binary_file
```

---

## 28. Alternative Expression Keywords

```
CASE WHEN ... THEN ... ELSE ... END
IF(... , ... , ...)
IFNULL
NULLIF
COALESCE
NVL
NVL2
DECODE
IIF
CHOOSE
ELT
FIELD
FIND_IN_SET
INTERVAL
STRCMP
GREATEST
LEAST
ISNULL
IS NULL
IS NOT NULL
BETWEEN ... AND ...
NOT BETWEEN
IN (...)
EXISTS (...)
SOME (...)
ALL (...)
ANY (...)
(type) CAST
CONVERT(type, ...)
BINARY
COLLATE
DEFAULT
```

---

*This reference is intended for defensive research, authorized penetration testing, CTF competitions, and security education purposes only.*
