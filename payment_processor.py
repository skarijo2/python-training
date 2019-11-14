from json import load
from account import Account
from transaction import Transaction
from datetime import datetime, timedelta

balances_filepath = 'program_1/balances.json'
payments_filepath = 'program_1/payments.json'


def process(accounts, transactions):
    for transaction in transactions.values():
        
        if transaction.transaction_type == 'payment':
           transaction.process(accounts)

        elif transaction.transaction_type == 'cancellation':
            transaction.process(accounts, transactions.get(transaction.transaction))


def filter_transactions(transactions, account):
    return sorted([t for t in transactions.values() if (t.transaction_type == 'payment' and t.status == 'COMPLETE' and account.id in (t.sender_id, t.recipient_id))], key= lambda t: t.transaction_datetime)


def print_last_transaction(transactions, account):
    if transactions:
      print(f'Last transaction: {transactions[-1].transaction_datetime}')


def print_balance_changes_over_past_x_days_for_a_given_account(transactions, account, days):
    cutoff_date = datetime.now() - timedelta(days=days)
    transactions = [t for t in transactions if t.transaction_datetime > cutoff_date]
    balances = {}
    for transaction in transactions:
        if transaction.currency not in balances:
            balances[transaction.currency] = 0
        
        if account.id == transaction.sender_id:
            balances[transaction.currency] -= transaction.amount
        elif account.id == transaction.recipient_id:
            balances[transaction.currency] += transaction.amount
    
    print(f'Balances Change over Past {days} days: {balances}')


def check_fraud(transactions, account):
    count = 0
    for transaction in transactions:
        if account.id == transaction.sender_id:
            count += 1
        else:
            count = 0

    if count >= 3:
        account.status = 'FRAUD'


if __name__ == '__main__':
    with open(balances_filepath) as f:
        accounts = {account_data['id']: Account(**account_data) for account_data in load(f) }

    with open(payments_filepath) as f:
        transactions = {transaction_data['id']: Transaction.from_json(**transaction_data) for transaction_data in load(f)}

    process(accounts, transactions)

    for account in accounts.values():
        account_transactions = filter_transactions(transactions, account)
        print('')
        print(f'{account.name} - Balances: {account.balances}')
        print_last_transaction(account_transactions, account)
        print_balance_changes_over_past_x_days_for_a_given_account(account_transactions, account, 2)
        check_fraud(account_transactions, account)
        print(f'Status: {account.status}')

