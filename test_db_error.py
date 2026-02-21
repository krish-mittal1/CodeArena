import asyncio
from sqlalchemy import select
from backend.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.models.submission_result import SubmissionResult
from backend.models.submission import Submission

async def main():
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(
            select(SubmissionResult, Submission)
            .join(Submission)
            .where(SubmissionResult.verdict == "compilation_error")
            .order_by(SubmissionResult.id.desc())
            .limit(1)
        )
        row = result.first()
        if row:
            sub_result, submission = row
            with open("error_log.txt", "w", encoding="utf-8") as f:
                f.write(f"Submission ID: {sub_result.submission_id}\n")
                f.write(f"Language: {submission.language}\n")
                f.write(f"Code:\n{submission.code}\n")
                f.write("-" * 40 + "\n")
                f.write(f"Error Output:\n{sub_result.error_output}\n")
            print("Wrote to error_log.txt")
        else:
            print("No compilation errors found.")

asyncio.run(main())
