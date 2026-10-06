-- MepCenter Claude Hub veritabanı şeması (MySQL 5.7+ / MariaDB 10.3+)

CREATE TABLE IF NOT EXISTS hub_settings (
  k VARCHAR(64) NOT NULL PRIMARY KEY,
  v TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Bağlanmasına izin verilen ajanlar (her makine/Claude için ayrı token)
CREATE TABLE IF NOT EXISTS hub_agents (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  type VARCHAR(30) NOT NULL DEFAULT 'claude',
  token_hash CHAR(64) NOT NULL UNIQUE,
  token_hint VARCHAR(12) NOT NULL,
  active TINYINT(1) NOT NULL DEFAULT 1,
  note VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_seen_at DATETIME NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Çalışan oturumlar (makine + proje klasörü başına bir kayıt)
CREATE TABLE IF NOT EXISTS hub_sessions (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  agent_id INT UNSIGNED NOT NULL,
  client_key VARCHAR(191) NOT NULL,
  machine VARCHAR(100) NOT NULL DEFAULT '',
  project VARCHAR(191) NOT NULL DEFAULT '',
  project_code VARCHAR(60) NULL,
  cwd VARCHAR(500) NOT NULL DEFAULT '',
  status_text TEXT NULL,
  started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ended_at DATETIME NULL,
  UNIQUE KEY uq_agent_client (agent_id, client_key),
  KEY idx_last_seen (last_seen_at),
  CONSTRAINT fk_sess_agent FOREIGN KEY (agent_id) REFERENCES hub_agents(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Oturumlar arası mesajlar. to_type: all | agent | session | machine | project | admin (panele)
CREATE TABLE IF NOT EXISTS hub_messages (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  from_session_id INT UNSIGNED NULL,
  from_label VARCHAR(191) NOT NULL,
  to_type VARCHAR(10) NOT NULL DEFAULT 'all',
  to_value VARCHAR(191) NOT NULL DEFAULT '',
  topic VARCHAR(191) NOT NULL DEFAULT '',
  body MEDIUMTEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_to (to_type, to_value),
  KEY idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS hub_message_reads (
  message_id INT UNSIGNED NOT NULL,
  session_id INT UNSIGNED NOT NULL,
  read_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (message_id, session_id),
  CONSTRAINT fk_read_msg FOREIGN KEY (message_id) REFERENCES hub_messages(id) ON DELETE CASCADE,
  CONSTRAINT fk_read_sess FOREIGN KEY (session_id) REFERENCES hub_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Konuşma kayıtları / özetler / notlar
CREATE TABLE IF NOT EXISTS hub_topics (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  session_id INT UNSIGNED NULL,
  project_code VARCHAR(60) NULL,
  kind VARCHAR(20) NOT NULL DEFAULT 'conversation',
  title VARCHAR(255) NOT NULL DEFAULT '',
  content MEDIUMTEXT NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_session (session_id),
  KEY idx_code (project_code),
  KEY idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Yüklenen dosyalar (aynı yol tekrar yüklenirse yeni sürüm olarak eklenir)
CREATE TABLE IF NOT EXISTS hub_files (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  session_id INT UNSIGNED NULL,
  project_code VARCHAR(60) NULL,
  orig_name VARCHAR(255) NOT NULL,
  rel_path VARCHAR(500) NOT NULL DEFAULT '',
  stored_name CHAR(40) NOT NULL,
  size INT UNSIGNED NOT NULL,
  sha256 CHAR(64) NOT NULL,
  note VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_session (session_id),
  KEY idx_code (project_code),
  KEY idx_sha (sha256)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Proje kodları: kullanıcı konuşma başında "Proje kodu: XXX" der, tüm kayıtlar bu koda bağlanır
CREATE TABLE IF NOT EXISTS hub_projects (
  code VARCHAR(60) NOT NULL PRIMARY KEY,
  name VARCHAR(191) NOT NULL DEFAULT '',
  summary MEDIUMTEXT NULL,
  summary_by VARCHAR(191) NULL,
  summary_at DATETIME NULL,
  note TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Ortak anahtar/değer deposu (Claude'ların paylaşılan "veritabanı"sı)
CREATE TABLE IF NOT EXISTS hub_kv (
  ns VARCHAR(100) NOT NULL,
  k VARCHAR(191) NOT NULL,
  v MEDIUMTEXT NOT NULL,
  updated_by VARCHAR(191) NOT NULL DEFAULT '',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (ns, k)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS hub_login_attempts (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  ip VARCHAR(45) NOT NULL,
  attempted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_ip_time (ip, attempted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
