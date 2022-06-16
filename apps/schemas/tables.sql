CREATE TABLE CharacterMasters (
    CharacterId INT64 NOT NULL,
    Name STRING(16) NOT NULL,
    Kind STRING(16) NOT NULL,
    CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
    UpdatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
) PRIMARY KEY (CharacterId);

CREATE TABLE OpponentMasters (
    OpponentId INT64 NOT NULL,
    Name STRING(32) NOT NULL,
    Kind STRING(16) NOT NULL,
    Strength INT64 NOT NULL,
    Experience INT64 NOT NULL,
    CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
    UpdatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
) PRIMARY KEY (OpponentId);

CREATE TABLE Users (
    UserId INT64 NOT NULL,
    Name STRING(32) NOT NULL,
    Mail STRING(64) NOT NULL,
    Password STRING(64) NOT NULL,
    CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
    UpdatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
) PRIMARY KEY (UserId);

CREATE TABLE Characters (
    Id INT64 NOT NULL,
    UserId INT64 NOT NULL,
    CharacterId INT64 NOT NULL,
    Name STRING(16) NOT NULL,
    Level INT64 NOT NULL,
    Experience INT64 NOT NULL,
    Strength INT64 NOT NULL,
    CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
    UpdatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
    FOREIGN KEY (UserId) REFERENCES Users (UserId),
    FOREIGN KEY (CharacterId) REFERENCES CharacterMasters (CharacterId),
) PRIMARY KEY (UserId, Id),
INTERLEAVE IN PARENT Users ON DELETE CASCADE;

CREATE TABLE BattleHistory (
    BattleHistoryId INT64 NOT NULL,
    UserId INT64 NOT NULL,
    Id INT64 NOT NULL,
    OpponentId INT64 NOT NULL,
    Result BOOL NOT NULL,
    EntryShardId INT64 NOT NULL,
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