import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px

with st.echo(code_location='below'):
    st.title('Olympic Summer & Winter Games')
    @st.cache(allow_output_mutation=True)
    def get_data(url):
        return pd.read_csv(url)

    df_hosts = get_data("https://storage.googleapis.com/kagglesdsdata/datasets/1475786/3445521/olympic_hosts.csv?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20220514%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20220514T101050Z&X-Goog-Expires=259199&X-Goog-SignedHeaders=host&X-Goog-Signature=5011c1eec50142d1abbb036196740465ea137428ae5dcf5d24a7d3909f298597a8ad5531ae7f0724d3051de8301c10e4a7b1bdf8e533037b76d8402c39191577807bb587d0cad1c3d212e7739aa69a62f58ea389af655ce620a796e9f6578fff16fb9300d56d80a7457c0d53bd9028cb6aaef2541a31e24692a7b4f10d6f430b3b436f59ed9ee945cff95df53037ac66193e5bd25c1e7be06da9840cb17891f79daefbf03d519c3b4857bce635d9cf5533ea75d131b0d6a28abe14d41214142699de4dae2634d7fa816c6deb79310f856aed969a9bf5027cc6764452b9e693ae61906832efc7eeceee1f5ff848c3bd18aaacc7dc0a041d6e912508ac9a6b62d1")
    df_medals = get_data("https://github.com/bae24-student/olympic_games/raw/master/olympic_medals.csv")
    df_athletes = get_data("https://github.com/bae24-student/olympic_games/raw/master/olympic_athletes.csv")
    df_more = get_data("https://query.data.world/s/cvsvl2742mgzlkolbxfjnwtkjntkaw")
    df_summer = get_data("https://github.com/bae24-student/olympic_games/raw/master/summer.csv")

    df_hosts["city"] = df_hosts["game_name"].str[0:-5]
    iso = pd.DataFrame({"Nation": df_more["Nation"], "Code": df_more["Code"]})
    df_hosts_iso = df_hosts.merge(iso, left_on='game_location', right_on='Nation', how='left')
    df_hosts_iso.iloc[2, 9] = "KOR"
    df_hosts_iso.iloc[4, 9] = "RUS"
    df_hosts_iso.iloc[17, 9] = "KOR"
    df_hosts_iso.iloc[21, 9] = "RUS"
    df_hosts_iso.iloc[25, 9] = "DEU"
    df_hosts_iso.iloc[33, 9] = "AUS"

    fig = px.scatter_geo(df_hosts_iso, locations="Code", color="game_season",
                         hover_name="game_name",
                         animation_frame="game_year",
                         projection="natural earth")
    st.plotly_chart(fig)

    nations_medals_s = pd.DataFrame({"Nation": df_more["Nation"], "Medal.1": df_more["Medal.1"]}).sort_values(
        "Medal.1",
        ascending=False).set_index(
        "Nation")
    nations_medals_s.loc['Other countries', :] = nations_medals_s.iloc[40:].sum(axis=0)
    other_countries = nations_medals_s.iloc[226]
    nations_medals_s.drop(nations_medals_s.tail(198).index, inplace=True)
    nations_summer = nations_medals_s.append(other_countries).reset_index()

    fig = px.pie(nations_summer, values='Medal.1', names='Nation', title='Total Number of Medals Won on Olympic Games')
    st.plotly_chart(fig)

    season = st.radio(
        "Выберите сезон",
        ('Summer', 'Winter'))

    if season == 'Summer':
        summer = pd.DataFrame(
            {"Nation": df_more["Nation"], "SO_Gold": df_more["SO_Gold"], "SO_Silver": df_more["SO_Silver"],
             "SO_Bronze": df_more["SO_Bronze"]})
        summer.loc[:, 'Total'] = summer.sum(axis=1)
        summer = summer[lambda x: x['Total'] > 0]
        medals_summer = summer.sort_values("Total", ascending=False)[:20]

        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(15, 10))
        sns.set_color_codes()
        sns.barplot(x="SO_Bronze", y="Nation", data=medals_summer,
                    label="Bronze", color="brown", ax=ax)
        sns.set_color_codes()
        sns.barplot(x="SO_Silver", y="Nation", data=medals_summer,
                    label="Silver", color="silver", ax=ax)
        sns.set_color_codes()
        sns.barplot(x="SO_Gold", y="Nation", data=medals_summer,
                    label="Gold", color="gold", ax=ax)
        ax.legend(ncol=2, loc="lower right", frameon=True)
        ax.set(ylabel="", xlabel="Medals for Summer Olympic Games")
        sns.despine(left=True, bottom=True)
        st.pyplot(fig)

        women_summer = df_summer[lambda x: x['Gender'] == "Women"].groupby("Year").agg({"Gender": "count"})
        men_summer = df_summer[lambda x: x['Gender'] == "Men"].groupby("Year").agg({"Gender": "count"})
        men_women = men_summer.merge(women_summer, left_on="Year", right_on="Year", how="left").fillna(int(0))
        men_women.loc[:, 'Total'] = men_women.sum(axis=1)
        women = men_women.reset_index()[["Year", "Gender_y"]].rename(columns={"Gender_y": "Number"})
        women.loc[:, "Gender"] = "Women"
        men = pd.DataFrame(
            {"Year": men_women.reset_index()["Year"], "Gender_x": men_women.reset_index()["Gender_x"]}).rename(
            columns={"Gender_x": "Number"})
        men.loc[:, "Gender"] = "Men"
        men_women_summer = men.append(women).set_index("Year").reset_index()

        pink_blue = alt.Scale(domain=('Men', 'Women'),
                              range=["steelblue", "salmon"])
        chart = alt.Chart(men_women_summer[lambda x: x['Year'] > 1975]).mark_bar().encode(
            x='Gender',
            y='Number',
            color=alt.Color('Gender', scale=pink_blue),
            column='Year'
        )
        st.altair_chart(chart)

        agree = st.checkbox('Нажмите, чтобы посмотреть больший промежуток времени')

        if agree:
            pink_blue = alt.Scale(domain=('Men', 'Women'),
                                  range=["steelblue", "salmon"])
            chart = alt.Chart(men_women_summer).mark_bar().encode(
                x='Gender',
                y='Number',
                color=alt.Color('Gender', scale=pink_blue),
                column='Year'
            )
            st.altair_chart(chart)

    else:
        winter = pd.DataFrame(
            {"Nation": df_more["Nation"], "WO_Gold": df_more["WO_Gold"], "WO_Silver": df_more["WO_Silver"],
             "WO_Bronze": df_more["WO_Bronze"]})
        winter.loc[:, 'Total'] = winter.sum(axis=1)
        winter = winter[lambda x: x['Total'] > 0]
        medals_winter = winter.sort_values("Total", ascending=False)[:20]

        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(15, 10))
        sns.set_color_codes()
        sns.barplot(x="WO_Bronze", y="Nation", data=medals_winter,
                    label="Bronze", color="brown")
        sns.set_color_codes()
        sns.barplot(x="WO_Silver", y="Nation", data=medals_winter,
                    label="Silver", color="silver")
        sns.set_color_codes()
        sns.barplot(x="WO_Gold", y="Nation", data=medals_winter,
                    label="Gold", color="gold")
        ax.legend(ncol=2, loc="lower right", frameon=True)
        ax.set(ylabel="", xlabel="Medals for Winter Olympic Games")
        sns.despine(left=True, bottom=True)
        st.pyplot(fig)


