
import os
from flask import Flask, render_template, request, jsonify
import pandas as pd
from collections import defaultdict
from flask import Flask, render_template, request, jsonify, redirect, url_for
import random
app = Flask(__name__)
credentials = {
    "admin": "Admin_qwerty",
    "user1": "user_login@123"
}



def load_players():
    try:
        df = pd.read_excel('players.xlsx')
        players = df.to_dict('records')
        random.shuffle(players)
        for player in players:
            if player['grade'] == 'Diamond':
                player['base_price'] = 300000
                player['bid_increment'] = 50000
            elif player['grade'] == 'Platinum':
                player['base_price'] = 200000
                player['bid_increment'] = 50000
            elif player['grade'] == 'Gold':
                player['base_price'] = 100000
                player['bid_increment'] = 50000
            player['final_bid'] = 0
            player['winning_team'] = None
            player['unsold'] = False
            player['bid_history'] = []  # Initialize bid history for each player
        return players
    except Exception as e:
        print(f"Error loading players: {e}")
        return []

players = load_players()
unsold_players = []

teams = {
    "PM Capitals": {"budget": 10000000, "players": [], "grade_count": defaultdict(int)},
    "PM Knight Riders": {"budget": 10000000, "players": [], "grade_count": defaultdict(int)},
    "PM Royals": {"budget": 10000000, "players": [], "grade_count": defaultdict(int)},
    "PM Super Giants": {"budget": 10000000, "players": [], "grade_count": defaultdict(int)},
    "PM Super Kings": {"budget": 10000000, "players": [], "grade_count": defaultdict(int)},
    "PM Titans": {"budget": 10000000, "players": [], "grade_count": defaultdict(int)}
}

current_player_index = 0

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in credentials and credentials[username] == password:
            if username == 'admin':
                return redirect(url_for('auction'))
            else:
                return redirect(url_for('view_info'))
        else:
            return "Invalid credentials. Please try again."
    return render_template('login.html')

# @app.route('/auction')
# def auction():
#     global current_player_index, players, unsold_players  # Declare global variables

#     # If all players have been processed, check if there are any unsold players left
#     if current_player_index >= len(players):
#         if unsold_players:
#             # Re-add only unsold players back into the auction
#             players = unsold_players.copy()  # Reset 'players' to only contain unsold ones
#             unsold_players.clear()  # Clear the 'unsold_players' list since they are now in 'players'
#             current_player_index = 0  # Reset index to start from first unsold player
#             return render_template('auction.html', player=players[current_player_index], teams=teams)
#         return "No more players left"  # No more players (including unsold ones) left to auction

#     # Continue with normal auction if there are still unprocessed players
#     return render_template('auction.html', player=players[current_player_index], teams=teams)

@app.route('/auction')
def auction():
    global current_player_index, players, unsold_players

    if current_player_index >= len(players):
        if unsold_players:
            players = unsold_players.copy()
            unsold_players.clear()
            current_player_index = 0
            return render_template('auction.html', player=players[current_player_index], teams=teams)
        
        # Redirect to final teams page when no players are left
        return redirect(url_for('final_teams'))

    return render_template('auction.html', player=players[current_player_index], teams=teams)

# @app.route('/auction')
# def auction():
#     global current_player_index, players
#     if current_player_index >= len(players):
#         if unsold_players:
#             players.extend(unsold_players)
#             unsold_players.clear()
#             current_player_index = len(players) - len(unsold_players)
#             return render_template('auction.html', player=players[current_player_index], teams=teams)
#         return "No more players left"
#     else:
#         return render_template('auction.html', player=players[current_player_index], teams=teams)

# @app.route('/bid', methods=['POST'])
# def bid():
#     global current_player_index
#     data = request.json
#     team_name = data['team_name']
#     player = players[current_player_index]
    
#     # Initialize bid_history if it doesn't exist
#     if 'bid_history' not in player:
#         player['bid_history'] = []
    
#     # Check if team has already bought 2 players of this grade
#     if teams[team_name]["grade_count"][player['grade']] >= 2:
#         return jsonify(success=False, message=f"Team already has 2 players of grade {player['grade']}!")

#     if player['final_bid'] == 0:
#         bid_amount = player['base_price']
#     else:
#         bid_amount = player['final_bid'] + player['bid_increment']

#     if bid_amount <= teams[team_name]["budget"]:
#         # Store current bid in history before updating
#         if player['winning_team']:
#             player['bid_history'].append({
#                 'team': player['winning_team'],
#                 'amount': player['final_bid']
#             })
        
#         player['final_bid'] = bid_amount
#         player['winning_team'] = team_name
#         return jsonify(success=True, player=player)
    
#     return jsonify(success=False, message="Bid exceeds budget!")



