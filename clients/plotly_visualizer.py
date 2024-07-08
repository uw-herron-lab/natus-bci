import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from collections import deque
from plotly.subplots import make_subplots
from client_sub import ClientSub

# Plotly/Dash-based Subscriber for Real-Time Plotting
class PlotlyDash(ClientSub):
    def __init__(self, sub_ip="localhost", sub_port=1000, sub_topic="ProcessedData", n_channels : int = 1):
        super().__init__(sub_ip, sub_port, sub_topic)
        
        # Dash app setup
        self.app = dash.Dash(__name__)
        self.app.layout = html.Div([
            dcc.Graph(id='live-graph', style={'height': '90vh', 'overflowY': 'scroll'}),
            dcc.Interval(id='graph-update', interval=200, n_intervals=0)  # Update every second
        ])
        
        # Store data for each channel
        self.n_channels = n_channels
        self.data = [[] for _ in range(self.n_channels)]

        # Initialize callback for graph updates
        self.app.callback(
            Output('live-graph', 'figure'),
            Input('graph-update', 'n_intervals')
        )(self.update_plot)
    
    def update_plot(self, n_intervals):
        try:
            samplestamps, samples = self.get_data()
            
            for i in range(self.n_channels):
                self.data[i].extend(samples[:, i])

            print("Got Data!")
        except Exception as e:
            print(f"Did not get data: {e}")

        data_length = len(self.data[0])
        x_start = max(0, data_length - 2000)
        x_end = max(2000, data_length)
        
        # Create a figure with subplots
        fig = make_subplots(rows=self.n_channels, cols=1, 
                            subplot_titles=[f"Channel {i+1}" for i in range(self.n_channels)],
                            shared_xaxes=True, 
                            vertical_spacing=.025)

        for i in range(self.n_channels):
            fig.add_trace(go.Scatter(
                x=list(range(x_start, x_end)),
                y=list(self.data[i])[x_start:x_end],
                mode='lines',
                name=f'Channel {i+1}'
            ), row=i+1, col=1)
        
        # Update layout for better visualization
        fig.update_layout(
            title='Real-Time Data Streaming',
            xaxis_title='Sample Index',
            yaxis_title='Value',
            xaxis=dict(range=[x_start, x_end]),  # Limit the x-axis to the most recent 2000 points
            yaxis=dict(autorange=True),
            showlegend=True,
            height=450 * self.n_channels
        )

        return fig
    
    def plot_data(self):
        # Run the Dash app
        self.app.run_server(debug=True, use_reloader=False)  # use_reloader=False to avoid multiple instances

if __name__ == "__main__":
    subscriber = PlotlyDash(n_channels=2)
    subscriber.plot_data()
