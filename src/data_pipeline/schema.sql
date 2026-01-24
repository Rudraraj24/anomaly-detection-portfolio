-- STRICTLY CONFIDENTIAL - ZeTheta Algorithms Pvt Ltd
-- Database Schema for Anomaly Detection System

-- Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    transaction_type VARCHAR(50),
    merchant_id VARCHAR(100),
    merchant_category VARCHAR(50),
    location_country VARCHAR(50),
    location_city VARCHAR(100),
    device_type VARCHAR(50),
    ip_address INET,
    is_fraud BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX idx_transactions_is_fraud ON transactions(is_fraud);

-- Transaction Features Table
CREATE TABLE IF NOT EXISTS transaction_features (
    feature_id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) REFERENCES transactions(transaction_id),
    amount_zscore DECIMAL(10, 4),
    amount_user_avg_ratio DECIMAL(10, 4),
    transaction_velocity_1h INTEGER,
    transaction_velocity_24h INTEGER,
    hour_of_day INTEGER,
    day_of_week INTEGER,
    is_weekend BOOLEAN,
    days_since_last_transaction DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_features_transaction_id ON transaction_features(transaction_id);

-- Anomaly Scores Table
CREATE TABLE IF NOT EXISTS anomaly_scores (
    score_id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) REFERENCES transactions(transaction_id),
    isolation_forest_score DECIMAL(10, 6),
    lof_score DECIMAL(10, 6),
    one_class_svm_score DECIMAL(10, 6),
    xgboost_score DECIMAL(10, 6),
    composite_score DECIMAL(10, 6) NOT NULL,
    risk_level VARCHAR(20),
    model_version VARCHAR(50),
    scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_anomaly_scores_transaction_id ON anomaly_scores(transaction_id);
CREATE INDEX idx_anomaly_scores_composite ON anomaly_scores(composite_score);
CREATE INDEX idx_anomaly_scores_risk_level ON anomaly_scores(risk_level);

-- Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    alert_id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(100) REFERENCES transactions(transaction_id),
    score_id INTEGER REFERENCES anomaly_scores(score_id),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    priority INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'OPEN',
    assigned_to VARCHAR(100),
    investigated_by VARCHAR(100),
    resolution VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE INDEX idx_alerts_transaction_id ON alerts(transaction_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_created_at ON alerts(created_at);

-- Model Metrics Table
CREATE TABLE IF NOT EXISTS model_metrics (
    metric_id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    precision DECIMAL(6, 4),
    recall DECIMAL(6, 4),
    f1_score DECIMAL(6, 4),
    pr_auc DECIMAL(6, 4),
    detection_rate DECIMAL(6, 4),
    false_positive_rate DECIMAL(6, 4),
    total_predictions INTEGER,
    evaluation_start TIMESTAMP,
    evaluation_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_model_metrics_name ON model_metrics(model_name);
CREATE INDEX idx_model_metrics_created_at ON model_metrics(created_at);

-- User Profiles Table
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id VARCHAR(100) PRIMARY KEY,
    avg_transaction_amount DECIMAL(15, 2),
    std_transaction_amount DECIMAL(15, 2),
    transaction_frequency DECIMAL(10, 2),
    risk_score DECIMAL(6, 4),
    account_age_days INTEGER,
    profile_last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_profiles_risk_score ON user_profiles(risk_score);
