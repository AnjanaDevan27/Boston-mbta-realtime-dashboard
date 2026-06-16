-- tables to store MBTA real-time data

CREATE TABLE IF NOT EXISTS predictions (
    id              SERIAL PRIMARY KEY,
    route           VARCHAR(20) NOT NULL,
    stop_id         VARCHAR(50),
    direction_id    SMALLINT,
    arrival_time    TIMESTAMPTZ,
    departure_time  TIMESTAMPTZ,
    status          VARCHAR(50),
    schedule_relationship VARCHAR(50),
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS vehicles (
    id              SERIAL PRIMARY KEY,
    vehicle_id      VARCHAR(50) NOT NULL,
    route           VARCHAR(20) NOT NULL,
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    bearing         SMALLINT,
    speed           DOUBLE PRECISION,
    current_status  VARCHAR(50),
    occupancy_status VARCHAR(50),
    fetched_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS alerts (
    id              SERIAL PRIMARY KEY,
    alert_id        VARCHAR(50) NOT NULL,
    header          TEXT,
    severity        SMALLINT,
    effect          VARCHAR(100),
    cause           VARCHAR(100),
    active_period_start TIMESTAMPTZ,
    active_period_end TIMESTAMPTZ,
    fetched_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id              SERIAL PRIMARY KEY,
    started_at      TIMESTAMPTZ NOT NULL,
    finished_at     TIMESTAMPTZ,
    status          VARCHAR(20),
    records_inserted INT,
    error_message    TEXT

);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_predictions_route ON predictions(route);
CREATE INDEX IF NOT EXISTS idx_predictions_fetched_at ON predictions(fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_vehicles_route ON vehicles(route);
CREATE INDEX IF NOT EXISTS idx_vehicles_fetched_at ON vehicles(fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_fetched_at ON alerts(fetched_at DESC);