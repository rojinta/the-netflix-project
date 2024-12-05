import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import cm
from matplotlib.colors import to_hex
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import networkx as nx
from collections import Counter
from itertools import combinations

netflix_data = pd.read_csv('netflix_movies.csv')


# Distribution of Movie Ratings

valid_ratings = [
    'PG-13', 'TV-MA', 'PG', 'TV-14', 'TV-PG', 'TV-Y', 
    'TV-Y7', 'R', 'TV-G', 'G', 'NC-17', 'NR', 'TV-Y7-FV', 'UR'
]

rating_counts = netflix_data['rating'].value_counts()
rating_counts_filtered = rating_counts[rating_counts.index.isin(valid_ratings)]

top_10_ratings = rating_counts_filtered.nlargest(10)

num_ratings = len(top_10_ratings)
dynamic_colors = [to_hex(c) for c in cm.get_cmap('tab20')(range(num_ratings))]

plt.figure(figsize=(10, 8))
plt.pie(
    top_10_ratings,
    labels=top_10_ratings.index,
    startangle=140,
    colors=dynamic_colors
)
plt.title("Distribution of Movie Ratings (Top 10)", fontsize=16)
plt.savefig("distribution_of_movie_ratings.png", dpi=300, bbox_inches='tight')


# Genre Distribution

genres = netflix_data['listed_in'].str.split(',').explode().str.strip()
top_genres = genres.value_counts().head(10)  # Top 10 genres

plt.figure(figsize=(10, 6))
sns.barplot(x=top_genres.values, y=top_genres.index, orient='h', color="skyblue")
plt.title("Genre Distribution (Top 10)", fontsize=16)
plt.xlabel("Count", fontsize=12)
plt.ylabel("Genre", fontsize=12)
plt.savefig("genre_distribution.png", dpi=300, bbox_inches='tight')


# Content Over Time

netflix_data['date_added'] = pd.to_datetime(netflix_data['date_added'], errors='coerce')
netflix_data['year_added'] = netflix_data['date_added'].dt.year
content_by_year = netflix_data.groupby(['year_added', 'type']).size().unstack(fill_value=0)

plt.figure(figsize=(12, 8))
content_by_year.plot(kind='line', figsize=(12, 8), marker='o', color=['green', 'orange'])
plt.title("Content Over Time", fontsize=16)
plt.xlabel("Year Added", fontsize=12)
plt.ylabel("Number of Titles", fontsize=12)
plt.legend(["Movies", "TV Shows"], title="Type", fontsize=10, loc="upper left")
plt.savefig("content_over_time.png", dpi=300, bbox_inches='tight')


# Movie Duration Distribution

movie_durations = netflix_data[netflix_data['type'] == 'Movie']['duration']
movie_durations = movie_durations.str.replace(' min', '').dropna().astype(int)

plt.figure(figsize=(10, 6))
sns.boxplot(
    x=movie_durations,
    color="skyblue",
    flierprops={
        "marker": "o", 
        "markerfacecolor": "grey",
        "markeredgecolor": "grey",
        "markersize": 5
    }
)
plt.title("Movie Duration Distribution", fontsize=16)
plt.xlabel("Duration (Minutes)", fontsize=12)
plt.savefig("movie_duration_distribution.png", dpi=300, bbox_inches='tight')


# Geographical Distribution of Movies

countries = netflix_data['country'].dropna().str.split(',').explode().str.strip()
country_counts = countries.value_counts()

plt.figure(figsize=(12, 8))
sns.barplot(x=country_counts.head(20).values, y=country_counts.head(20).index, orient='h', color="skyblue")
plt.title("Geographical Distribution of Movies (Top 20)", fontsize=16)
plt.xlabel("Number of Titles", fontsize=12)
plt.ylabel("Country", fontsize=12)
plt.savefig("geographical_distribution.png", dpi=300, bbox_inches='tight')


# Choropleth Map

df = pd.read_csv('netflix_movies.csv')
df = df.country.value_counts().reset_index()

processed_counts = {}

for index, row in df.iterrows():
    countries = row['country'].split(", ")
    if len(countries) > 1:
        for country in countries:
            if country in processed_counts:
                processed_counts[country] += row['count']
            else:
                processed_counts[country] = row['count']
    else:
        country = countries[0]
        if country in processed_counts:
            processed_counts[country] += row['count']
        else:
            processed_counts[country] = row['count']

