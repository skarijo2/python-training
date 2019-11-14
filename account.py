from fee_management import calculate_fee

class Account:

    def __init__(self, id, name='<Unknown>', country=None, balances={}):
        self.id = id
        self.name = name
        self.country = country
        self.balances = balances
        self.status = 'IN_GOOD_STANDING'
    
    def update_balance(self, amount, currency):
        if currency not in self.balances:
            self.balances[currency] = 0
    
        self.balances[currency] += amount

    def has_sufficient_funds(self, amount, currency):
        current_balance = self.balances.get(currency, 0)
        return current_balance >= amount

    def pay(self, recipient, amount, currency, master, fees_apply=True):

        fee = calculate_fee(amount, currency)
        sender_fee = fee[0] if fee[1] == 'sender' and fees_apply else 0
        recipient_fee = fee[0] if fee[1] == 'recipient' and fees_apply else 0

        if self.has_sufficient_funds(amount + sender_fee, currency):
            self.update_balance(-(amount + sender_fee), currency)
            recipient.update_balance(amount - recipient_fee, currency)
            master.update_balance(sender_fee + recipient_fee, currency)
            return True
        else:
            print(f'{self.name} has insufficient funds for transaction.')
            return False