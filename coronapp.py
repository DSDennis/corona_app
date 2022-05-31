#!/usr/bin/env python
# coding: utf-8

# In[1]:


# db = "./covid-19-data/us-counties.csv"
db = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"

default_date_for_map = "2020-03-11"

# database file downloaded from
# https://www.weather.gov/source/gis/Shapefiles/County/c_03mr20.zip
# to get the lat and long values for US counties
dbf = "./c_03mr20.dbf"


# In[2]:

pip install simpledbf
from simpledbf import Dbf5
import pandas as pd
import streamlit as st
from datetime import datetime, date
from numpy import insert


def get_county_key(df, state):
    return df[df.state == state].county.unique()


def get_state_key(df):
    return sorted(df.state.unique())


def get_fips():
    xdbf = Dbf5(dbf)
    fips_df = xdbf.to_dataframe()
    fips_df["FIPS"] = fips_df["FIPS"].astype(float)
    return fips_df.loc[:, ["FIPS", "LON", "LAT"]]


def df_left_merge(left_df, right_df):
    return left_df.merge(right_df, left_on="fips", right_on="FIPS", how="left")


def df_clean(ff):
    ff1 = ff.rename(columns={"LON": "lon", "LAT": "lat"})
    return ff1.dropna()


@st.cache
def get_coord(df):
    df1 = get_fips()
    merged_df = df_left_merge(df, df1)
    clean_df = df_clean(merged_df)
    return clean_df

#have removed the @st.cache function as raised an error

def get_data():
    df = pd.read_csv(db)
    df["date"] = pd.to_datetime(df["date"])
    return df


def filter_data_by_county_state(df, co, st):
    if (co == "All") & (st == "All"):
        return df
    elif co == "All":
        return df[df.state == st]
    elif st == "All":
        return df[df.county == co]
    else:
        return df[(df.state == st) & (df.county == co)]


# In[3]:


def draw_tot_cases_graph(df):
    tot_cases_by_day = df.groupby("date")["cases"].sum()
    st.write("Total cases(US):")
    st.line_chart(tot_cases_by_day)


def draw_daily_cases_graph(df):
    cases_by_day = df.groupby("date")["cases"].sum().reset_index(name="cases")
    shifted = cases_by_day["cases"].shift(1)
    cases_by_day["daily_cases"] = cases_by_day["cases"] - shifted
    cases_by_day.drop(columns=["cases"], axis=1, inplace=True)
    cases_by_day.set_index("date", inplace=True)
    st.write("Daily cases(US):")
    st.bar_chart(cases_by_day)


def draw_tot_deaths_graph(df):
    tot_cases_by_day = df.groupby("date")["deaths"].sum()
    st.write("Total deaths(US):")
    st.line_chart(tot_cases_by_day)


def draw_daily_deaths_graph(df):
    cases_by_day = df.groupby("date")["deaths"].sum().reset_index(name="deaths")
    shifted = cases_by_day["deaths"].shift(1)
    cases_by_day["daily_deaths"] = cases_by_day["deaths"] - shifted
    cases_by_day.drop(columns=["deaths"], axis=1, inplace=True)
    cases_by_day.set_index("date", inplace=True)
    st.write("Daily deaths(US):")
    st.bar_chart(cases_by_day)


def draw_county_state_cases_graph(df, co, state):
    county_state_cases_by_day = df.groupby("date")["cases"].sum()
    st.write(f"Total cases({co}, {state}):")
    st.line_chart(county_state_cases_by_day)


def draw_daily_county_state_cases_graph(df, co, state):
    cases_by_day = df.groupby("date")["cases"].sum().reset_index(name="cases")
    shifted = cases_by_day["cases"].shift(1)
    cases_by_day["daily_cases"] = cases_by_day["cases"] - shifted
    cases_by_day.loc[cases_by_day.daily_cases < 0, "daily_cases"] = 0
    cases_by_day.drop(columns=["cases"], axis=1, inplace=True)
    cases_by_day.set_index("date", inplace=True)
    st.write(f"Daily cases({co}, {state}):")
    st.bar_chart(cases_by_day)


def draw_county_state_deaths_graph(df, co, state):
    county_state_deaths_by_day = df.groupby("date")["deaths"].sum()
    st.write(f"Total deaths({co}, {state}):")
    st.line_chart(county_state_deaths_by_day)


def draw_daily_county_state_deaths_graph(df, co, state):
    cases_by_day = df.groupby("date")["deaths"].sum().reset_index(name="deaths")
    shifted = cases_by_day["deaths"].shift(1)
    cases_by_day["daily_deaths"] = cases_by_day["deaths"] - shifted
    cases_by_day.loc[cases_by_day.daily_deaths < 0, "daily_deaths"] = 0
    cases_by_day.drop(columns=["deaths"], axis=1, inplace=True)
    cases_by_day.set_index("date", inplace=True)
    st.write(f"Daily deaths({co}, {state}):")
    st.bar_chart(cases_by_day)


def draw_map(df, state, co, date):
    st_co_data_for_date = df[df.date.dt.date == date]
    st.subheader(f"Map of CoVid cases on {date} for {co}, {state}")
    st.map(st_co_data_for_date)
    st.write(f"{len(st_co_data_for_date.index)} counties affected in {co}, {state}")
    st.write(
        f"Total deaths in {co}, {state} till {date} : {st_co_data_for_date['deaths'].sum()}"
    )
    st.write(
        f"Total cases in {co}, {state} till {date} : {st_co_data_for_date['cases'].sum()}"
    )


# In[4]:


covid_data = get_data()


st.title("Covid Dataset")

nav_link = st.sidebar.radio("Navigation", ("Home", "US Trends", "Local Trends"))

if nav_link == "Home":
    st.header(
        "This app is to create a dashboard for Covid dataset provide by New York Times."
    )

elif nav_link == "US Trends":
    st.header("US Trends")
    draw_tot_cases_graph(covid_data)
    draw_tot_deaths_graph(covid_data)
    draw_daily_cases_graph(covid_data)
    draw_daily_deaths_graph(covid_data)

elif nav_link == "Local Trends":
    cov_coord = get_coord(covid_data)
    st.header("Local Trends")

    state_key = get_state_key(cov_coord)
    # state_key = insert(state_key, 0, "All")
    st.sidebar.header(f"Choose your county and state below:")
    state = st.sidebar.selectbox("Select your state ", state_key)
    county_key = get_county_key(cov_coord, state)
    county_key = insert(county_key, 0, "All")
    county = st.sidebar.selectbox("Select your county ", county_key)

    st_co_data = filter_data_by_county_state(covid_data, county, state)

    if not st_co_data.empty:
        draw_county_state_cases_graph(st_co_data, county, state)
        draw_county_state_deaths_graph(st_co_data, county, state)
        draw_daily_county_state_cases_graph(st_co_data, county, state)
        draw_daily_county_state_deaths_graph(st_co_data, county, state)
        date_to_filter = st.date_input(
            "Check for date",
            datetime.strptime(default_date_for_map, "%Y-%m-%d").date(),
        )
        map_st_co_data = filter_data_by_county_state(cov_coord, county, state)
        draw_map(map_st_co_data, state, county, date_to_filter)
    else:
        st.write("This combination is invalid!!!")

