from pydantic import BaseModel


class ChartResultResponse(BaseModel):
    chart_type: str
    title: str
    columns: list[str]
    image_base64: str


class DatasetVisualizationResponse(BaseModel):
    dataset_id: str
    charts: list[ChartResultResponse]
