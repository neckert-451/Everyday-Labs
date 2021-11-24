# import python libraries
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
colors = {
    "background": "#F0F8FF",
    "text": "#00008B"
}
# picking the data for the dashboard
df = pd.read_csv("timeseriesplot.csv")
# defining the figure 
# this plot is going to look at the total absences for students, based on the cities that they live in
# this plot also includes a heatmap bar to easily identify high percentages for missed days
fig = px.scatter(df, x="city", y="total_absences", color="percent_missed")
fig.update_layout(
    plot_bgcolor=colors["background"],
    paper_bgcolor=colors["background"],
    font_color=colors["text"]
)
# including some markdown text so it's not so naked 
markdown_text = '''
### Student Absence Dashboard
Creator: Noel Eckert, [LinkedIn](https://www.linkedin.com/in/noel-eckert/), [github](https://github.com/neckert-451)
This plot looks at the distribution of absences across different cities.
Source for data: Everyday Labs
'''
# setting up some simple app layout, pretty basic layout for dash :)
app.layout = html.Div([
    dcc.Markdown(children=markdown_text,
        style={
            "backgroundColor": colors["background"],
            "textAlign": "center",
            "color": colors["text"]
        }),
    
    dcc.Graph(
        id="example-graph",
        figure=fig
    )
])
if __name__ == "__main__":
    app.run_server(debug=True)