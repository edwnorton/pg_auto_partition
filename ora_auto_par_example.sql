create table test
(
  time date,
  ip   varchar2(20)
 )
 partition by range(time)
 interval(numtoDSinterval(1,'DAY'))
  (
    partition p_main values less then(to_date('2019-2-1 00:00:00','YYYY-MM-DD HH24:MI:SS'))
  );
--create/recreate indexes
create index INDEX_time on test (time) local;
