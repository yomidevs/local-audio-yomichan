
## v1.0.0
**Major code rewrite:**
- Separated code into different files, one for each source
- Made base class to reuse logic better
- Moved most audio logic into their respective classes

**Other logic changes:**
- Got rid of `ORDER BY speaker` when `user` param exists, because it will be re-ordered in post processing anyways
- Changed general table format:
    ```
    CREATE TABLE table_name (
        id integer PRIMARY KEY,
        expression text NOT NULL,
        reading text,
        file text NOT NULL
        priority integer NOT NULL
    );
    CREATE INDEX idx_table_name_expression_reading ON table_name(expression, reading);
    ```
- Removed nhk98 support (due to not having any audio files for it to test it on)
- Fixed JPod + JPod Alt audio sometimes not being fetched because the query does not account for empty expressions or readings
    - Kana only words are stored with both expression and reading being filled (as the same thing)
    - Expression only words are stored without reading i.e. (null)



## sql_09
