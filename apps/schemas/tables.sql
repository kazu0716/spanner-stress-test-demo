CREATE TABLE Users (
    UserId INT64 NOT NULL,
    Mail STRING(64),
    Password STRING(64),
    CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
    UpdatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
) PRIMARY KEY (UserId);

CREATE TABLE Characters (
    Id INT64 NOT NULL,
    UserId INT64 NOT NULL,
    CharacterId INT64 NOT NULL,
    Name STRING(16),
    Level INT64,
    Experience INT64,
    Strength INT64,
    CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
    UpdatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
    FOREIGN KEY (CharacterId) REFERENCES CharacterMasters (CharacterId),
) PRIMARY KEY (UserId, Id),
INTERLEAVE IN PARENT Users ON DELETE CASCADE;

CREATE TABLE CharacterMasters (
    CharacterId INT64,
    Name STRING(16),
    Kind STRING(16),
    CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
    UpdatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
) PRIMARY KEY (CharacterId);

CREATE TABLE OpponentMasters (
    OpponentId INT64 NOT NULL,
    Name STRING(32),
    Kind STRING(16),
    Strength INT64,
    Experience INT64,
    CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
    UpdatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
) PRIMARY KEY (OpponentId);

CREATE TABLE BattleHistory (
    BattleHistoryId INT64 NOT NULL,
    UserId INT64 NOT NULL,
    Id INT64 NOT NULL,
    OpponentId INT64 NOT NULL,
    Result BOOL,
    EntryShardId INT64,
    CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
    UpdatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
    FOREIGN KEY (UserId) REFERENCES Users (UserId),
    FOREIGN KEY (Id) REFERENCES Characters (Id),
    FOREIGN KEY (OpponentId) REFERENCES OpponentMasters (OpponentId),
) PRIMARY KEY (
    UserId,
    Id,
    OpponentId,
    BattleHistoryId
);

CREATE INDEX BattleHistoryByUserId ON BattleHistory(EntryShardId, UserId, UpdatedAt);