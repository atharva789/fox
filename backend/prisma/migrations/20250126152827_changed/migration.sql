/*
  Warnings:

  - You are about to drop the column `name` on the `StudyGuide` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "Resource" ALTER COLUMN "embedding" DROP NOT NULL;

-- AlterTable
ALTER TABLE "StudyGuide" DROP COLUMN "name";
