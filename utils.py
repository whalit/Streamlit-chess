import chess
import chess.svg
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def load_data():
    """
    Load and return the chess game data from a CSV file.
    Returns:
        pd.DataFrame: Dataframe containing the game data.
    """
    return pd.read_csv('games_revisited.csv')


######################################################################################################
##################################         PLOTS              ########################################

def plot_ranking(data):
    """
    Creates a frequency plot data for player ratings from a dataset.
    
    Parameters:
        data (pd.DataFrame): Dataset containing 'white_rating' and 'black_rating' columns.

    Returns:
        pd.DataFrame: Dataframe prepared for plotting, containing 'Rating' and 'Frequency'.
    """
    combined_ratings = pd.concat([data['white_rating'], data['black_rating']])
    rating_count = combined_ratings.value_counts().reset_index()
    rating_count.columns = ['Rating', 'Frequency']
    sorted_ratings = rating_count.sort_values(by='Rating').reset_index(drop=True)
    return pd.DataFrame({"Rating": sorted_ratings['Rating'], "Frequency": sorted_ratings['Frequency']})

def plot_winning_rates(data):
    """
    Generates a pie chart of winning rates for different players in a given dataset.

    Parameters:
        data (pd.DataFrame): Dataset containing 'winner' and 'time_control_category'.

    Returns:
        plotly.graph_objs._figure.Figure: Pie chart of winning rates or None if data is empty.
    """
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
    """
    Plots the top chess openings based on a specified sorting criteria.

    Parameters:
        data (pd.DataFrame): Dataset containing 'opening_name' and 'winner'.
        sort_by (str): Sorting criterion, either 'winning_rate' or other valid DataFrame sorting keys.

    Returns:
        plotly.graph_objs._figure.Figure: Bar chart of the top 5 openings by winning rate.
    """
    openings_count = data.groupby(['opening_name', 'winner']).size().unstack(fill_value=0).reset_index()
    title = 'Top 5 Openings by Winning Rate'
    if sort_by == 'winning_rate':
        openings_count = openings_count.nlargest(5, ['white', 'black'])
    fig = px.bar(openings_count, y='opening_name', x=['white', 'black'], title=title, labels={'value': 'Number of Wins', 'variable': 'Winner'}, color_discrete_sequence=['#E2E2E2', '#22223B'], barmode='group', height=400, orientation='h')
    fig.update_traces(marker_line_width=0.5)
    return fig

def plot_most_played_openings(data):
    """
    Identifies and visualizes the top 5 most played chess openings.

    Parameters:
        data (pd.DataFrame): Dataset containing 'opening_name'.

    Returns:
        tuple: Contains a Plotly figure of the bar chart and the dataframe of the top openings.
    """
    openings_count = data['opening_name'].value_counts().reset_index()
    openings_count.columns = ['Opening Name', 'Number of Games Played']
    openings_count = openings_count.nlargest(5, 'Number of Games Played')
    custom_colors = ['#FFBE0B', '#FB5607', '#FF006E', '#8338EC', '#3A86FF']
    openings_count['color'] = custom_colors[:len(openings_count)]
    fig = px.bar(openings_count, x='Opening Name', y='Number of Games Played', title='Top 5 Most Played Openings', height=550, orientation='v', color='color', color_discrete_map={color: color for color in custom_colors})
    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Number of Games Played")
    return fig, openings_count


def plot_time_control_cat(game_data, selected_opening):
    """
    Plots the distribution of time control categories for a selected opening as a pie chart.

    Parameters:
        game_data (pd.DataFrame): DataFrame containing all game data.
        selected_opening (str): The chess opening to analyze.

    Effects:
        Renders a pie chart in Streamlit or displays a message if no data is available.
    """
    opening_data = game_data[game_data['opening_name'] == selected_opening]
    if not opening_data.empty:
        category_percentage = opening_data['time_control_category'].value_counts(normalize=True) * 100
        df_category_percentage = pd.DataFrame({'Time Control Category': category_percentage.index, 'Percentage': category_percentage.values})
        custom_colors = ['#FFAFCC', '#BDE0FE', '#84A98C', '#FDFCDC']
        fig = px.pie(df_category_percentage, names='Time Control Category', values='Percentage', color='Time Control Category', color_discrete_sequence=custom_colors, labels={'Time Control Category': 'Category', 'Percentage': 'Percentage'})
        fig.update_layout(width=700, height=400, legend=dict(title="Categories", x=0.1, xanchor="center", yanchor="top", orientation="v"))
        st.plotly_chart(fig)
    else:
        st.write(f"No data available for the opening: {selected_opening}")

def plot_winners_cat(include_draws, game_data, selected_opening):
    """
    Plots a pie chart of the winners distribution for a selected opening, optionally excluding draws.

    Parameters:
        include_draws (bool): Whether to include draws in the plot.
        game_data (pd.DataFrame): DataFrame containing all game data.
        selected_opening (str): The chess opening to analyze.

    Effects:
        Renders a pie chart in Streamlit or displays a message if no relevant data is available.
    """
    opening_data = game_data[game_data['opening_name'] == selected_opening]
    if not opening_data.empty:
        if not include_draws:
            opening_data = opening_data[opening_data['winner'] != 'draw']
        if not opening_data.empty:
            winner_percentage = opening_data['winner'].value_counts(normalize=True) * 100
            df_winner_percentage = pd.DataFrame({'Winner': winner_percentage.index, 'Percentage': winner_percentage.values})
            color_map = {'white': '#E2E2E2', 'black': '#22223B', 'draw': '#2A9D8F'}
            if not include_draws:
                color_map.pop('draw', None)
            fig = px.pie(df_winner_percentage, names='Winner', values='Percentage', color='Winner', color_discrete_map=color_map)
            fig.update_layout(width=700, height=400, legend=dict(title="Categories", x=0.1, xanchor="center", yanchor="top", orientation="v"))
            st.plotly_chart(fig)
        else:
            st.write(f"No relevant data available for the opening: {selected_opening}")
    else:
        st.write(f"No data available for the opening: {selected_opening}")
        
        