processed_df = pd.DataFrame(list(processed_counts.items()), columns=['country', 'count'])
processed_df = processed_df.sort_values(by='count', ascending=False).reset_index(drop=True)
processed_df['count'] /= processed_df['count'].sum()
processed_df['count'] *= 100
processed_df.rename(columns={'count': 'Share', 'country': 'Country'}, inplace=True)
processed_df.sort_values(by='Share', ascending=False, inplace=True)

countries_2_letter = {"BD": "Bangladesh", "BE": "Belgium", "BF": "Burkina Faso", "BG": "Bulgaria", "BA": "Bosnia and Herzegovina", "BB": "Barbados", "WF": "Wallis and Futuna", "BL": "Saint Barthelemy", "BM": "Bermuda", "BN": "Brunei", "BO": "Bolivia", "BH": "Bahrain", "BI": "Burundi", "BJ": "Benin", "BT": "Bhutan", "JM": "Jamaica", "BV": "Bouvet Island", "BW": "Botswana", "WS": "Samoa", "BQ": "Bonaire, Saint Eustatius and Saba ", "BR": "Brazil", "BS": "Bahamas", "JE": "Jersey", "BY": "Belarus", "BZ": "Belize", "RU": "Russia", "RW": "Rwanda", "RS": "Serbia", "TL": "East Timor", "RE": "Reunion", "TM": "Turkmenistan", "TJ": "Tajikistan", "RO": "Romania", "TK": "Tokelau", "GW": "Guinea-Bissau", "GU": "Guam", "GT": "Guatemala", "GS": "South Georgia and the South Sandwich Islands", "GR": "Greece", "GQ": "Equatorial Guinea", "GP": "Guadeloupe", "JP": "Japan", "GY": "Guyana", "GG": "Guernsey", "GF": "French Guiana", "GE": "Georgia", "GD": "Grenada", "GB": "United Kingdom", "GA": "Gabon", "SV": "El Salvador", "GN": "Guinea", "GM": "Gambia", "GL": "Greenland", "GI": "Gibraltar", "GH": "Ghana", "OM": "Oman", "TN": "Tunisia", "JO": "Jordan", "HR": "Croatia", "HT": "Haiti", "HU": "Hungary", "HK": "Hong Kong", "HN": "Honduras", "HM": "Heard Island and McDonald Islands", "VE": "Venezuela", "PR": "Puerto Rico", "PS": "Palestinian Territory", "PW": "Palau", "PT": "Portugal", "SJ": "Svalbard and Jan Mayen", "PY": "Paraguay", "IQ": "Iraq", "PA": "Panama", "PF": "French Polynesia", "PG": "Papua New Guinea", "PE": "Peru", "PK": "Pakistan", "PH": "Philippines", "PN": "Pitcairn", "PL": "Poland", "PM": "Saint Pierre and Miquelon", "ZM": "Zambia", "EH": "Western Sahara", "EE": "Estonia", "EG": "Egypt", "ZA": "South Africa", "EC": "Ecuador", "IT": "Italy", "VN": "Vietnam", "SB": "Solomon Islands", "ET": "Ethiopia", "SO": "Somalia", "ZW": "Zimbabwe", "SA": "Saudi Arabia", "ES": "Spain", "ER": "Eritrea", "ME": "Montenegro", "MD": "Moldova", "MG": "Madagascar", "MF": "Saint Martin", "MA": "Morocco", "MC": "Monaco", "UZ": "Uzbekistan", "MM": "Myanmar", "ML": "Mali", "MO": "Macao", "MN": "Mongolia", "MH": "Marshall Islands", "MK": "Macedonia", "MU": "Mauritius", "MT": "Malta", "MW": "Malawi", "MV": "Maldives", "MQ": "Martinique", "MP": "Northern Mariana Islands", "MS": "Montserrat", "MR": "Mauritania", "IM": "Isle of Man", "UG": "Uganda", "TZ": "Tanzania", "MY": "Malaysia", "MX": "Mexico", "IL": "Israel", "FR": "France", "IO": "British Indian Ocean Territory", "SH": "Saint Helena", "FI": "Finland", "FJ": "Fiji", "FK": "Falkland Islands", "FM": "Micronesia", "FO": "Faroe Islands", "NI": "Nicaragua", "NL": "Netherlands", "NO": "Norway", "NA": "Namibia", "VU": "Vanuatu", "NC": "New Caledonia", "NE": "Niger", "NF": "Norfolk Island", "NG": "Nigeria", "NZ": "New Zealand", "NP": "Nepal", "NR": "Nauru", "NU": "Niue", "CK": "Cook Islands", "XK": "Kosovo", "CI": "Ivory Coast", "CH": "Switzerland", "CO": "Colombia", "CN": "China", "CM": "Cameroon", "CL": "Chile", "CC": "Cocos Islands", "CA": "Canada", "CG": "Republic of the Congo", "CF": "Central African Republic", "CD": "Democratic Republic of the Congo", "CZ": "Czech Republic", "CY": "Cyprus", "CX": "Christmas Island", "CR": "Costa Rica", "CW": "Curacao", "CV": "Cape Verde", "CU": "Cuba", "SZ": "Swaziland", "SY": "Syria", "SX": "Sint Maarten", "KG": "Kyrgyzstan", "KE": "Kenya", "SS": "South Sudan", "SR": "Suriname", "KI": "Kiribati", "KH": "Cambodia", "KN": "Saint Kitts and Nevis", "KM": "Comoros", "ST": "Sao Tome and Principe", "SK": "Slovakia", "KR": "South Korea", "SI": "Slovenia", "KP": "North Korea", "KW": "Kuwait", "SN": "Senegal", "SM": "San Marino", "SL": "Sierra Leone", "SC": "Seychelles", "KZ": "Kazakhstan", "KY": "Cayman Islands", "SG": "Singapore", "SE": "Sweden", "SD": "Sudan", "DO": "Dominican Republic", "DM": "Dominica", "DJ": "Djibouti", "DK": "Denmark", "VG": "British Virgin Islands", "DE": "Germany", "YE": "Yemen", "DZ": "Algeria", "US": "United States", "UY": "Uruguay", "YT": "Mayotte", "UM": "United States Minor Outlying Islands", "LB": "Lebanon", "LC": "Saint Lucia", "LA": "Laos", "TV": "Tuvalu", "TW": "Taiwan", "TT": "Trinidad and Tobago", "TR": "Turkey", "LK": "Sri Lanka", "LI": "Liechtenstein", "LV": "Latvia", "TO": "Tonga", "LT": "Lithuania", "LU": "Luxembourg", "LR": "Liberia", "LS": "Lesotho", "TH": "Thailand", "TF": "French Southern Territories", "TG": "Togo", "TD": "Chad", "TC": "Turks and Caicos Islands", "LY": "Libya", "VA": "Vatican", "VC": "Saint Vincent and the Grenadines", "AE": "United Arab Emirates", "AD": "Andorra", "AG": "Antigua and Barbuda", "AF": "Afghanistan", "AI": "Anguilla", "VI": "U.S. Virgin Islands", "IS": "Iceland", "IR": "Iran", "AM": "Armenia", "AL": "Albania", "AO": "Angola", "AQ": "Antarctica", "AS": "American Samoa", "AR": "Argentina", "AU": "Australia", "AT": "Austria", "AW": "Aruba", "IN": "India", "AX": "Aland Islands", "AZ": "Azerbaijan", "IE": "Ireland", "ID": "Indonesia", "UA": "Ukraine", "QA": "Qatar", "MZ": "Mozambique"}
countries_3_letter = {"BD": "BGD", "BE": "BEL", "BF": "BFA", "BG": "BGR", "BA": "BIH", "BB": "BRB", "WF": "WLF", "BL": "BLM", "BM": "BMU", "BN": "BRN", "BO": "BOL", "BH": "BHR", "BI": "BDI", "BJ": "BEN", "BT": "BTN", "JM": "JAM", "BV": "BVT", "BW": "BWA", "WS": "WSM", "BQ": "BES", "BR": "BRA", "BS": "BHS", "JE": "JEY", "BY": "BLR", "BZ": "BLZ", "RU": "RUS", "RW": "RWA", "RS": "SRB", "TL": "TLS", "RE": "REU", "TM": "TKM", "TJ": "TJK", "RO": "ROU", "TK": "TKL", "GW": "GNB", "GU": "GUM", "GT": "GTM", "GS": "SGS", "GR": "GRC", "GQ": "GNQ", "GP": "GLP", "JP": "JPN", "GY": "GUY", "GG": "GGY", "GF": "GUF", "GE": "GEO", "GD": "GRD", "GB": "GBR", "GA": "GAB", "SV": "SLV", "GN": "GIN", "GM": "GMB", "GL": "GRL", "GI": "GIB", "GH": "GHA", "OM": "OMN", "TN": "TUN", "JO": "JOR", "HR": "HRV", "HT": "HTI", "HU": "HUN", "HK": "HKG", "HN": "HND", "HM": "HMD", "VE": "VEN", "PR": "PRI", "PS": "PSE", "PW": "PLW", "PT": "PRT", "SJ": "SJM", "PY": "PRY", "IQ": "IRQ", "PA": "PAN", "PF": "PYF", "PG": "PNG", "PE": "PER", "PK": "PAK", "PH": "PHL", "PN": "PCN", "PL": "POL", "PM": "SPM", "ZM": "ZMB", "EH": "ESH", "EE": "EST", "EG": "EGY", "ZA": "ZAF", "EC": "ECU", "IT": "ITA", "VN": "VNM", "SB": "SLB", "ET": "ETH", "SO": "SOM", "ZW": "ZWE", "SA": "SAU", "ES": "ESP", "ER": "ERI", "ME": "MNE", "MD": "MDA", "MG": "MDG", "MF": "MAF", "MA": "MAR", "MC": "MCO", "UZ": "UZB", "MM": "MMR", "ML": "MLI", "MO": "MAC", "MN": "MNG", "MH": "MHL", "MK": "MKD", "MU": "MUS", "MT": "MLT", "MW": "MWI", "MV": "MDV", "MQ": "MTQ", "MP": "MNP", "MS": "MSR", "MR": "MRT", "IM": "IMN", "UG": "UGA", "TZ": "TZA", "MY": "MYS", "MX": "MEX", "IL": "ISR", "FR": "FRA", "IO": "IOT", "SH": "SHN", "FI": "FIN", "FJ": "FJI", "FK": "FLK", "FM": "FSM", "FO": "FRO", "NI": "NIC", "NL": "NLD", "NO": "NOR", "NA": "NAM", "VU": "VUT", "NC": "NCL", "NE": "NER", "NF": "NFK", "NG": "NGA", "NZ": "NZL", "NP": "NPL", "NR": "NRU", "NU": "NIU", "CK": "COK", "XK": "XKX", "CI": "CIV", "CH": "CHE", "CO": "COL", "CN": "CHN", "CM": "CMR", "CL": "CHL", "CC": "CCK", "CA": "CAN", "CG": "COG", "CF": "CAF", "CD": "COD", "CZ": "CZE", "CY": "CYP", "CX": "CXR", "CR": "CRI", "CW": "CUW", "CV": "CPV", "CU": "CUB", "SZ": "SWZ", "SY": "SYR", "SX": "SXM", "KG": "KGZ", "KE": "KEN", "SS": "SSD", "SR": "SUR", "KI": "KIR", "KH": "KHM", "KN": "KNA", "KM": "COM", "ST": "STP", "SK": "SVK", "KR": "KOR", "SI": "SVN", "KP": "PRK", "KW": "KWT", "SN": "SEN", "SM": "SMR", "SL": "SLE", "SC": "SYC", "KZ": "KAZ", "KY": "CYM", "SG": "SGP", "SE": "SWE", "SD": "SDN", "DO": "DOM", "DM": "DMA", "DJ": "DJI", "DK": "DNK", "VG": "VGB", "DE": "DEU", "YE": "YEM", "DZ": "DZA", "US": "USA", "UY": "URY", "YT": "MYT", "UM": "UMI", "LB": "LBN", "LC": "LCA", "LA": "LAO", "TV": "TUV", "TW": "TWN", "TT": "TTO", "TR": "TUR", "LK": "LKA", "LI": "LIE", "LV": "LVA", "TO": "TON", "LT": "LTU", "LU": "LUX", "LR": "LBR", "LS": "LSO", "TH": "THA", "TF": "ATF", "TG": "TGO", "TD": "TCD", "TC": "TCA", "LY": "LBY", "VA": "VAT", "VC": "VCT", "AE": "ARE", "AD": "AND", "AG": "ATG", "AF": "AFG", "AI": "AIA", "VI": "VIR", "IS": "ISL", "IR": "IRN", "AM": "ARM", "AL": "ALB", "AO": "AGO", "AQ": "ATA", "AS": "ASM", "AR": "ARG", "AU": "AUS", "AT": "AUT", "AW": "ABW", "IN": "IND", "AX": "ALA", "AZ": "AZE", "IE": "IRL", "ID": "IDN", "UA": "UKR", "QA": "QAT", "MZ": "MOZ"}