@app.route('/bid', methods=['POST'])
def bid():
    global current_player_index
    data = request.json
    team_name = data['team_name']
    player = players[current_player_index]
    
    # Initialize bid_history if it doesn't exist
    if 'bid_history' not in player:
        player['bid_history'] = []
    
    # Get current team's players
    team_players = [p for p in players if p.get('winning_team') == team_name]
    
    # Check grade and gender restrictions
    grade = player['grade']
    gender = player['gender']
    
    # Count current players by grade and gender
    diamond_males = sum(1 for p in team_players if p['grade'] == 'Diamond' and p['gender'] == 'Male')
    diamond_females = sum(1 for p in team_players if p['grade'] == 'Diamond' and p['gender'] == 'Female')
    gold_males = sum(1 for p in team_players if p['grade'] == 'Gold' and p['gender'] == 'Male')
    platinum_males = sum(1 for p in team_players if p['grade'] == 'Platinum' and p['gender'] == 'Male')
    platinum_females = sum(1 for p in team_players if p['grade'] == 'Platinum' and p['gender'] == 'Female')
    
    # Check restrictions
    if (grade == 'Diamond' and gender == 'Male' and diamond_males >= 1) or \
       (grade == 'Diamond' and gender == 'Female' and diamond_females >= 1) or \
       (grade == 'Gold' and gender == 'Male' and gold_males >= 1) or \
       (grade == 'Platinum' and gender == 'Male' and platinum_males >= 1) or \
       (grade == 'Platinum' and gender == 'Female' and platinum_females >= 3):
        return jsonify(success=False, message=f"Team has reached maximum limit for {grade} {gender} players!")

    if player['final_bid'] == 0:
        bid_amount = player['base_price']
    else:
        bid_amount = player['final_bid'] + player['bid_increment']

    if bid_amount <= teams[team_name]["budget"]:
        # Store current bid in history before updating
        if player['winning_team']:
            player['bid_history'].append({
                'team': player['winning_team'],
                'amount': player['final_bid']
            })
        
        player['final_bid'] = bid_amount
        player['winning_team'] = team_name
        return jsonify(success=True, player=player)
    
    return jsonify(success=False, message="Bid exceeds budget!")


# @app.route('/sell_player', methods=['POST'])
# def sell_player():
#     global current_player_index
#     data = request.json
#     team_name = data['team_name']
#     player = players[current_player_index]

#     if player['final_bid'] > 0:
#         # Check again if team has already bought 2 players of this grade
#         if teams[team_name]["grade_count"][player['grade']] >= 2:
#             return jsonify(success=False, message=f"Team already has 2 players of grade {player['grade']}!")
        
#         teams[team_name]["players"].append({
#             "name": player['name'],
#             "price": player['final_bid'],
#             "grade": player['grade']
#         })
#         teams[team_name]["budget"] -= player['final_bid']
#         teams[team_name]["grade_count"][player['grade']] += 1
#         current_player_index += 1

#         if current_player_index < len(players):
#             return jsonify(success=True, player=players[current_player_index], team_data=teams[team_name])
#         elif unsold_players:
#             players.extend(unsold_players)
#             unsold_players.clear()
#             current_player_index = len(players) - len(unsold_players)
#             return jsonify(success=True, player=players[current_player_index], team_data=teams[team_name])
#         else:
#             if unsold_players:
#                 players.extend(unsold_players)
#                 unsold_players.clear()
#                 current_player_index = len(players) - len(unsold_players)
#                 return jsonify(success=True, player=players[current_player_index], team_data=teams[team_name])
#             return jsonify(success=False, message="No more players to auction!")
#     return jsonify(success=False)


# 



@app.route('/sell_player', methods=['POST'])
def sell_player():
    global current_player_index, players, unsold_players

    data = request.json
    team_name = data['team_name']
    
    if current_player_index >= len(players):
        return jsonify(success=False, message="No more players available for auction!")

    player = players[current_player_index]

    if player['final_bid'] > 0:
        # Get current team's players
        team_players = teams[team_name]["players"]
        
        # Count current players by grade and gender
        diamond_males = sum(1 for p in team_players if p['grade'] == 'Diamond' and p['gender'] == 'Male')
        diamond_females = sum(1 for p in team_players if p['grade'] == 'Diamond' and p['gender'] == 'Female')
        gold_males = sum(1 for p in team_players if p['grade'] == 'Gold' and p['gender'] == 'Male')
        platinum_males = sum(1 for p in team_players if p['grade'] == 'Platinum' and p['gender'] == 'Male')
        platinum_females = sum(1 for p in team_players if p['grade'] == 'Platinum' and p['gender'] == 'Female')
        
        # Check restrictions
        if ((player['grade'] == 'Diamond' and player['gender'] == 'Male' and diamond_males >= 1) or
            (player['grade'] == 'Diamond' and player['gender'] == 'Female' and diamond_females >= 1) or
            (player['grade'] == 'Gold' and player['gender'] == 'Male' and gold_males >= 1) or
            (player['grade'] == 'Platinum' and player['gender'] == 'Male' and platinum_males >= 1) or
            (player['grade'] == 'Platinum' and player['gender'] == 'Female' and platinum_females >= 3)):
            return jsonify(success=False, message=f"Team has reached maximum limit for {player['grade']} {player['gender']} players!")
        
        # Add sold player's details to the team
        teams[team_name]["players"].append({
            "name": player['name'],
            "price": player['final_bid'],
            "grade": player['grade'],
            "gender": player['gender']
        })
        
        teams[team_name]["budget"] -= player['final_bid']

        # Move on to next player after selling
        current_player_index += 1

        if current_player_index < len(players):
            return jsonify(success=True, player=players[current_player_index], team_data=teams[team_name])

        elif len(unsold_players) > 0:
            players = unsold_players.copy()
            unsold_players.clear()
            current_player_index = 0
            return jsonify(success=True, player=players[current_player_index], team_data=teams[team_name])

        else:
            return redirect(url_for('final_teams'))
    
    return jsonify(success=False)