######################################################################################################
##################################         OTHERS              ########################################

def display_opening_details(data, opening_name):
    """
    Displays detailed information about a specific chess opening in a Streamlit dataframe.

    Parameters:
        data (pd.DataFrame): The dataset containing 'opening_name' and other related columns.
        opening_name (str): The specific opening to detail.
    """
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
    st.dataframe(pd.DataFrame(details), hide_index=True)

def display_chess_board(board, arrows=None):
    """
    Generates and returns an SVG string representing a chess board with optional arrows.

    Parameters:
        board (chess.Board): The chess board object.
        arrows (list of chess.svg.Arrow, optional): Arrows indicating moves or other highlights.

    Returns:
        str: An SVG string of the chess board.
    """
    return chess.svg.board(board=board, size=350, arrows=arrows)

def update_chess_board(moves, current_move_index):
    """
    Updates the chess board to a specified move index.

    Parameters:
        moves (list of str): List of moves in standard algebraic notation.
        current_move_index (int): Index of the last move to execute on the board.

    Returns:
        tuple: Returns a tuple containing the updated board and the last move executed.
    """
    board = chess.Board()
    last_move = None
    for move in moves[:current_move_index + 1]:
        last_move = board.push_san(move)
    return board, last_move


def display_moves_list(op_data, selected_opening, game_data):
    """
    Displays a list of chess moves for a selected opening in a DataFrame format.

    Parameters:
        op_data (pd.DataFrame): DataFrame containing opening moves data.
        selected_opening (str): The chess opening whose moves to display.
        game_data (pd.DataFrame): DataFrame containing detailed game data.
    """
    try:
        moves_str = op_data.loc[op_data['opening_name'] == selected_opening, 'moves'].iloc[0]
        opening_ply = game_data.loc[game_data['opening_name'] == selected_opening, 'opening_ply'].iloc[0]
        moves = moves_str.split()
        moves_limited = moves[:opening_ply]
        move_pairs = [(moves_limited[i], moves_limited[i+1] if i+1 < len(moves_limited) else '') for i in range(0, len(moves_limited), 2)]
        df_moves = pd.DataFrame(move_pairs, columns=['White Move', 'Black Move'])
        df_moves.index += 1
        df_moves.reset_index(inplace=True)
        df_moves.rename(columns={'index': 'Turn'}, inplace=True)
        num_rows = len(df_moves)
        height = 150 if num_rows > 2 else num_rows * 50
        st.dataframe(df_moves, height=height, hide_index=True)
    except IndexError:
        st.write("No moves data available for the selected opening.")

def get_move_list(op_data, selected_opening):
    """
    Retrieves a list of moves for a selected opening.

    Parameters:
        op_data (pd.DataFrame): DataFrame containing opening moves data.
        selected_opening (str): The chess opening whose moves to retrieve.

    Returns:
        list of str: A list of moves, or an empty list if no data is available.
    """
    try:
        moves_str = op_data.loc[op_data['opening_name'] == selected_opening, 'moves'].iloc[0]
        moves = moves_str.split()
        return moves
    except IndexError:
        return []

def handle_checkbox(row):
    """
    Handles the logic for a checkbox interaction in a Streamlit app.

    Parameters:
        row (pd.Series): A data row from a DataFrame which includes a 'Select' column.
    """
    if row['Select']:
        st.write("Selected:", row['rated'], row['turns'], row['white_rating'], row['black_rating'], row['winner'], row['victory_status'])
        
def plot_opening_vs_game_duration(data, top_most_played):
    """
    Plots a scatter plot comparing the average game duration of the top 10 chess openings against their name.

    Parameters:
        data (pd.DataFrame): DataFrame containing chess game data.
        top_most_played (pd.DataFrame): DataFrame containing the top 5 most played openings.

    Returns:
        plotly.graph_objs._figure.Figure: A Plotly figure object that can be used in Streamlit.
    """
    
    data['total_duration'] = data['initial_time'] + data['turns'] * data['increment']
    grouped_data = data.groupby('opening_name').agg(average_duration=pd.NamedAgg(column='total_duration', aggfunc='mean'), count=pd.NamedAgg(column='total_duration', aggfunc='count')).reset_index()
    top_openings = grouped_data.sort_values(by='count', ascending=False).head(10)
    top_openings = top_openings.merge(top_most_played[['Opening Name', 'color']], how='left', left_on='opening_name', right_on='Opening Name')
    default_color = '#cccccc'
    fig = go.Figure(data=[go.Scatter(x=top_openings['opening_name'], y=top_openings['average_duration'], mode='markers', marker=dict(size=10, color=top_openings['color'].fillna(default_color), line=dict(width=0.5, color='white')))])
    fig.update_layout(title='Top 10 Chess Openings in Game Duration', xaxis_title='Opening Name', yaxis_title='Average Game Duration (Seconds)', xaxis_tickangle=-45)
    return fig
