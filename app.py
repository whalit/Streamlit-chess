import chess
import chess.svg
import streamlit as st
import streamlit_antd_components as sac

from utils import *


def main():
    
    st.set_page_config(page_title='Interactive Chess Board', layout='wide')
    st.title('Interactive Chess Board Visualisation')
    game_data = load_data()
    category_descriptions = {
        'Rapid': '10-60 minutes per player; balances deep strategic thinking with time pressure.',
        'Blitz': '3-10 minutes per player; emphasizes quick thinking and immediate decision-making.',
        'Bullet': '1-3 minutes per player; focuses on extremely fast moves and instant reactions.'
    }

    st.sidebar.markdown('<h2 style="font-weight: bold; font-size: 25px; color : #9C7A97;">Plot Filters</h3>', unsafe_allow_html=True)
    category = st.sidebar.selectbox('Select Time Control Category', game_data['time_control_category'].unique())
    if category in category_descriptions:
        description_html = f'<p style="font-style: italic; font-size: 10px;">{category_descriptions[category]}</p>'
        st.sidebar.markdown(description_html, unsafe_allow_html=True)
    filter_rated_plot = st.sidebar.selectbox("Filter Games by Rating", ["All", "Rated", "Non-Rated"])
    enable_selectbox = st.sidebar.checkbox("Include Time Increment?")
    description_timeInc = f'<p style="font-style: italic; font-size: 10px;">Time increment adds extra seconds per move </p>'
    st.sidebar.markdown(description_timeInc, unsafe_allow_html=True)
    
    if enable_selectbox:
        # Define the specific increments you want to include
        specific_increments = [1, 2, 5, 10, 15,20, 30]
        # Filter the unique increments to include only the specified values
        increments_filtered = [increment for increment in game_data['increment'].unique() if increment in specific_increments]
        # Sort the filtered increments before displaying them
        sorted_increments = sorted(increments_filtered)

    time_increment = None
    if enable_selectbox:
        specific_increments = [1, 2, 5, 10, 15, 20, 30]
        increments_filtered = [increment for increment in game_data['increment'].unique() if increment in specific_increments]
        time_increment = st.sidebar.selectbox('Select Time Increment', sorted(increments_filtered))
    include_rating = st.sidebar.checkbox("Include rating?")
    rating = st.sidebar.slider('Select The Rating Range', min_value=0, max_value=game_data['white_rating'].max(), step=100, value=(0, game_data['white_rating'].max()), disabled=not include_rating)
    st.sidebar.markdown('<h2 style="font-weight: bold; font-size: 20px; color: #7EA2AA;">Additional Filters</h3>', unsafe_allow_html=True)
    st.sidebar.markdown('<h2 style="font-style: italic; font-size: 10px;">These additinal filters control the list of games in the chess board tab</h3>', unsafe_allow_html=True)
    filter_winner = st.sidebar.selectbox("Filter Games by Winner", ["All", "White", "Black"], key="winner_filter")




    # Apply filters to the data
    filtered_data = game_data[game_data['time_control_category'] == category]
    if filter_rated_plot != "All":
        is_rated = filter_rated_plot == "Rated"
        filtered_data = filtered_data[filtered_data['rated'] == is_rated]

    if enable_selectbox and time_increment:
        filtered_data = filtered_data[filtered_data['increment'] == time_increment]

    if include_rating:
        lower, upper = rating
        filtered_data = filtered_data[(filtered_data['white_rating'].between(lower, upper)) |
                                    (filtered_data['black_rating'].between(lower, upper))]
        
    tab1, tab2 = st.tabs(["Statistical Plots", "Opening Details & Chess Board Display"])
    
    with tab1:
        st.session_state.active_tab = "tab1"
        col1, col2 = st.columns(2)
        with col1:
            # Check if there is data to plot
            if not filtered_data.empty:
                fig3, most_played = plot_most_played_openings(filtered_data)
                if fig3:
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.write("No plot available with these filters.")

                fig2 = plot_top_openings(filtered_data)
                if fig2:
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.write("No plot available with these filters.")
            else:
                st.write("No plot available with these filters.")
        
        with col2:
            # Check if there is data to plot
            if not filtered_data.empty:
                fig4 = plot_opening_vs_game_duration(filtered_data, most_played)
                if fig4:
                    st.plotly_chart(fig4, use_container_width=True)
                else:
                    st.write("No plot available with these filters.")

                fig1 = plot_winning_rates(filtered_data)
                if fig1:
                    st.plotly_chart(fig1, use_container_width=True)
                else:
                    st.write("No plot available with these filters.")
            else:
                st.write("No plot available with these filters.")


            
    with tab2:
        col3, col4 = st.columns(2)

            
        with col4:
            selected_opening = st.selectbox('Select an Opening to view details:', sorted(game_data['opening_name'].unique()))
            opening_games = game_data[game_data['opening_name'] == selected_opening]
            # Display the filtered games
            display_data = opening_games[['id','rated', 'turns', 'white_rating', 'black_rating', 'winner', 'victory_status','time_control_category']].reset_index(drop=True)
            moves = get_move_list(game_data, selected_opening)
            if 'selected_opening' not in st.session_state or st.session_state.selected_opening != selected_opening:
                st.session_state['moves'] = moves
                st.session_state['current_move_index'] = 0
                st.session_state['selected_opening'] = selected_opening
                
            if 'current_move_index' not in st.session_state or st.session_state.selected_opening != selected_opening:
                st.session_state.current_move_index = 0
                st.session_state.selected_opening = selected_opening
            display_opening_details(game_data, selected_opening)
            sac.tabs([
                sac.TabsItem(label='Opening move'),
                sac.TabsItem(label='Winners Percentage'),
                sac.TabsItem(label='Time control'),
                sac.TabsItem(label='List Of Games')], align='center', color='teal', key='tabs')
    
            if st.session_state['tabs'] is not None:
                    if st.session_state['tabs'] == 'Opening move':
                        display_moves_list(game_data, selected_opening,game_data)
                    if st.session_state['tabs'] == 'Time control':
                        plot_time_control_cat(game_data, selected_opening)
                    if st.session_state.get('tabs') == 'Winners Percentage':
                        include_draws = st.checkbox('Include draws in the win rates', value=True)
                        plot_winners_cat(include_draws, game_data, selected_opening)
                    if st.session_state.get('tabs') == 'List Of Games':
                        if not opening_games.empty:

                            # Apply the rated filter
                            if filter_rated_plot == "Rated":
                                filtered_games = display_data[display_data['rated'] == True]
                            elif filter_rated_plot == "Non-Rated":
                                filtered_games = display_data[display_data['rated'] == False]
                            else:
                                filtered_games = display_data  # Show all games if 'All' is selected

                            # Apply the winner filter
                            if filter_winner == "White":
                                filtered_games = filtered_games[filtered_games['winner'] == 'white']
                            elif filter_winner == "Black":
                                filtered_games = filtered_games[filtered_games['winner'] == 'black']
                                
                            # Rating range filter: Check if the rating slider is active and apply filter
                            if include_rating:
                                # Get the selected rating range
                                # Extract lower and upper bounds of the selected range
                                rating_lower_bound, rating_upper_bound = rating
                                # Adjust the bounds with +-50
                                rating_lower_bound -= 50
                                rating_upper_bound += 50
                                filtered_games = filtered_games[
                                    (filtered_games['white_rating'].between(rating_lower_bound, rating_upper_bound)) |
                                    (filtered_games['black_rating'].between(rating_lower_bound, rating_upper_bound))
                                ]
                            else:
                                rating_lower_bound = 0
                                rating_upper_bound = game_data['white_rating'].max()
                                
                            if filtered_games.empty:
                                st.write("No existing games match the selected filters.")
                            else:
                                # Rename columns before displaying
                                filtered_games = filtered_games.rename(columns={
                                    'id': 'ID',
                                    'rated': 'Rated',
                                    'turns': 'Turns',
                                    'white_rating': 'White Rating',
                                    'black_rating': 'Black Rating',
                                    'winner': 'Winner',
                                    'victory_status': 'Victory Status',
                                    'time_control_category': 'Category'
                                })

                                # Determine the number of rows for setting the dataframe height
                                num_rows = len(filtered_games)
                                if num_rows == 1:
                                    height = 50
                                elif num_rows == 2:
                                    height = 100
                                else:
                                    height = 200  # Set maximum height to 200 for more than 2 rows

                                # Display the dataframe with the filtered data
                                st.dataframe(filtered_games, height=height, hide_index=True)

                                
            game_ID = st.selectbox('Select the Game By ID', display_data['id'].unique())
            game_moves = game_data[game_data['id'] == game_ID]['moves']
            st.dataframe(game_moves, hide_index=True, width = 550)
        with col3:
            coltemp1, col5, col6, col7, coltemp2 = st.columns([3, 5, 4, 5, 4]) #coltemp1 and coltemp2 are only for esthetic purpose
            current_move = st.session_state['moves'][st.session_state['current_move_index']]
            
            with col5:
                if st.button("⬅️") and st.session_state.get('current_move_index', 0) > 0:
                    st.session_state['current_move_index'] -= 1
                    # Fetch the move right after updating the index
                    current_move = st.session_state['moves'][st.session_state['current_move_index']]
                    
            with col7:
                if st.button("➡️") and st.session_state.get('current_move_index', 0) < len(st.session_state.get('moves', [])) - 1:
                    st.session_state['current_move_index'] += 1
                    # Fetch the move right after updating the index
                    current_move = st.session_state['moves'][st.session_state['current_move_index']]

            with col6:
                    st.write(current_move)
                    
            if 'moves' in st.session_state:
                    board, last_move = update_chess_board(st.session_state['moves'], st.session_state['current_move_index'])
                    if last_move is not None:
                            move_arrow = [chess.svg.Arrow(last_move.from_square, last_move.to_square, color="#D00000")]
            else:
                move_arrow = None

            chess_svg = display_chess_board(board, arrows=move_arrow)
            st.image(chess_svg, caption='Current Board', output_format='SVG', width=450)
            


if __name__ == "__main__":
    main()