from pydantic import BaseModel


class OfflineCheckResult(BaseModel):
    updated_count: int


class SchedulerStatus(BaseModel):
    running: bool
    jobs: list[str]
