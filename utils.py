import chess
import chess.svg
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit_antd_components as sac

st.cache_data
def load_data():
    return pd.read_csv('games_revisited.csv')


def plot_ranking(data):
    # Combine the white and black ratings into one series
    combined_ratings = pd.concat([data['white_rating'], data['black_rating']])
    # Count the frequency of each rating
    rating_count = combined_ratings.value_counts().reset_index()
    rating_count.columns = ['Rating', 'Frequency']
    # Sort the ratings by the rating value
    sorted_ratings = rating_count.sort_values(by='Rating').reset_index(drop=True)
    # Create a DataFrame for plotting
    chart_data = pd.DataFrame({
        "Rating": sorted_ratings['Rating'],
        "Frequency": sorted_ratings['Frequency']})
    return chart_data


def plot_winning_rates(data):
    if data.empty:
        st.sidebar.write("No data available for the selected category.")
        return None
    winner_counts = data['winner'].value_counts().reset_index()
    winner_counts.columns = ['winner', 'counts']
    category = data['time_control_category'].iloc[0] if not data.empty else "Selected Category"
    fig = px.pie(winner_counts, values='counts', names='winner', title=f'Winning Rates in {category}',
                color='winner', color_discrete_map={'white': '#E2E2E2', 'black': '#22223B', 'draw': '#2A9D8F'})
    return fig


def plot_top_openings(data, sort_by='winning_rate'):
    openings_count = data.groupby(['opening_name', 'winner']).size().unstack(fill_value=0).reset_index()
    title = 'Top 5 Openings by Winning Rate'
    if sort_by == 'winning_rate':
        openings_count = openings_count.nlargest(5, ['white', 'black'])
    fig = px.bar(openings_count, y='opening_name', x=['white', 'black'],
                title=title,
                labels={'value': 'Number of Wins', 'variable': 'Winner'},
                color_discrete_sequence=['#E2E2E2', '#22223B'],
                barmode='group', height=400, orientation='h')
    fig.update_traces(marker_line_width=0.5)
    return fig




def plot_most_played_openings(data):
    openings_count = data['opening_name'].value_counts().reset_index()
    openings_count.columns = ['Opening Name', 'Number of Games Played']
    openings_count = openings_count.nlargest(5, 'Number of Games Played')
    
    # Define a list of colors for the bars
    custom_colors = ['#FFBE0B', '#FB5607', '#FF006E', '#8338EC', '#3A86FF']
    # Assign each opening a color based on its position
    openings_count['color'] = custom_colors[:len(openings_count)]
    
    # Create a bar chart with custom colors
    fig = px.bar(openings_count, x='Opening Name', y='Number of Games Played',
                 title='Top 5 Most Played Openings',
                 height=550, orientation='v',
                 color='color',  # Use the color column to apply colors
                 color_discrete_map={color: color for color in custom_colors})  # Map each color to itself
    
    # Update text position to be outside the bar for better readability
    fig.update_traces(textposition='outside')
    
    # Hide the color legend since colors are explicitly set
    fig.update_layout(showlegend=False)
    
    # Update axis labels
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Number of Games Played"
    )
    return fig,openings_count


def display_opening_details(data, opening_name):
    opening_data = data[data['opening_name'] == opening_name]
    most_winning_color = opening_data['winner'].mode().iloc[0] if not opening_data.empty else 'N/A'
    most_played_time_category = opening_data['time_control_category'].mode().iloc[0] if not opening_data.empty else 'N/A'
    games_count = len(opening_data)
    details = {
        "Opening PLY": [opening_data['opening_ply'].iloc[0] if 'opening_ply' in opening_data.columns and not opening_data.empty else 'N/A'],
        "Game Number": [games_count],
        "Most Winner Color": [most_winning_color],
        "Most Played Time category": [most_played_time_category]
    }
    details_df = pd.DataFrame(details)
    st.dataframe(details_df, hide_index = True)
    

def display_chess_board(board, arrows=None):
    return chess.svg.board(board=board, size=350, arrows=arrows)

def update_chess_board(moves, current_move_index):
    board = chess.Board()
    last_move = None
    for move in moves[:current_move_index + 1]:
        last_move = board.push_san(move)  # Push move in standard algebraic notation
    return board, last_move


def plot_time_control_cat(game_data, selected_opening):
    opening_data = game_data[game_data['opening_name'] == selected_opening]
    if not opening_data.empty:
        # Calculate the percentage of each category
        category_percentage = opening_data['time_control_category'].value_counts(normalize=True) * 100
        # Convert to DataFrame for better handling in Plotly
        df_category_percentage = pd.DataFrame({ 'Time Control Category': category_percentage.index,
                                                'Percentage': category_percentage.values })
        # Define custom color sequence for the categories
        custom_colors = ['#FFAFCC', '#BDE0FE', '#84A98C', '#FDFCDC']
        # Create the pie chart
        fig = px.pie(df_category_percentage,
                    names='Time Control Category',
                    values='Percentage',
                    color='Time Control Category',
                    color_discrete_sequence=custom_colors,
                    labels={'Time Control Category': 'Category', 'Percentage': 'Percentage'})
        # Adjust legend positioning and plot dimensions
        fig.update_layout(
            width=700,  # Adjust the width to fit within your Streamlit container
            height=400,
            legend=dict( title="Categories", x=0.1, xanchor="center", yanchor="top", orientation="v"))
        st.plotly_chart(fig)
    else:
        st.write(f"No data available for the opening: {selected_opening}")


