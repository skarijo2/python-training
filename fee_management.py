from json import load

with open('program_1/fees.json') as f:
    FEES = load(f)

def calculate_fee(amount, currency):
    fee = FEES.get(currency, {})
    if 'flat' in fee:
        return fee['flat'], fee['who']
    elif 'pct' in fee:
        return (amount * fee['pct']), fee['who']
    return (None, None)