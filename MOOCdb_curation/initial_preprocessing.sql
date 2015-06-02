-- Set safe update to 0
SET SQL_SAFE_UPDATES=0;

-- Create user table
DROP TABLE IF EXISTS `moocdb`.`users`;
CREATE TABLE `moocdb`.`users` AS ( SELECT user_id FROM observed_events GROUP BY user_id);

-- Create time-stamp index
set @exist := (select count(*) from information_schema.statistics where table_name = 'submissions' and index_name = 'user-timestamp_idx' and table_schema = 'moocdb');
--DROP INDEX IF (@exist > 0);
set @sqlstmt := if( @exist > 0, 'drop index `user-timestamp_idx` on `moocdb`.`submissions`', 'select * from `moocdb`.`submissions` where 1=0');
PREPARE stmt FROM @sqlstmt;
EXECUTE stmt;



ALTER TABLE `moocdb`.`submissions` ADD INDEX `user-timestamp_idx`
    (`user_id` ASC, `submission_timestamp` ASC) ;