def plot_winners_cat(include_draws,game_data, selected_opening):
    opening_data = game_data[game_data['opening_name'] == selected_opening]
    if not opening_data.empty:
        if not include_draws:
            # Exclude draws if checkbox is unchecked
            opening_data = opening_data[opening_data['winner'] != 'draw']
        if not opening_data.empty:
            winner_percentage = opening_data['winner'].value_counts(normalize=True) * 100
            # Convert the Series to a DataFrame for Plotly
            df_winner_percentage = pd.DataFrame({
                'Winner': winner_percentage.index,
                'Percentage': winner_percentage.values})
            # Define the color map only if it is needed
            color_map = {'white': '#E2E2E2', 'black': '#22223B', 'draw': '#2A9D8F'}
            # Filter out the draw color if draws are not included
            if not include_draws:
                color_map.pop('draw', None)  # Remove 'draw' key if it exists
            fig = px.pie(df_winner_percentage, names='Winner', values='Percentage',
                        color='Winner', color_discrete_map={'white': '#E2E2E2', 'black': '#22223B', 'draw': '#2A9D8F'})
            fig.update_layout(
                width=700,  # Adjust the width to fit within your Streamlit container
                height=400,
                legend=dict(title="Categories", x=0.1, xanchor="center", yanchor="top", orientation="v"))
            st.plotly_chart(fig)
        else:
            st.write(f"No relevant data available for the opening: {selected_opening}")
    else:
        st.write(f"No data available for the opening: {selected_opening}")
        
        
def display_moves_list(op_data, selected_opening, game_data):
    try:
        # Retrieve the moves string for the selected opening
        moves_str = op_data.loc[op_data['opening_name'] == selected_opening, 'moves'].iloc[0]
        opening_ply = game_data.loc[game_data['opening_name'] == selected_opening, 'opening_ply'].iloc[0]
        # Split the string into individual moves
        moves = moves_str.split()
        # Limit moves to the opening ply number
        moves_limited = moves[:opening_ply]

        # Create pairs of moves (White and Black)
        move_pairs = [(moves_limited[i], moves_limited[i+1] if i+1 < len(moves_limited) else '') for i in range(0, len(moves_limited), 2)]

        # Create DataFrame from move pairs
        df_moves = pd.DataFrame(move_pairs, columns=['White Move', 'Black Move'])
        df_moves.index += 1  # Adjusting index to start from 1 to represent turns
        df_moves.reset_index(inplace=True)
        df_moves.rename(columns={'index': 'Turn'}, inplace=True)

        # Calculate the appropriate height for the DataFrame display
        num_rows = len(df_moves)
        if num_rows == 1:
            height = 50
        elif num_rows == 2:
            height = 100
        else:
            height = 150  # Set maximum height to 150 for more than 2 rows

        # Display the moves DataFrame
        st.dataframe(df_moves, height=height, hide_index = True)
    except IndexError:
        st.write("No moves data available for the selected opening.")



def get_move_list(op_data, selected_opening):
    try:
        moves_str = op_data.loc[op_data['opening_name'] == selected_opening, 'moves'].iloc[0]
        # Split the string into individual moves
        moves = moves_str.split()
        return moves
    except IndexError:
        # Return an empty list if the moves data is not available
        return []
    
def handle_checkbox(row):
    if row['Select']:
        st.write("Selected:", row['rated'], row['turns'], row['white_rating'], row['black_rating'], row['winner'], row['victory_status'])
        
def plot_opening_vs_game_duration(data, top_most_played):
    """
    Creates a Plotly scatter plot of chess openings against the total game duration for the first ten openings,
    highlighting those that also appear in the top 5 most played openings with the same colors.

    Parameters:
        data (pd.DataFrame): DataFrame containing chess game data with columns
                             'opening_name', 'initial_time', 'increment', and 'turns'.
        top_most_played (pd.DataFrame): DataFrame containing the top 5 most played openings with their assigned colors.

    Returns:
        plotly.graph_objs._figure.Figure: Plotly figure object that can be used in Streamlit.
    """
    # Calculate total game duration
    data['total_duration'] = data['initial_time'] + data['turns'] * data['increment']
    
    # Group by opening name to average the duration
    grouped_data = data.groupby('opening_name').agg(
        average_duration=pd.NamedAgg(column='total_duration', aggfunc='mean'),
        count=pd.NamedAgg(column='total_duration', aggfunc='count')
    ).reset_index()

    # Sort and then take only the top 10 for statistical significance
    top_openings = grouped_data.sort_values(by='count', ascending=False).head(10)

    # Merge to get colors for those in top 5 most played
    top_openings = top_openings.merge(top_most_played[['Opening Name', 'color']], how='left', left_on='opening_name', right_on='Opening Name')

    # Define default color for those not in top 5 most played
    default_color = '#cccccc'

    # Create the Plotly figure
    fig = go.Figure(data=[
        go.Scatter(
            x=top_openings['opening_name'],
            y=top_openings['average_duration'],
            mode='markers',
            marker=dict(size=10, color=top_openings['color'].fillna(default_color), line=dict(width=0.5, color='white'))
        )
    ])

    # Update layout for better readability
    fig.update_layout(
        title='Top 10 Chess Openings in Game Duration',
        xaxis_title='Opening Name',
        yaxis_title='Average Game Duration (Seconds)',
        xaxis_tickangle=-45
    )

    return fig