# @app.route('/mark_unsold', methods=['POST'])
# def mark_unsold():
#     global current_player_index

#     player = players[current_player_index]
#     player['unsold'] = True
#     unsold_players.append(players.pop(current_player_index))

#     if current_player_index >= len(players):
#         if unsold_players:
#             players.extend(unsold_players)
#             unsold_players.clear()
#             current_player_index = len(players) - len(unsold_players)
#         return jsonify(success=True, player=players[current_player_index])

#     return jsonify(success=True, player=players[current_player_index])

@app.route('/mark_unsold', methods=['POST'])
def mark_unsold():
    global current_player_index, players, unsold_players  # Declare global variables

    # Mark the current player as unsold and move them to 'unsold_players'
    if current_player_index < len(players):
        player = players[current_player_index]
        player['unsold'] = True
        unsold_players.append(player)  # Add to 'unsold_players' list

        # Remove the player from 'players' but don't increment index (since we removed one)
        del players[current_player_index]

    # If there are still remaining players in 'players', continue with next one.
    if current_player_index < len(players):
        return jsonify(success=True, player=players[current_player_index])

    # If no more regular players left, check if we need to re-add unsold ones.
    if len(players) == 0 and len(unsold_players) > 0:
        return jsonify(success=True, message="All regular players processed; unsold will be re-auctioned.")

    return jsonify(success=False, message="No more players left")

@app.route('/cancel_bid', methods=['POST'])
def cancel_bid():
    global current_player_index
    player = players[current_player_index]
    
    # Initialize bid_history if it doesn't exist
    if 'bid_history' not in player:
        player['bid_history'] = []
    
    # If there's no bid yet, return error
    if player['final_bid'] == 0:
        return jsonify(success=False, message="No bid to cancel")
    
    # If only base price bid exists
    if player['final_bid'] == player['base_price']:
        player['final_bid'] = 0
        player['winning_team'] = None
        return jsonify(success=True, player=player)
    
    # Get previous bid from history
    if player['bid_history']:
        previous_bid = player['bid_history'].pop()
        player['final_bid'] = previous_bid['amount']
        player['winning_team'] = previous_bid['team']
    else:
        # If no bid history, reduce by increment
        player['final_bid'] -= player['bid_increment']
        if player['final_bid'] < player['base_price']:
            player['final_bid'] = player['base_price']
        player['winning_team'] = None
    
    return jsonify(
        success=True, 
        player=player, 
        message=f"Bid cancelled. Current bid: {player['final_bid']} by {player['winning_team'] or 'None'}"
    )


@app.route('/final_teams')
def final_teams():
    return render_template('final_teams.html', teams=teams)

@app.route('/view_info')
def view_info():
    current_player = None
    if current_player_index < len(players):
        current_player = players[current_player_index]
    return render_template('view_info.html', 
                         player=current_player, 
                         teams=teams)


@app.route('/manual_bid', methods=['POST'])
def manual_bid():
    global current_player_index
    data = request.json
    team_name = data['team_name']
    bid_amount = data['bid_amount']
    player = players[current_player_index]

    if teams[team_name]["grade_count"][player['grade']] >= 2:
        return jsonify(success=False, message=f"Team already has 2 players of grade {player['grade']}!")

    if bid_amount < player['base_price']:
        return jsonify(success=False, message=f"Bid must be at least {player['base_price']}!")
        
    if player['final_bid'] > 0 and bid_amount <= player['final_bid']:
        return jsonify(success=False, message="Bid must be higher than current bid!")
        
    if bid_amount > teams[team_name]["budget"]:
        return jsonify(success=False, message="Insufficient team budget!")

    if player['winning_team']:
        player['bid_history'].append({
            'team': player['winning_team'],
            'amount': player['final_bid']
        })

    player['final_bid'] = bid_amount
    player['winning_team'] = team_name
    
    return jsonify(success=True, player=player)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
