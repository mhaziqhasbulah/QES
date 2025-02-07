CREATE TABLE Jobcards (
    JobcardNumber BIGINT PRIMARY KEY,
    CreatedAt DATETIME DEFAULT GETDATE()
);

CREATE TABLE Stringers (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    MachineId VARCHAR(255) NOT NULL,
    JobcardNumber BIGINT FOREIGN KEY REFERENCES Jobcards(JobcardNumber) ON DELETE CASCADE,
    CurrentLayerName VARCHAR(255),
    CompletionPercentage DECIMAL(5,2) DEFAULT 0.00,
    PresetId VARCHAR(50),
    HeaterTemperature INT,
    MaximumSpeed INT,
    MinimumSpeed INT,
    AverageSpeed DECIMAL(10,2) DEFAULT 0.00,
    LastMoveTimeEpoch BIGINT,
    TotalRuntimeSeconds INT DEFAULT 0,
    IsCompleted BIT DEFAULT 0
);

CREATE TABLE Laminators (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    MachineId VARCHAR(255) NOT NULL,
    JobcardNumber BIGINT FOREIGN KEY REFERENCES Jobcards(JobcardNumber) ON DELETE CASCADE,
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
    IsCompleted BIT DEFAULT 0
);

CREATE TABLE designerfile (
    jobcard INT,
    week INT,
    date DATE,
    rig NVARCHAR(MAX),
    finish_facilities NVARCHAR(MAX),
    salesperson NVARCHAR(MAX),
    sail_type NVARCHAR(MAX),
    product_m NVARCHAR(MAX),
    layout_m_mx NVARCHAR(MAX),
    patches_internal_external NVARCHAR(MAX),
    xply_angle NVARCHAR(MAX),
    transverse_angle NVARCHAR(MAX),
    number_of_panel NVARCHAR(MAX),
    area_m_2 Float,
    dpi Float,
    stringing_film NVARCHAR(MAX),
    stringing_film_code NVARCHAR(MAX),
    laminate_film NVARCHAR(MAX),
    laminate_film_code NVARCHAR(MAX),
    i_pure_corner NVARCHAR(MAX),
    i_pure_starfish NVARCHAR(MAX),
    batten_end NVARCHAR(MAX),
    jellyfish NVARCHAR(MAX),
    remark NVARCHAR(MAX),
    stringer_id NVARCHAR(MAX),
    laminate_id NVARCHAR(MAX),
    low_power INT,
    medium_low_power INT,
    medium_power INT,
    medium_high_power INT,
    high_power INT,
    speed_low FLOAT,
    speed_medium_low FLOAT,
    speed_medium FLOAT,
    speed_medium_high FLOAT,
    speed_high FLOAT,
    target_temperature INT,    	presetid NVARCHAR(MAX),
    actual_target_temperature FLOAT,
    quality_1_to_5 INT,
    failure_mode_gg_percent FLOAT,
    failure_mode_gp_percent FLOAT,
    failure_mode_ps_percent FLOAT,
    membrane_feel_hard_or_soft NVARCHAR(MAX),
    approved NVARCHAR(MAX),
    comment NVARCHAR(MAX)
);

CREATE TABLE process_data (
    ID INT IDENTITY(1,1) PRIMARY KEY,  -- A unique identifier for each entry that auto-increments
    TIME TIME,           -- Stores the time
    DATE DATE,           -- Stores the date
    JOBCARD_NUMBER VARCHAR(50),  -- Stores job card number (string)
    SAIL_NAME VARCHAR(100),  -- Stores sail or product name
    PRESET_ID VARCHAR(50),   -- Preset identifier
    POWER_SET INT,           -- Power set
    POWER_DENSITY FLOAT,     -- Power density
    SPEED_SET FLOAT,         -- Speed set
    MACHINE_ID VARCHAR(50),  -- Machine identifier
    TARGET_TEMP INT,         -- Target temperature
    TEMP1A FLOAT,            -- Temperature readings
    TEMP1B FLOAT,
    TEMP2A FLOAT,
    TEMP2B FLOAT,
    TEMP3A FLOAT,
    TEMP3B FLOAT,
    TEMP4A FLOAT,
    TEMP4B FLOAT,
    AVG_STIFFNESS FLOAT,     -- Average stiffness
    ADHESION VARCHAR(50),    -- Adhesion measurement
    COMMENTS TEXT            -- Additional comments
);

CREATE TABLE preset_list (
    Rig VARCHAR(100),
    Sail_Type VARCHAR(100),
    Product VARCHAR(100),
    Area_m2 FLOAT,  -- Area in square meters
    DPI_At_1_2_Leech_MIN FLOAT,  -- DPI at 1/2 Leech (minimum)
    DPI_At_1_2_Leech_MAX FLOAT,  -- DPI at 1/2 Leech (maximum)
    Film_Stringing VARCHAR(100),  -- Film Stringing type/description
    Film_Laminate VARCHAR(100),   -- Film Laminate type/description
    Laminator_Yellow_Blue VARCHAR(100),  -- Laminator (Yellow/Blue)
    Power_Low FLOAT,  -- Power settings
    Power_Medium_Low FLOAT,
    Power_Medium FLOAT,
    Power_Medium_High FLOAT,
    Power_High FLOAT,
    Speed_Low FLOAT,  -- Speed settings
    Speed_Medium_Low FLOAT,
    Speed_Medium FLOAT,
    Speed_Medium_High FLOAT,
    Speed_High FLOAT,
    Target_Internal_Temp_C FLOAT,  -- Target Internal Temperature in °C
    Actual_Internal_Temp_C FLOAT   -- Actual Internal Temperature in °C
);

SELECT TOP (1000) [jobcard]
      ,[time]
      ,[date]
      ,[power_w_cm2]
      ,[power_percent]
      ,[speed]
      ,[sensor1]
      ,[sensor2]
      ,[sensor3]
      ,[sensor4]
      ,[sensor5]
      ,[sensor6]
      ,[sensor7]
      ,[sensor8]
      ,[target_temperature]
      ,[machine]
  FROM [laminatordatabase].[dbo].[logs]

ALTER TABLE preset_list
ALTER COLUMN DPI_At_1_2_Leech_MIN FLOAT;

ALTER TABLE preset_list
ALTER COLUMN DPI_At_1_2_Leech_MAX FLOAT;

SELECT TABLE_SCHEMA, TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME = 'logs';


