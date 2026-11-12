"""Version 1 contracts. Independent of any model-provider SDK."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

MAX_TEXT = 30_000
Category = Literal['content_license', 'third_party_sharing', 'data_retention', 'arbitration']
Risk = Literal['Low', 'Medium', 'High']


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True, strict=True)


class AnalyzeRequest(StrictModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT)
    original_length: int | None = Field(default=None, ge=1, le=10_000_000)
    truncated: bool = False

    @model_validator(mode='after')
    def check_coverage(self):
        original = self.original_length if self.original_length is not None else len(self.text)
        if original < len(self.text) or self.truncated != (original > len(self.text)):
            raise ValueError('Truncation metadata must match the supplied text length.')
        return self


class Finding(StrictModel):
    category: Category
    quote: str = Field(min_length=1, max_length=1200)
    explanation: str = Field(min_length=1, max_length=1200)


class ProviderResult(StrictModel):
    risk_level: Risk
    summary: str = Field(min_length=1, max_length=2000)
    findings: list[Finding] = Field(max_length=8)


class Coverage(StrictModel):
    submitted_characters: int
    original_characters: int
    truncated: bool


class AnalyzeResponse(StrictModel):
    schema_version: Literal['1.0'] = '1.0'
    request_id: str
    mode: Literal['mock', 'ai']
    status: Literal['complete', 'partial']
    risk_level: Risk
    summary: str
    red_flags: list[str]
    findings: list[Finding]
    coverage: Coverage
    limitations: list[str]
