from datetime import datetime
from account import Account
from fee_management import calculate_fee
from master import master

class Transaction:

    def __init__(self, id, transaction_type, transaction_datetime):
        self.id = id
        self.transaction_type = transaction_type
        self.transaction_datetime = datetime.strptime(transaction_datetime, '%Y-%m-%d %H:%M:%S')
        self.status = 'PENDING'

    @staticmethod
    def from_json(**kwargs):
        if kwargs['transaction_type'] == 'payment':
            return Payment(**kwargs)
        elif kwargs['transaction_type'] == 'cancellation':
            return Cancellation(**kwargs)


class Cancellation(Transaction):

    def __init__(self, id, transaction_type, transaction_datetime=None, transaction=None):
        super().__init__(id, transaction_type, transaction_datetime)
        self.transaction = transaction

    def process(self, accounts, original_transaction):
        original_sender = accounts.get(original_transaction.sender_id)
        original_recipient = accounts.get(original_transaction.recipient_id)
        fee = calculate_fee(original_transaction.amount, original_transaction.currency)
        original_recipient.pay(original_sender, original_transaction.amount, original_transaction.currency, master, fees_apply=False)

        if fee[1] == 'sender':
            fee_charged_to = original_sender
        elif fee[1] == 'recipient':
            fee_charged_to = original_recipient

        master.pay(fee_charged_to, fee[0], original_transaction.currency, master, fees_apply=False)

        self.status = 'COMPLETE'
        original_transaction.status = 'CANCELLED'


class Payment(Transaction):

    def __init__(self, id, transaction_type, transaction_datetime=None, sender_id=None, recipient_id=None, amount=0, currency='USD'):
        super().__init__(id, transaction_type, transaction_datetime)
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.amount = amount
        self.currency = currency

    def process(self, accounts):
        sender_id = self.sender_id
        recipient_id = self.recipient_id

        sender = accounts.get(sender_id)
        if not recipient_id in accounts:
            accounts[recipient_id] = Account(recipient_id)
        recipient = accounts.get(recipient_id)
        if sender.pay(recipient, self.amount, self.currency, master):
            self.status = 'COMPLETE'
        else:
            self.status = 'FAILED'