drop table t_rtp_report;
create table t_rtp_report
(
	pcap_time timestamp without time zone,
	srcip     VARCHAR(20)
);

INSERT into t_rtp_report(pcap_time,srcip) VALUES(to_date('2018-02-16 11:00:00', 'YYYY-MM-DD HH24:MI:SS'), '192.168.0.1');