countries_2_letter = pd.DataFrame(countries_2_letter.items(), columns=['iso2', 'name'])
countries_3_letter = pd.DataFrame(countries_3_letter.items(), columns=['iso2', 'iso3'])
countries = pd.merge(countries_2_letter, countries_3_letter, on='iso2', how='inner')[['name', 'iso3']]
countries = countries.dropna()

processed_df = pd.merge(processed_df, countries, left_on='Country', right_on='name', how='right')[['name', 'Share', 'iso3']].fillna(0).rename(columns={'name': 'Country'})
processed_df.sort_values(by='Share', ascending=False, inplace=True)
processed_df.head(5)

fig = px.choropleth(
    processed_df,
    locations="Country",
    locationmode="country names",
    color="Share",
    color_continuous_scale=px.colors.sequential.Viridis,
    range_color=(0, 15),
    title="Geographical Distribution of Movies"
)
fig.update_layout(
    title={
        'text': "Geographical Distribution of Movies",
        'x': 0.5,
        'xanchor': 'center',
        'font': {'color': 'black', 'size': 18}
    },
    width=1000,
    height=500,
    margin=dict(l=10, r=10, t=50, b=10),
    coloraxis_colorbar=dict(
        title="Share (%)",
        titlefont=dict(color="black"),
        tickfont=dict(color="black")
    )
)
fig.update_traces(
    hovertemplate="<b>%{location}</b><br>Count: %{z}%<extra></extra>"
)
output_file = "choropleth_map.png"
fig.write_image(output_file, format="png", scale=2) 


