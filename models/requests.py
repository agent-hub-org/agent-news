from pydantic import BaseModel, Field


class NewsPreferencesRequest(BaseModel):
    topics: list[str] = Field(
        default_factory=list,
        description="News topics of interest (e.g. ['technology', 'Indian markets', 'climate']).",
    )
    regions: list[str] = Field(
        default_factory=list,
        description="Geographic regions to prioritize (e.g. ['India', 'US', 'EU']).",
    )
    excluded_topics: list[str] = Field(
        default_factory=list,
        description="Topics to exclude from briefings (e.g. ['sports', 'celebrity']).",
    )
    market_tickers: list[str] = Field(
        default_factory=list,
        description="Stock/asset tickers to track for market news (e.g. ['RELIANCE.NS', 'NIFTY']).",
    )
