from flask import Flask, request, jsonify
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

# List all past transactions
transactions = []

# Maps a payer to their amount of points
balances = defaultdict(int)

@app.route('/add', methods=['POST'])
def add_points():
    """
    Endpoint to add points for a user through a payer.
    Example request body:
    {
        "payer" : "DANNON",
        "points" : 5000,
        "timestamp" : "2020-11-02T14:00:00Z"
    }
    """
    data = request.get_json()
    payer = data['payer']
    points = int(data['points'])
    timestamp = data['timestamp']
    
    # Parse the timestamp to ensure correct format
    # Removes the last character 'Z' before parsing it
    timestamp = datetime.fromisoformat(timestamp[:-1])
    
    # Store the transaction
    transactions.append({
        'payer': payer,
        'points': points,
        'timestamp': timestamp
    })
    
    # Update the payer's balance
    balances[payer] += points
    
    return '', 200

@app.route('/spend', methods=['POST'])
def spend_points():
    """
    Endpoint to spend points based on the rules:
    1. Spend the oldest points first.
    2. No payer's points can go negative.
    
    Example request body:
    {
        "points": 5000
    }
    """
    data = request.get_json()
    points_to_spend = int(data['points'])
    
    if points_to_spend > sum(balances.values()):
        return 'User does not have enough points.', 400

    # Sort transactions by timestamp (oldest first)
    sorted_transactions = sorted(transactions, key=lambda x: x['timestamp'])
    spent_points = defaultdict(int)
    
    for transaction in sorted_transactions:
        if points_to_spend <= 0:
            break
        
        payer = transaction['payer']
        available_points = balances[payer]
        
        if available_points <= 0:
            continue
        
        spend_amount = min(transaction['points'], points_to_spend)
        
        # Ensure we don't spend more than the available points from a payer
        if spend_amount > balances[payer]:
            spend_amount = balances[payer]

        # Update the balances and transaction points
        balances[payer] -= spend_amount
        points_to_spend -= spend_amount
        spent_points[payer] += -spend_amount
    
    res = []

    for key in spent_points:
        res.append({"payer": key, "points": spent_points[key]})
    
    return jsonify(res), 200

@app.route('/balance', methods=['GET'])
def get_balance():
    """
    Endpoint to get the current points balance for each payer.
    Example response:
    {
        "DANNON": 1000,
        "UNILEVER": 0,
        "MILLER COORS": 5300
    }
    """
    return jsonify(balances), 200

if __name__ == '__main__':
    app.run(port=8000)
