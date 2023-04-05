# Import time module to add delays between actions
import time

# Import json module to handle JSON data
import json

# Import threading module to create and manage separate threads for parallel execution
import threading

# Import tkinter module for creating the graphical user interface (GUI)
from tkinter import *

# Import Web3 module to interact with the Ethereum blockchain
from web3 import Web3
import web3

# Import geth_poa_middleware for Proof of Authority (PoA) networks compatibility
from web3.middleware import geth_poa_middleware

from ui import create_ui, run_ui, update_status_label, update_transactions_count_label, update_total_gas_spent_label

from urllib3.exceptions import MaxRetryError


# Load contract ABI from the xenftABI.json file
with open('xenftABI.json') as abi_file:
    contract_abi = json.load(abi_file)

stop_flag = False

def send_transactions(status_label, transactions_count_label, total_gas_spent_label):
    """
    Function to send a specified number of transactions, monitor their status,
    and update the UI elements accordingly.
    """
    global stop_flag

    try:
        # Get user input for Ethereum node URL and contract address
        eth_node_url = eth_node_url_entry.get()
        contract_address = contract_address_entry.get()
        
        # Initialize Web3 instance and contract object
        w3 = Web3(Web3.HTTPProvider(eth_node_url))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        
        # Get user input for private key and derive the corresponding address
        private_key = private_key_entry.get()
        my_address = w3.eth.account.from_key(private_key).address

        # Get user input for transaction parameters
        count = int(count_entry.get())
        term = int(term_entry.get())
        max_gas_price = int(max_gas_price_entry.get()) * 10**9
        loops = int(loops_entry.get())
        chain_id = int(chain_id_entry.get())

        # Initialize the counters for the number of transactions and total gas spent
        transactions_count = 0
        total_gas_spent = 0

        # Get the current nonce 
        nonce = w3.eth.get_transaction_count(my_address)    

        # Loop for the specified number of transactions
        for i in range(loops):

            if stop_flag:
                stop_flag = False
                status_label.config(text=f'Stopped at transaction {i+1}')
                break

            gas_price = w3.eth.gas_price

            # Loop until the gas price is within the specified limit
            while gas_price > max_gas_price:
                # If the gas price is too high, update the status label and wait for 60 seconds
                gas_price_gwei = w3.from_wei(gas_price, 'gwei')
                status_label.config(text=f'Gas price too high: {gas_price_gwei:.4f} Gwei, waiting...')
                time.sleep(60)
                gas_price = w3.eth.gas_price

            # Create a function call to bulkClaimRank with the given count and term
            function_call = contract.functions.bulkClaimRank(count, term)

            # Estimate the gas needed for the transaction
            gas_estimate = function_call.estimate_gas({'from': my_address})

            # Build the transaction object
            transaction_data = function_call._encode_transaction_data()
            txn = {
                'from': my_address,
                'to': contract_address,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': chain_id,
                'data': transaction_data,
            }
    

            # Sign the transaction using the private key and chain ID
            signed_txn = w3.eth.account.sign_transaction(txn, private_key)
                
            # Send the signed transaction and get the transaction hash
            retry = True
            while retry:
                    try:
                        txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                        retry = False
                    except ValueError as e:
                        error_data = e.args[0]
                        if isinstance(error_data, dict) and error_data.get('message') == 'already known':
                            status_label.config(text=f'Transaction {i+1} already known, retrying...')
                            time.sleep(5)  # Wait for 5 seconds before retrying
                        elif isinstance(error_data, dict) and error_data.get('message') == 'nonce too low':
                            status_label.config(text=f'Transaction {i+1} nonce too low, retrying...')
                            nonce = w3.eth.get_transaction_count(my_address)  # Update the nonce
                            txn['nonce'] = nonce
                            signed_txn = w3.eth.account.sign_transaction(txn, private_key)  # Sign the transaction with the updated nonce
                            time.sleep(5)  # Wait for 5 seconds before retrying
                        else:
                            raise  # Re-raise the exception if it's not an "already known" or "nonce too low" error

                    except MaxRetryError:
                        status_label.config(text=f'Max retries exceeded for transaction {i+1}, waiting and retrying...')
                        time.sleep(30)  # Wait for 30 seconds before retrying



            # Update the status label with the transaction hash
            status_label.config(text=f'Sent transaction {i+1} with hash {txn_hash.hex()}')


            try:
                txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash, timeout=300)
            except web3.exceptions.TimeExhausted:
                current_gas_price = w3.eth.gas_price
                min_gas_price = gas_price * 1.1  # At least a 10% increase in gas price
                
                if min_gas_price < current_gas_price <= max_gas_price:
                    # Replace the transaction with a higher gas price
                    status_label.config(text=f'Transaction {i+1} still pending, replacing with a higher gas price...')
                    
                    # Use the current gas price, ensuring it's at least 10% higher than the original gas price
                    gas_price = current_gas_price
                    txn['gasPrice'] = gas_price

                    # Sign the transaction again with the new gas price
                    signed_txn = w3.eth.account.sign_transaction(txn, private_key)

                    # Send the signed transaction and get the new transaction hash
                    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

                    # Wait for the replaced transaction to be confirmed
                    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash, timeout=1800)
                elif current_gas_price > gas_price:
                    status_label.config(text=f'Transaction {i+1} still pending due to gas price spike, waiting...')
                    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash, timeout=1800)  # Wait longer, e.g., 1800 seconds
                else:
                    raise  # Re-raise the exception if the gas price hasn't spiked

                
            # Update the status label with the block number the transaction was confirmed in
            status_label.config(text=f'Transaction {i+1} confirmed in block {txn_receipt["blockNumber"]}')

            # Update the counters when a transaction is confirmed
            transactions_count += 1
            gas_spent = txn_receipt['gasUsed'] * gas_price
            total_gas_spent += gas_spent

            # Update the labels with the new values
            transactions_count_label.config(text=f"XENfts Minted: {transactions_count}")
            total_gas_spent_label.config(text=f"Total Gas Spent: {w3.from_wei(total_gas_spent, 'ether'):.4f}")


            # Update the status label with the block number the transaction was confirmed in
            status_label.config(text=f'Transaction {i+1} confirmed in block {txn_receipt["blockNumber"]}')
            nonce +=1

            # Sleep for 5 seconds before the next iteration
            time.sleep(5)
        else:
            # If the gas price is too high, update the status label and wait for 60 seconds
            gas_price_gwei = w3.from_wei(gas_price, 'gwei')
            status_label.config(text=f'Gas price too high: {gas_price_gwei:.4f} Gwei, waiting...')
            time.sleep(60)

    except Exception as e:
        # If there is an unexpected error, update the UI background color and status label
        root.config(bg='red')
        status_label.config(text=f'Error: {str(e)}', bg='red')


def toggle_key_visibility():
    if private_key_entry.config('show')[-1] == '*':
        private_key_entry.config(show='')
        toggle_key_visibility_button.config(text='Hide')
    else:
        private_key_entry.config(show='*')
        toggle_key_visibility_button.config(text='Show')

def start_thread(status_label, transactions_count_label, total_gas_spent_label):
    # Reset the stop_flag before starting a new thread
    global stop_flag
    stop_flag = False
    # Start a new thread for the send_transactions function
    threading.Thread(target=send_transactions, args=(status_label, transactions_count_label, total_gas_spent_label)).start()


def stop_transactions():
    global stop_flag
    stop_flag = True

# Create the UI
root, eth_node_url_entry, contract_address_entry, private_key_entry, count_entry, term_entry, max_gas_price_entry, loops_entry, chain_id_entry = create_ui(send_transactions, stop_transactions, toggle_key_visibility, start_thread)


# Run the UI
run_ui(root)
