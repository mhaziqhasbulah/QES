CREATE TABLE Jobcards (
    JobcardNumber BIGINT PRIMARY KEY,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Stringers (
    ID SERIAL PRIMARY KEY,
    MachineId VARCHAR(255) NOT NULL,
    JobcardNumber BIGINT REFERENCES Jobcards(JobcardNumber) ON DELETE CASCADE,
    CurrentLayerName VARCHAR(255),
    CompletionPercentage DECIMAL(5,2) DEFAULT 0.00,
    PresetId VARCHAR(50),
    HeaterTemperature INT,
    MaximumSpeed INT,
    MinimumSpeed INT,
    AverageSpeed DECIMAL(10,2) DEFAULT 0.00,
    LastMoveTimeEpoch BIGINT,
    TotalRuntimeSeconds INT DEFAULT 0,
    IsCompleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE Laminators (
    ID SERIAL PRIMARY KEY,
    MachineId VARCHAR(255) NOT NULL,
    JobcardNumber BIGINT REFERENCES Jobcards(JobcardNumber) ON DELETE CASCADE,
    PresetId VARCHAR(50),
    HeaterPower INT,
    HeaterMinimumPower INT,
    HeaterMaximumPower INT,
    LaminationSpeed DECIMAL(5,2),
    VacuumReading DECIMAL(5,2),
    TotalRuntimeSeconds INT DEFAULT 0,
    LastMoveTimeEpoch BIGINT,
    AverageSurfaceTemperature1 DECIMAL(5,2),
    AverageSurfaceTemperature2 DECIMAL(5,2),
    AverageSurfaceTemperature3 DECIMAL(5,2),
    MaxTemperatureSensor1 DECIMAL(5,2),
    MaxTemperatureSensor2 DECIMAL(5,2),
    MaxTemperatureSensor3 DECIMAL(5,2),
    MaxTemperatureSensor4 DECIMAL(5,2),
    MaxTemperatureSensor5 DECIMAL(5,2),
    MaxTemperatureSensor6 DECIMAL(5,2),
    MaxTemperatureSensor7 DECIMAL(5,2),
    MaxTemperatureSensor8 DECIMAL(5,2),
    IsCompleted BOOLEAN DEFAULT FALSE
);
