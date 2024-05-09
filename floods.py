import dash
from dash import dcc, html, Input, Output, ClientsideFunction
import dash_leaflet as dl
import pandas as pd

# Create an empty DataFrame to store user-reported flood instances
user_data = pd.DataFrame(columns=['Latitude', 'Longitude', 'Severity'])

# Center coordinates for Kenya
kenya_center = [-1.2921, 36.8219]  # Latitude and longitude of Nairobi, the capital city of Kenya

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1('Flood Cases in Kenya'),
    
    # Map displaying flood cases
    dl.Map(
        id='map',
        center=kenya_center,  # Centering the map on Kenya
        zoom=6,
        style={'width': '100%', 'height': '500px'},  # Set map size
        children=[
            dl.TileLayer(),  # Add default tile layer
            dl.LayerGroup(id='user-data', children=[]),  # Empty LayerGroup for user data
            dl.Marker(id='add-marker', position=[0, 0], draggable=True, children=[
                dl.Tooltip(f'Severity: {0}')
            ])
        ],
    ),
    
    # Input form for reporting flood instances
    html.Div([
        dcc.Input(id='map-click', value='', style={'display': 'none'}),
        html.Label('Severity (1-5):'),
        dcc.Input(id='severity-input', type='number', min=1, max=5, value=3),
        html.Button('Add Flood', id='add-button', n_clicks=0),
        html.Div(id='report-message')
    ]),
])

# Callback to update the map with user-reported flood instances
@app.callback(
    [Output('user-data', 'children'), Output('report-message', 'children')],
    [Input('add-button', 'n_clicks')],
    [dash.dependencies.State('map-click', 'value'),
     dash.dependencies.State('severity-input', 'value')]
)
def update_map(n_clicks, lat_lng, severity):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, ''

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'add-button' and lat_lng:
        lat, lng = map(float, lat_lng.split(','))
        user_data.loc[len(user_data)] = [lat, lng, severity]
        message = f'Flood instance added: Latitude - {lat}, Longitude - {lng}, Severity - {severity}'
        print(message)
    else:
        message = ''
    
    markers = []
    for index, row in user_data.iterrows():
        marker = dl.Marker(position=[row['Latitude'], row['Longitude']], children=[
            dl.Tooltip(f'Severity: {row["Severity"]}')
        ])
        markers.append(marker)
    
    return markers, message

# Callback to update the map with the clicked location
@app.callback(
    Output('map-click', 'value'),
    [Input('map', 'click_lat_lng')]
)
def update_map_click(click_lat_lng):
    if click_lat_lng:
        lat, lng = click_lat_lng
        return f'{lat},{lng}'
    else:
        return ''

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
    