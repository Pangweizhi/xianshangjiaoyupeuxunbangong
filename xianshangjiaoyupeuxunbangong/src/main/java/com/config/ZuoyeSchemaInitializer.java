package com.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

/**
 * Ensure the homework table schema matches the current entity and mapper.
 *
 * Some environments still ship a legacy zuoye table without start_time/end_time.
 * The backend selects and writes these columns, so we add them lazily on startup
 * when they are missing.
 */
@Component
public class ZuoyeSchemaInitializer implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(ZuoyeSchemaInitializer.class);

    private final DataSource dataSource;

    public ZuoyeSchemaInitializer(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Override
    public void run(ApplicationArguments args) {
        try (Connection connection = dataSource.getConnection()) {
            String schema = connection.getCatalog();
            if (schema == null || schema.trim().isEmpty()) {
                log.warn("Skip zuoye schema check because database schema name is empty");
                return;
            }

            boolean startExists = columnExists(connection, schema, "zuoye", "start_time");
            boolean endExists = columnExists(connection, schema, "zuoye", "end_time");

            if (startExists && endExists) {
                return;
            }

            try (Statement statement = connection.createStatement()) {
                if (!startExists) {
                    statement.executeUpdate(
                        "ALTER TABLE `zuoye` ADD COLUMN `start_time` timestamp NULL DEFAULT NULL COMMENT '开始时间' AFTER `chapter_id`"
                    );
                    log.info("Added missing column zuoye.start_time");
                }

                if (!endExists) {
                    statement.executeUpdate(
                        "ALTER TABLE `zuoye` ADD COLUMN `end_time` timestamp NULL DEFAULT NULL COMMENT '结束时间' AFTER `start_time`"
                    );
                    log.info("Added missing column zuoye.end_time");
                }

                statement.executeUpdate(
                    "UPDATE `zuoye` " +
                        "SET `start_time` = IF(`start_time` IS NULL, COALESCE(`insert_time`, `create_time`, NOW()), `start_time`), " +
                        "`end_time` = IF(`end_time` IS NULL, COALESCE(`deadline_time`, DATE_ADD(COALESCE(`insert_time`, `create_time`, NOW()), INTERVAL 7 DAY)), `end_time`) " +
                        "WHERE 1 = 1"
                );
                log.info("Backfilled zuoye.start_time and zuoye.end_time values");
            }
        } catch (SQLException e) {
            throw new IllegalStateException("Failed to ensure zuoye table schema", e);
        }
    }

    private boolean columnExists(Connection connection, String schema, String table, String column) throws SQLException {
        DatabaseMetaData metaData = connection.getMetaData();
        try (ResultSet resultSet = metaData.getColumns(schema, null, table, column)) {
            return resultSet.next();
        }
    }
}
