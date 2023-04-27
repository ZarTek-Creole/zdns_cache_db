CREATE DATABASE IF NOT EXISTS `zdns_cache_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

USE `zdns_cache_db`;

CREATE TABLE IF NOT EXISTS `dns_records` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `domain_name` VARCHAR(255) NOT NULL,
    `record_type` ENUM('A', 'AAAA', 'CNAME', 'MX', 'NS', 'PTR', 'SOA', 'SRV', 'TXT') NOT NULL,
    `ip_address` VARCHAR(45) NOT NULL,
    `search_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_domain_name_record_type` (`domain_name`, `record_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
