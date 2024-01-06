# Common SQL queries

```sql
CREATE ROLE <user_name> WITH CREATEDB LOGIN ENCRYPTED PASSWORD '<your_pasword>'; 
CREATE DATABASE <db_name> WITH OWNER '<user_name>' ENCODING 'utf8';

psql -h localhost -p <port_number> -U <user_name> <db_name>

SHOW search_path; 
SET search_path= translate;
```

```sql
-- Create Table
CREATE TABLE my_table (
	col_name1 datatype,
	col_name2 datatype
);
```

```sql
-- Create Table with integrity constraints 
-- applied to individual columns
CREATE TABLE my_table (
	col_name1 datatype NOT NULL,
	col_name2 datatype UNIQUE,
	col_name3 datatype NOT NULL PRIMARY,
	col_name4 datatype DEFAULT=' ',
	col_name5 datatype CHECK(condition)
); 
```

```sql
(colname datatype CHECK(colname IN(' ', ' '));
(colname datatype CHECK(colname BETWEEN 25.00 AND 770.00));
(colname datatype CHECK(colname LIKE '        '));
```

### Performing Select queries

```sql
-- selecting specific columns
SELECT colname1, colname2
FROM my_table

-- selecting every column in table
SELECT * FROM my_table;

-- avoid duplicate rows
SELECT DISTINCT colname 
FROM my_table;
```

### `SELECT` queries with `WHERE` clause

```sql
-- select rows based on condition
SELECT colname, colname1, colname2
FROM my_table
WHERE <condition>;

-- using relational operator
-- <> not equal to 
-- =, >, <, >=, <=, <>
SELECT * FROM my_table
WHERE city <> 'Delhi'
```

`>` later in alphabet and `<` earlier in alphabet

```sql
-- either one
WHERE (grade='E2' OR grade='E3'); 

-- both condition should meet
WHERE (grade-'E4' AND gross<9000);

WHERE (NOT grade='G1');
```

Operator precedence: `NOT` > `AND` > `OR`

```sql
WHERE colname BETWEEN 30 AND 50;
WHERE colname NOT BETWEEN 30 AND 50;
```

```sql
-- Display list of member from ' ' or ' '
SELECT * FROM my_table
WHERE colname IN('  ', '  ');

-- Display list of members not from ' ' or ' '
SELECT * FROM my_table
WHERE colname NOT IN (' ', ' ');
```

```sql
SELECT * FROM my_table
WHERE colaname LIKE "13%";

-- 13% - any string starting with '13'
-- %13 - any string ending with '13'
-- %13% - any string with '13'
WHERE colname NOT LIKE "13%"

-- String with any 3 characters ending with
WHERE colname LIKE "___0"; 
-- LIKE "wx\%yz%" ESCAPE "\"  matches all string starting "wx%yz"

-- searching for rows with or without null values
WHERE colname IS NULL;
WHERE colname IS NOT NULL;
```

```sql
-- Order by
ORDER BY colnam;
ORDER BY colname DESC;
ORDER BY colname ASC;
```

```sql
-- Group By
GROUP BY colname;

-- Group By with having clause appling condition per group
GROUP BY colname
HAVING condition;
```

Scalar expressions

```sql
SELECT colname, gross*100, '%'
FROM my_table;
```

### Creating table from existing table

```sql
CREATE TABLE my_table2 AS (
	SELECT col1, col2
	FROM my_table
);
```

### Inserting into table

```sql
-- insert into all rows
INSERT INTO my_table
VALUES (, ' ',  ,' ');

-- inset into specific rows
-- columns not listed will have default value 
-- if defiend otherwise NULL value
INSERT INTO my_table(ecode, ename, sex)
VALUES (2018, 'MAX', 'M');
```

```sql
-- insert result from a where query
INSET INTO my_table2
SELECT * FROM  my_table
WHERE gross > 700.00
```

### Delete from table

```sql
DELETE FROM my_table
WHERE <condition>;
```

### Update table

```sql
UPDATE my_table
SET colname = 250
WHERE colname = 14;
```

### Create views

```sql
CREATE VIEW vir_tab AS
SELECT * FROM my_table
WHERE gross > 8000;
```

```sql
CREATE VIEW vir_tab(col, col1, col2) AS
SELECT * FROM my_table
WHERE gross > 8000;
```

```sql
-- create views with sacalar expressions
CREATE VIEW vir_tab(col1, col2, col3) AS
SELECT col1, col2, col3 * 0.1
FROM my_table
WHERE gross > 8000;
```

## Joins

### Inner join

```sql
SELECT
       emp.first_name,
       dep.department_id,
       loc.city,
       loc.state_province
from
     employees emp
INNER JOIN
    departments dep on dep.department_id = emp.department_id
INNER JOIN
    locations loc on dep.location_id = loc.location_id
WHERE
    lower(emp.first_name) like '%s%'
```

### Right join

```sql
SELECT
    emp.first_name,
    dep.department_name
FROM
    employees emp
RIGHT JOIN departments dep on dep.department_id = emp.department_id
```

## Useful commands for psql

- `\dn schema` : Show list of schema
- `\q` : Quit psql
- `\i <drive_letter>_:///<sql_file>.sql` : Run sql from file
- `\du`: show list of roles
- `\d <Table_name>`: Show schema
- `\l` : List of databases