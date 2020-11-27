/**
 * Welcome to the SQL editor
 * =========================
 *
 * The SQL code you write here will continuously transform your streaming data
 * when your application is running.
 *
 * Get started by clicking "Add SQL from templates" or pull up the
 * documentation and start writing your own custom queries.
 */

CREATE OR REPLACE STREAM "DESTINATION_SQL_STREAM"
           (time_value VARCHAR(50),
            id        BIGINT, --recordid
            source        VARCHAR(8), --source
            predicted_label        DECIMAL,
            pred_proba DOUBLE); --pred_label

CREATE OR REPLACE PUMP "STREAM_PUMP" AS
   INSERT INTO "DESTINATION_SQL_STREAM"
      SELECT STREAM "time_value","id","source","predicted_label","pred_proba"
      FROM   "SOURCE_SQL_STREAM_001"
      WHERE  "pred_proba" > 0.5;
