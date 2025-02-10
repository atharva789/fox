/*
  Warnings:

  - Added the required column `embedding` to the `Resource` table without a default value. This is not possible if the table is not empty.

*/
-- CreateExtension
CREATE EXTENSION IF NOT EXISTS "vector";

-- AlterTable
ALTER TABLE "Resource" ADD COLUMN     "embedding" vector(1536) NOT NULL;
