CREATE OR REPLACE FUNCTION "public"."auto_insert_into_tbl_partition"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
DECLARE
    time_column_name 	text ;			-- 父表中用于分区的时间字段的名称[必须首先初始化!!]
    curMMdd 		varchar(20);		-- 'YYYYMMdd'字串,用做分区子表的后缀
    isExist 		boolean;		-- 分区子表,是否已存在
    startTime 		text;
    endTime		text;
    strSQL  		text;
    
BEGIN
    -- 调用前,必须首先初始化(时间字段名):time_column_name [直接从调用参数中获取!!]
    time_column_name := TG_ARGV[0];
   
    -- 判断对应分区表 是否已经存在?
    EXECUTE 'SELECT $1.'||time_column_name INTO strSQL USING NEW;
    curMMdd := to_char(strSQL::timestamp , 'YYYYMMdd');
    select count(*) INTO isExist from pg_class where relname = (TG_RELNAME||'_'||curMMdd);
 
    -- 若不存在, 则插入前需 先创建子分区
    IF ( isExist = false ) THEN  
        -- 创建子分区表
        startTime := curMMdd||' 00:00:00';
        endTime := to_char( startTime::timestamp + interval '1 day', 'YYYYMMDD HH24:MI:SS');
        strSQL := 'CREATE TABLE IF NOT EXISTS '||TG_RELNAME||'_'||curMMdd||
				'( CHECK('||time_column_name||'>='''|| startTime ||''' AND '||
				time_column_name||'< '''|| endTime ||''' )) INHERITS ('||TG_RELNAME||') ;';  
        EXECUTE strSQL;
 
        -- 创建索引
        strSQL := 'CREATE INDEX '||TG_RELNAME||'_'||curMMdd||'_INDEX_'||time_column_name||' ON '
                  ||TG_RELNAME||'_'||curMMdd||' ('||time_column_name||');' ;
        EXECUTE strSQL;
       
    END IF;
 
    -- 插入数据到子分区!
    strSQL := 'INSERT INTO '||TG_RELNAME||'_'||curMMdd||' SELECT $1.*' ;
    EXECUTE strSQL USING NEW;
    RETURN NULL; 
END
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
	
CREATE TRIGGER insert_tbl_partition_trigger
  BEFORE INSERT
  ON t_rtp_report
  FOR EACH ROW
  EXECUTE PROCEDURE auto_insert_into_tbl_partition('pcap_time');