# Word Cloud of Movie Titles

titles = ' '.join(netflix_data['title'].dropna())
wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(titles)

plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title("Word Cloud of Movie Titles", fontsize=16)
plt.savefig("word_cloud.png", dpi=300, bbox_inches='tight')


# Co-appearance Network of Cast Members

cast = netflix_data['cast'].dropna().str.split(',').explode().str.strip()
cast_pairs = netflix_data['cast'].dropna().apply(lambda x: list(map(str.strip, x.split(','))))
edges = [tuple(sorted(pair)) for pairs in cast_pairs for pair in combinations(pairs, 2)]

edge_counts = Counter(edges)
filtered_edges = [(a, b) for (a, b), count in edge_counts.items() if count > 1]

top_cast = cast.value_counts().head(50).index
filtered_edges = [(a, b) for (a, b) in filtered_edges if a in top_cast and b in top_cast]

small_graph = nx.Graph()
small_graph.add_edges_from(filtered_edges)

node_degrees = dict(small_graph.degree())
pos_spaced_further = nx.spring_layout(small_graph, seed=42, k=0.5)
plt.figure(figsize=(16, 16))
ax = plt.gca()
nx.draw_networkx_nodes(
    small_graph, pos_spaced_further,
    node_size=[node_degrees[node] * 40 for node in small_graph.nodes()],
    node_color='skyblue',
    alpha=0.8
)
nx.draw_networkx_edges(small_graph, pos_spaced_further, edge_color='gray', alpha=0.5)
nx.draw_networkx_labels(
    small_graph, pos_spaced_further,
    font_size=7, font_color='black'
)
plt.title("Co-appearance Network of Cast Members (Top 50)", fontsize=16)

border = patches.Rectangle(
    (0, 0), 1, 1,
    linewidth=1, edgecolor='black', facecolor='none', transform=ax.transAxes,
    clip_on=False
)
ax.add_patch(border)

plt.axis('off')
plt.savefig("coappearance_network.png", dpi=150, bbox_inches='tight')


# Release Trends by Country Over Time

country_year = netflix_data.groupby(['year_added', 'country']).size().unstack(fill_value=0)

top_countries = country_year.sum().sort_values(ascending=False).head(10).index
country_year_top = country_year[top_countries]

custom_colors = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]

plt.figure(figsize=(14, 8))
country_year_top.plot.area(alpha=0.8, figsize=(14, 8), color=custom_colors)
plt.title("Release Trends by Country Over Time", fontsize=16)
plt.xlabel("Year Added", fontsize=12)
plt.ylabel("Number of Titles", fontsize=12)
plt.legend(title="Country", fontsize=10, loc="upper left")
plt.savefig("release_trends.png", dpi=300, bbox_inches='tight')
