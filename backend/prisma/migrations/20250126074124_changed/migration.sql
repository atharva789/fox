/*
  Warnings:

  - You are about to drop the column `file` on the `Module` table. All the data in the column will be lost.
  - You are about to drop the column `email` on the `Student` table. All the data in the column will be lost.
  - You are about to drop the column `name` on the `Student` table. All the data in the column will be lost.
  - You are about to drop the column `file` on the `StudyGuide` table. All the data in the column will be lost.

*/
-- DropIndex
DROP INDEX "Student_email_key";

-- AlterTable
ALTER TABLE "Module" DROP COLUMN "file";

-- AlterTable
ALTER TABLE "Student" DROP COLUMN "email",
DROP COLUMN "name";

-- AlterTable
ALTER TABLE "StudyGuide" DROP COLUMN "file",
ADD COLUMN     "content" TEXT;

-- CreateTable
CREATE TABLE "Resource" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "moduleId" INTEGER NOT NULL,
    "file" TEXT,

    CONSTRAINT "Resource_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "Resource" ADD CONSTRAINT "Resource_moduleId_fkey" FOREIGN KEY ("moduleId") REFERENCES "Module"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
