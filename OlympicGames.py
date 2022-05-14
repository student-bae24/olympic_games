import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px

with st.echo(code_location='below'):
    st.title('Проект по визуализации данных: "Зимние и летние Олимпийские игры"')
    @st.cache(allow_output_mutation=True)
    def get_data(url):
        return pd.read_csv(url)

    df_hosts = get_data("https://storage.googleapis.com/kagglesdsdata/datasets/1475786/3445521/olympic_hosts.csv?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20220514%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20220514T101050Z&X-Goog-Expires=259199&X-Goog-SignedHeaders=host&X-Goog-Signature=5011c1eec50142d1abbb036196740465ea137428ae5dcf5d24a7d3909f298597a8ad5531ae7f0724d3051de8301c10e4a7b1bdf8e533037b76d8402c39191577807bb587d0cad1c3d212e7739aa69a62f58ea389af655ce620a796e9f6578fff16fb9300d56d80a7457c0d53bd9028cb6aaef2541a31e24692a7b4f10d6f430b3b436f59ed9ee945cff95df53037ac66193e5bd25c1e7be06da9840cb17891f79daefbf03d519c3b4857bce635d9cf5533ea75d131b0d6a28abe14d41214142699de4dae2634d7fa816c6deb79310f856aed969a9bf5027cc6764452b9e693ae61906832efc7eeceee1f5ff848c3bd18aaacc7dc0a041d6e912508ac9a6b62d1")
    df_medals = get_data("https://github.com/bae24-student/olympic_games/raw/master/olympic_medals.csv")
    df_more = get_data("https://query.data.world/s/cvsvl2742mgzlkolbxfjnwtkjntkaw")
    df_summer = get_data("https://github.com/bae24-student/olympic_games/raw/master/summer.csv")
    df_winter = get_data("https://storage.googleapis.com/kagglesdsdata/datasets/707/1330/winter.csv?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20220514%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20220514T144623Z&X-Goog-Expires=259199&X-Goog-SignedHeaders=host&X-Goog-Signature=6c16027b4a29a73c064eb5a9ca5f2118d53bc9ba6d501cb36416dcf8314914e877943ab095407e7f742620d7ccecf5fc77270796b322c8896b8d3b0118fa8258e4410878a446ec1b493cce48997cb1fde1c0b1af3e70b773ab265209e9ecf370967ef735c6b560c805ba21bcc000d5b5541bb45fea92b52e1cda61fd5b031558dd9ac8b144af895874b0841ae0feb55da2f514aef5d567bc3805da8ccc94da17dcf9949dd7e7ba99ffa35b3a687ceeac730d2f63ee965cb0a88935eafc27e5144679ad029070ed6ddc1efcb15cd437564041beb53146a0c0acddd31cd0600d6fdacf6d40dc94cdcd9bbc35b0dcb42c12a5704d49dfc1b6a1c39b8dd0aca2d7bd")

    """Данный проект посвящён анализу и визуализации данных о зимних и летних Олимпийских играх за весь период их проведения: с 1896 по 2022 год."""

    df_hosts["city"] = df_hosts["game_name"].str[0:-5]
    iso = pd.DataFrame({"Nation": df_more["Nation"], "Code": df_more["Code"]})
    df_hosts_iso = df_hosts.merge(iso, left_on='game_location', right_on='Nation', how='left')
    df_hosts_iso.iloc[2, 9] = "KOR"
    df_hosts_iso.iloc[4, 9] = "RUS"
    df_hosts_iso.iloc[17, 9] = "KOR"
    df_hosts_iso.iloc[21, 9] = "RUS"
    df_hosts_iso.iloc[25, 9] = "DEU"
    df_hosts_iso.iloc[33, 9] = "AUS"

    """Ниже представлена карта с местами проведения всех Олимпийских игр. Вы можете выбрать нужный год и посмотреть информацию о событии, наведя курсор на точку."""

    fig = px.scatter_geo(df_hosts_iso, locations="Code", color="game_season",
                         hover_name="game_name",
                         animation_frame="game_year",
                         projection="natural earth")
    st.plotly_chart(fig)

    """Теперь предлагаю посмотреть распределение медалей между странами за всё время проведения соревнований. Вы можете убрать неинтересующие вас страны, кликнув на квадрат около их названий и оставив нужное количество стран."""

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

    st.write("### Top 10 countries in 10 different disciplines")

    """Следующая визуализация демонстрирует распределение медалей между десятью странами в десяти различных дисциплинах."""

    medals = df_medals.groupby(["country_name", "discipline_title"]).agg({"medal_type": "count"}).pivot_table(
        index='country_name', columns='discipline_title', values='medal_type').fillna(0)
    medals.loc[:, 'Total'] = medals.sum(axis=1)
    medals_disciplines = medals.sort_values("Total", ascending=False).loc[
        ["United States of America", "Soviet Union", "Germany", "Great Britain", "France", "People's Republic of China",
         "Italy", "Sweden", "Australia", "Canada"], ["Athletics", "Fencing", "Gymnastics Artistic", "Judo", "Rowing",
                                                     "Sailing", "Shooting", "Swimming", "Weightlifting", "Wrestling"]]

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(medals_disciplines.T.astype(int), annot=True, fmt="d", linewidths=.5, cmap="BuPu", ax=ax)
    st.pyplot(fig)

    """Теперь рассмотрим отдельно летние и зимние Олимпийские игры."""

    season = st.radio(
        "Выберите сезон",
        ('Лето', 'Зима'))

    if season == 'Лето':

        """Ниже представлено распределение золотых, серебрянных и бронзовых медалей между первыми десятью странами за всё время проведения летних Олимпийских игр."""

        summer = pd.DataFrame(
            {"Nation": df_more["Nation"], "SO_Gold": df_more["SO_Gold"], "SO_Silver": df_more["SO_Silver"],
             "SO_Bronze": df_more["SO_Bronze"]})
        summer.loc[:, 'Total'] = summer.sum(axis=1)
        summer = summer[lambda x: x['Total'] > 0]
        medals_summer = summer.sort_values("Total", ascending=False)[:10]
        gold = medals_summer[["Nation", "SO_Gold"]].rename(columns={"SO_Gold": "Number"})
        gold.loc[:, "Type"] = "Gold"
        silver = pd.DataFrame({"Nation": medals_summer["Nation"], "SO_Silver": medals_summer["SO_Silver"]}).rename(
            columns={"SO_Silver": "Number"})
        silver.loc[:, "Type"] = "Silver"
        bronze = pd.DataFrame({"Nation": medals_summer["Nation"], "SO_Bronze": medals_summer["SO_Bronze"]}).rename(
            columns={"SO_Bronze": "Number"})
        bronze.loc[:, "Type"] = "Bronze"
        medals_summer = gold.append(silver).append(bronze).set_index("Nation").reset_index()

        colors = alt.Scale(domain=('Gold', 'Silver', 'Bronze'),
                           range=["gold", "silver", "brown"])
        chart = alt.Chart(medals_summer).mark_bar().encode(
            x='Number',
            y=alt.Y('Type', title=None),
            color=alt.Color('Type', scale=colors),
            row='Nation'
        )
        st.altair_chart(chart)

        """Теперь посмотрим на соотношение мужчин и женщин среди медалистов летних Олимпийских игр. Ниже представлен период с 1976 по 2012. Распределение для более ранних периодов можно посмотреть, поставив галочку ниже."""

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
            x=alt.X('Gender', title=None),
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
                x=alt.X('Gender', title=None),
                y='Number',
                color=alt.Color('Gender', scale=pink_blue),
                column='Year'
            )
            st.altair_chart(chart)

    else:

        """Ниже представлено распределение золотых, серебрянных и бронзовых медалей между первыми десятью странами за всё время проведения зимних Олимпийских игр."""

        winter = pd.DataFrame(
            {"Nation": df_more["Nation"], "WO_Gold": df_more["WO_Gold"], "WO_Silver": df_more["WO_Silver"],
             "WO_Bronze": df_more["WO_Bronze"]})
        winter.loc[:, 'Total'] = winter.sum(axis=1)
        winter = winter[lambda x: x['Total'] > 0]
        medals_winter = winter.sort_values("Total", ascending=False)[:10]
        gold = medals_winter[["Nation", "WO_Gold"]].rename(columns={"WO_Gold": "Number"})
        gold.loc[:, "Type"] = "Gold"
        silver = pd.DataFrame({"Nation": medals_winter["Nation"], "WO_Silver": medals_winter["WO_Silver"]}).rename(
            columns={"WO_Silver": "Number"})
        silver.loc[:, "Type"] = "Silver"
        bronze = pd.DataFrame({"Nation": medals_winter["Nation"], "WO_Bronze": medals_winter["WO_Bronze"]}).rename(
            columns={"WO_Bronze": "Number"})
        bronze.loc[:, "Type"] = "Bronze"
        medals_winter = gold.append(silver).append(bronze).set_index("Nation").reset_index()

        colors = alt.Scale(domain=('Gold', 'Silver', 'Bronze'),
                           range=["gold", "silver", "brown"])
        chart = alt.Chart(medals_winter).mark_bar().encode(
            x='Number',
            y=alt.Y('Type', title=None),
            color=alt.Color('Type', scale=colors),
            row='Nation'
        )
        st.altair_chart(chart)

        """Теперь посмотрим на соотношение мужчин и женщин среди медалистов зимних Олимпийских игр. Ниже представлен период с 1976 по 2012. Распределение для более ранних лет можно посмотреть, поставив галочку ниже."""

        women_winter = df_winter[lambda x: x['Gender'] == "Women"].groupby("Year").agg({"Gender": "count"})
        men_winter = df_winter[lambda x: x['Gender'] == "Men"].groupby("Year").agg({"Gender": "count"})
        men_women = men_winter.merge(women_winter, left_on="Year", right_on="Year", how="left").fillna(int(0))
        men_women.loc[:, 'Total'] = men_women.sum(axis=1)
        women = men_women.reset_index()[["Year", "Gender_y"]].rename(columns={"Gender_y": "Number"})
        women.loc[:, "Gender"] = "Women"
        men = pd.DataFrame(
            {"Year": men_women.reset_index()["Year"], "Gender_x": men_women.reset_index()["Gender_x"]}).rename(
            columns={"Gender_x": "Number"})
        men.loc[:, "Gender"] = "Men"
        men_women_winter = men.append(women).set_index("Year").reset_index()

        pink_blue = alt.Scale(domain=('Men', 'Women'),
                              range=["steelblue", "salmon"])
        chart = alt.Chart(men_women_winter[lambda x: x['Year'] > 1975]).mark_bar().encode(
            x=alt.X('Gender', title=None),
            y='Number',
            color=alt.Color('Gender', scale=pink_blue),
            column='Year'
        )
        st.altair_chart(chart)

        agree = st.checkbox('Нажмите, чтобы посмотреть больший промежуток времени')

        if agree:
            pink_blue = alt.Scale(domain=('Men', 'Women'),
                                  range=["steelblue", "salmon"])
            chart = alt.Chart(men_women_winter).mark_bar().encode(
                x=alt.X('Gender', title=None),
                y='Number',
                color=alt.Color('Gender', scale=pink_blue),
                column='Year'
            )
            st.altair_chart(chart)

    st.write("### Спасибо за внимание! 😌")