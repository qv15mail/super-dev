-- Migration SQL
-- Created: 2026-03-01T17:14:08.946564

-- Create users table
CREATE TABLE "users" (
    "id" UUID PRIMARY KEY,
    "email" VARCHAR(255) UNIQUE,
    "password_hash" VARCHAR(255),
    "name" VARCHAR(255),
    "created_at" TIMESTAMP,
    "updated_at" TIMESTAMP
);

-- Create auth_tokens table
CREATE TABLE "auth_tokens" (
    "id" UUID PRIMARY KEY,
    "user_id" UUID,
    "token" VARCHAR(255) UNIQUE,
    "expires_at" TIMESTAMP,
    "created_at" TIMESTAMP
);
