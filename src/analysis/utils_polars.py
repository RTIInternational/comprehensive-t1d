import polars as pl


def unfurl_and_tally_events(df: pl.DataFrame, events: list[str]) -> pl.DataFrame:
    """
    Unpack, sum, and cumulative sum the values for the given events.

    Parameters
    ----------
    df : pl.DataFrame
        Initial DataFrame
    events : list[str]
        List of columns to be unfurled

    Returns
    -------
    pl.DataFrame
        Unfurled and tallied DataFrame
    """

    events_df = df.select(events)
    events_df = events_df.with_row_index("agent_id")
    events_df = events_df.explode(events)
    events_df = events_df.with_columns(
        pl.int_range(0, pl.col("agent_id").len()).over("agent_id").alias("step")
    )
    events_df = events_df.filter(pl.col("step") > 0)
    events_df = events_df.drop("agent_id")
    events_df = events_df.group_by("step", maintain_order=True).agg(
        [pl.col(event).sum().alias(event) for event in events]
    )
    events_df = events_df.with_columns(
        [pl.col(event).cum_sum().alias(f"cumulative_{event}") for event in events]
    )

    ordered_events = []
    for event in events:
        ordered_events.extend((event, f"cumulative_{event}"))
    events_df = events_df.select(["step", *ordered_events])

    return events_df


def unfurl_and_tally_chronic_events(
    df: pl.DataFrame, events: list[str]
) -> pl.DataFrame:
    """
    Unpack, sum, and cumulative sum the values for the given chronic events.

    Parameters
    ----------
    df : pl.DataFrame
        Initial DataFrame
    events : list[str]
        List of columns to be unfurled

    Returns
    -------
    pl.DataFrame
        Unfurled and tallied DataFrame
    """

    def _replace_with_zeros(event: pl.Series):
        updated_event = event.to_list()
        if updated_event[0] == 0 and 1 in updated_event:
            first_one_index = updated_event.index(1)
            updated_event[first_one_index + 1 :] = [0] * (
                len(updated_event) - first_one_index - 1
            )
        else:
            updated_event = [0] * len(updated_event)

        return updated_event

    events_df = df.with_columns(
        [
            (pl.col(event).map_elements(_replace_with_zeros).alias(event))
            for event in events
        ]
    )

    return unfurl_and_tally_events(events_df, events)

def unfurl_and_tally_risk_factors(df: pl.DataFrame, risk_factors: list[str]) -> pl.DataFrame:
    """
    Unpack, sum, and cumulative sum the values for the given events.

    Parameters
    ----------
    df : pl.DataFrame
        Initial DataFrame
    events : list[str]
        List of columns to be unfurled

    Returns
    -------
    pl.DataFrame
        Unfurled and tallied DataFrame
    """

    events_df = df.select(risk_factors)
    events_df = events_df.with_row_index("agent_id")
    events_df = events_df.explode(risk_factors)
    events_df = events_df.with_columns(
        pl.int_range(0, pl.col("agent_id").len()).over("agent_id").alias("step")
    )
    events_df = events_df.filter(pl.col("step") > 0)
    events_df = events_df.drop("agent_id")

    events_df = events_df.group_by("step", maintain_order=True).agg(
        [
            *[pl.sum(risk_factor).name.prefix("sum_") for risk_factor in risk_factors],
            *[pl.mean(risk_factor).name.prefix("mean_") for risk_factor in risk_factors],
        ]
    )

    if 'bariatric_surgery' in df.columns:
        surgery_count = df['bariatric_surgery'].sum()
        events_df = events_df.with_columns(pl.lit(surgery_count).alias('sum individuals with surgery'))
    return events_df

    # this is the original code
    # events_df = events_df.group_by("step", maintain_order=True).agg(
    #     [(pl.col(risk_factor).mean().alias(f"annual_mean_{risk_factor}")) for risk_factor in risk_factors]
    # )

    # this is Claude 3 code
    # result = events_df.groupby("step", maintain_order=True).agg(
    #     [pl.sum(col).alias(f"{col}_sum") for col in risk_factors] +
    #     [pl.mean(col).alias(f"{col}_mean") for col in risk_factors]
    # )
    # print(result.head())
    # return result

def unfurl_and_tally_risk_factors_surgery(df: pl.DataFrame, risk_factors: list[str]) -> pl.DataFrame:
    """
    Unpack, sum, and cumulative sum the values for the given events.

    Parameters
    ----------
    df : pl.DataFrame
        Initial DataFrame
    events : list[str]
        List of columns to be unfurled

    Returns
    -------
    pl.DataFrame
        Unfurled and tallied DataFrame
    """

    df = df.filter(pl.col('bariatric_surgery') == 1)
    surgery_count = df['bariatric_surgery'].sum()

    events_df = df.select(risk_factors)
    events_df = events_df.with_row_index("agent_id")
    events_df = events_df.explode(risk_factors)
    events_df = events_df.with_columns(
        pl.int_range(0, pl.col("agent_id").len()).over("agent_id").alias("step")
    )
    events_df = events_df.filter(pl.col("step") > 0)
    events_df = events_df.drop("agent_id")

    events_df = events_df.group_by("step", maintain_order=True).agg(
        [
            *[(pl.sum(risk_factor) / surgery_count).name.prefix("surgery_mean_") for risk_factor in risk_factors],
        ]
    )

    return events_df