-- Created on Jan 6, 2016
-- @author: Alec Anderson for LIDS, MIT lab: alecand@mit.edu

set session sql_mode="NO_BACKSLASH_ESCAPES,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION";

--roll back old changes
SET @exist := (SELECT count(*) FROM INFORMATION_SCHEMA.COLUMNS
          WHERE TABLE_SCHEMA='moocdb' AND TABLE_NAME='users' AND COLUMN_NAME='user_last_submission_id' );
set @sqlstmt := if( @exist > 0, 'ALTER TABLE `moocdb`.`users` DROP COlUMN `user_last_submission_id`', 'select * from `moocdb`.`users` where 1=0');
PREPARE stmt FROM @sqlstmt;
EXECUTE stmt;

-- add column if necessary
DROP PROCEDURE IF EXISTS Alter_Table;

CREATE PROCEDURE Alter_Table()
BEGIN
    DECLARE _count INT;
    SET _count = (  SELECT COUNT(*) 
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = 'moocdb' AND
                                TABLE_NAME = 'users' AND
                                COLUMN_NAME = 'user_last_submission_id');
    IF _count = 0 THEN
      ALTER TABLE `moocdb`.`users`
        ADD COLUMN `user_last_submission_id` INT(11) NULL;
    END IF;
END;

CALL Alter_Table();

-- populate column
UPDATE `moocdb`.`users` AS `users`
   SET `users`.user_last_submission_id = (
       SELECT
           submissions.submission_id
       FROM
           `moocdb`.submissions AS submissions
       WHERE
           `users`.user_id = submissions.user_id
               AND submissions.submission_timestamp = (SELECT
                   MAX(submissions.submission_timestamp)
               FROM
                   `moocdb`.submissions AS submissions
               WHERE
                   `users`.user_id = submissions.user_id)
       GROUP BY submissions.user_id

   );