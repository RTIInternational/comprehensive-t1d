import pandas as pd


def tally_events(df, event):
    """
    Sum a grouped column

    :param df: Initial DataFrame
    :param event: Name of column to be unfurled
    :return: Unfurled dataframe
    """
    return df.groupby(['step'])[event].sum()


def tally_chronic_events(df, event):
    """
    Sum a grouped column

    :param df: Initial DataFrame
    :param event: Name of column to be unfurled
    :return: Unfurled dataframe
    """

    return df.groupby(['step'])[event].sum()


def unfurl_and_tally_events(df, event):
    """
    Unpack and tally a dataframe column

    :param df: Initial DataFrame
    :param event: Name of column to be unfurled
    :return: Unfurled dataframe
    """
    return tally_events(unfurl_events(df, event), event)


def unfurl_and_tally_chronic_events(df, event):
    """
    Unpack and tally a dataframe column

    :param df: Initial DataFrame
    :param event: Name of column to be unfurled
    :return: Unfurled dataframe
    """
    return tally_chronic_events(unfurl_chronic_events(df, event), event)


def unfurl_events(df, event):
    """
    Unpack a nested list by converting each entry to a DataFrame row.

    :param df: Initial DataFrame
    :param event: Name of column to be unfurled
    :return: Unfurled dataframe
    """
    rows = []

    def _apply(row):
        for i, b in enumerate(row[event]):
            # Data stored at index 0 is baseline, before conducting the simulation.
            # Since analysis is only concerned with data coming from the simulation,
            # we skip this baseline value.
            if i == 0:
                continue
            if event == 'qaly':
                rows.append([i, b])
            else:
                rows.append([i, int(b)])

    df.apply(_apply, axis=1)

    return pd.DataFrame(rows, columns=['step', event])


def unfurl_chronic_events(df, event):
    """
    Unpack a nested list by converting each entry to a DataFrame row.

    :param df: Initial DataFrame
    :param event: Name of column to be unfurled
    :return: Unfurled dataframe
    """
    rows = []

    def _apply(row):
        event_list = row[event]
        # only count incidence for t0=0; if a chronic condition already exists (t0=1), skip
        if event_list[0] == 0:
            try:
                # Find the index of the first 1
                first_one_index = event_list.index(1)
                # Replace the rest of the 1s with 0
                event_list[first_one_index + 1:] = [0] * (len(event_list) - first_one_index - 1)
            except ValueError:
                event_list = [0] * (len(event_list))
        else:
            event_list = [0] * (len(event_list))
        for i, b in enumerate(event_list):
            # Data stored at index 0 is baseline, before conducting the simulation.
            # Since analysis is only concerned with data coming from the simulation,
            # we skip this baseline value.
            if i == 0:
                continue
            if event == 'qaly':
                rows.append([i, b])
            else:
                rows.append([i, int(b)])

    df.apply(_apply, axis=1)

    return pd.DataFrame(rows, columns=['step', event])