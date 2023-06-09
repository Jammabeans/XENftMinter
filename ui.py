from tkinter import *
import time

network_var = None
eth_node_url_entry = None
contract_address_entry = None
chain_id_entry = None

def create_ui(send_transactions_callback, stop_transactions_callback, toggle_key_visibility_callback, start_thread_callback):
    global network_var, eth_node_url_entry, contract_address_entry, chain_id_entry
    root = Tk()
    root.title("Bulk XENft minter")

    # Add column spacing for all columns
    column_spacing = 20
    for i in range(5):  # Adjust the range according to the number of columns
        root.columnconfigure(i, minsize=column_spacing)
    root.configure(bg='white')

    # Define padding values for consistent spacing
    padding_x = 10
    padding_y = 10

    # Create and place the private key input field
    private_key_label = Label(root, text="Private Key:", bg='white')
    private_key_label.grid(row=0, column=0, padx=padding_x, pady=padding_y)
    private_key_entry = Entry(root, width=50, show='*')
    toggle_key_visibility_button = Button(root, text="Show", command=toggle_key_visibility_callback, bg='white')
    toggle_key_visibility_button.grid(row=0, column=2, padx=padding_x, pady=padding_y)
    private_key_entry.grid(row=0, column=1, padx=padding_x, pady=padding_y)

    # Create and place the Ethereum node URL input field
    eth_node_url_label = Label(root, text="Ethereum Node URL:", bg='white')
    eth_node_url_label.grid(row=1, column=0, padx=padding_x, pady=padding_y)
    eth_node_url_entry = Entry(root, width=50)
    eth_node_url_entry.grid(row=1, column=1, padx=padding_x, pady=padding_y)
      

    # Create and place the contract address input field
    contract_address_label = Label(root, text="Contract Address:", bg='white')
    contract_address_label.grid(row=3, column=0, padx=padding_x, pady=padding_y)
    contract_address_entry = Entry(root, width=50)
    contract_address_entry.grid(row=3, column=1, padx=padding_x, pady=padding_y)
    

    # Create and place the count input field
    count_label = Label(root, text="VUMs per XENft:", bg='white')
    count_label.grid(row=4, column=0, padx=padding_x, pady=padding_y)
    count_entry = Entry(root, width=50)
    count_entry.grid(row=4, column=1, padx=padding_x, pady=padding_y)
    count_entry.insert(0, '5')

    # Create and place the term input field
    term_label = Label(root, text="Number of Days:", bg='white')
    term_label.grid(row=5, column=0, padx=padding_x, pady=padding_y)
    term_entry = Entry(root, width=50)
    term_entry.grid(row=5, column=1, padx=padding_x, pady=padding_y)
    term_entry.insert(0, '400')

    # Create and place the max gas price input field
    max_gas_price_label = Label(root, text="Max Gas Price (Gwei):", bg='white')
    max_gas_price_label.grid(row=6, column=0, padx=padding_x, pady=padding_y)
    max_gas_price_entry = Entry(root, width=50)
    max_gas_price_entry.grid(row=6, column=1, padx=padding_x, pady=padding_y)
    max_gas_price_entry.insert(0, '3')

    # Create and place the loops input field
    loops_label = Label(root, text="Number of XENft's:", bg='white')
    loops_label.grid(row=7, column=0, padx=padding_x, pady=padding_y)
    loops_entry = Entry(root, width=50)
    loops_entry.grid(row=7, column=1, padx=padding_x, pady=padding_y)
    loops_entry.insert(0, '100') 

    # Create and place the chain ID input field
    chain_id_label = Label(root, text="Chain ID:", bg='white')
    chain_id_label.grid(row=8, column=0, padx=padding_x, pady=padding_y)
    chain_id_entry = Entry(root, width=50)
    chain_id_entry.grid(row=8, column=1, padx=padding_x, pady=padding_y)
    

    network_label = Label(root, text="Network:", bg='white')
    network_label.grid(row=5, column=3, padx=padding_x, pady=padding_y)

    network_var = StringVar(root)
    network_var.set('Ethereum')  # Set default value

    networks = ['Ethereum', 'BSC', 'Polygon', 'Avalanche C', 'Ethereum PoW', 'Moonbeam', 'Evmos', 'Fantom']  # Add more networks here if needed
    network_dropdown = OptionMenu(root, network_var, *networks)
    network_dropdown.grid(row=6, column=3, padx=padding_x, pady=padding_y)
    network_dropdown.config(bg='white')

    # Update the input fields when the network_var changes
    network_var.trace('w', update_inputs)

    # Create and place the start button that triggers the start_thread function
    start_button = Button(root, text="Start", command=lambda: start_thread_callback(status_label, transactions_count_label, total_gas_spent_label), bg='white')
    start_button.grid(row=9, column=0, columnspan=2, padx=padding_x, pady=padding_y)

    # Create and place the stop button that triggers the stop_thread function
    stop_button = Button(root, text="Stop", command=stop_transactions_callback, bg='white')
    stop_button.grid(row=9, column=1, padx=padding_x, pady=padding_y)

    status_label = Label(root, text="Status:", bg='white')
    status_label.grid(row=10, column=0, columnspan=2, padx=padding_x, pady=padding_y)

    # Add the labels for the number of transactions and total gas spent
    transactions_count_label = Label(root, text="Transactions: 0", bg='white')
    transactions_count_label.grid(row=0, column=3, padx=padding_x, pady=padding_y)

    total_gas_spent_label = Label(root, text="Total Gas Spent: 0", bg='white')
    total_gas_spent_label.grid(row=1, column=3, padx=padding_x, pady=padding_y)

    # Add an empty label with a specified height below the status label
    spacer_label = Label(root, text="", bg='white', height=2)
    spacer_label.grid(row=11, column=0, columnspan=2)

    return root, eth_node_url_entry, contract_address_entry, private_key_entry, count_entry, term_entry, max_gas_price_entry, loops_entry, chain_id_entry


def update_status_label(status):
    status_label.config(text=status)

def update_transactions_count_label(count):
    transactions_count_label.config(text=f"Transactions: {count}")

def update_total_gas_spent_label(total_gas_spent):
    total_gas_spent_label.config(text=f"Total Gas Spent: {total_gas_spent:.4f}")


def toggle_key_visibility():
    if private_key_entry.config('show')[-1] == '*':
        private_key_entry.config(show='')
        toggle_key_visibility_button.config(text='Hide')
    else:
        private_key_entry.config(show='*')
        toggle_key_visibility_button.config(text='Show')

def start_thread(send_transactions):
    # Reset the stop_flag before starting a new thread
    global stop_flag
    stop_flag = False
    # Start a new thread for the send_transactions function
    threading.Thread(target=send_transactions).start()

def update_inputs(*args):
    global network_var, eth_node_url_entry, contract_address_entry, chain_id_entry
    selected_network = network_var.get()
    
    if selected_network == 'Ethereum':
        eth_node_url_entry.delete(0, END)
        eth_node_url_entry.insert(0, 'https://mainnet.infura.io/v3/')
        contract_address_entry.delete(0, END)
        contract_address_entry.insert(0, '0x06450dEe7FD2Fb8E39061434BAbCFC05599a6Fb8')
        chain_id_entry.delete(0, END)
        chain_id_entry.insert(0, '1')
    elif selected_network == 'BSC':
        eth_node_url_entry.delete(0, END)
        eth_node_url_entry.insert(0, 'https://bsc-dataseed.binance.org/')
        contract_address_entry.delete(0, END)
        contract_address_entry.insert(0, '0x1Ac17FFB8456525BfF46870bba7Ed8772ba063a5')
        chain_id_entry.delete(0, END)
        chain_id_entry.insert(0, '56')
    elif selected_network == 'Polygon':
        eth_node_url_entry.delete(0, END)
        eth_node_url_entry.insert(0, 'https://rpc-mainnet.maticvigil.com/')
        contract_address_entry.delete(0, END)
        contract_address_entry.insert(0, '0x726bB6aC9b74441Eb8FB52163e9014302D4249e5')
        chain_id_entry.delete(0, END)
        chain_id_entry.insert(0, '137')
    elif selected_network == 'Avalanche Mainnet':
        eth_node_url_entry.delete(0, END)
        eth_node_url_entry.insert(0, 'https://api.avax.network/ext/bc/C/rpc')
        contract_address_entry.delete(0, END)
        contract_address_entry.insert(0, '0x94d9E02D115646DFC407ABDE75Fa45256D66E043')
        chain_id_entry.delete(0, END)
        chain_id_entry.insert(0, '43114') 
    elif selected_network == 'Ethereum PoW':
        eth_node_url_entry.delete(0, END)
        eth_node_url_entry.insert(0, 'https://mainnet.ethereumpow.org')
        contract_address_entry.delete(0, END)
        contract_address_entry.insert(0, '0x94d9E02D115646DFC407ABDE75Fa45256D66E043')
        chain_id_entry.delete(0, END)
        chain_id_entry.insert(0, '10001') 
    elif selected_network == 'Moonbeam':
        eth_node_url_entry.delete(0, END)
        eth_node_url_entry.insert(0, 'https://rpc.api.moonbeam.network')
        contract_address_entry.delete(0, END)
        contract_address_entry.insert(0, '0x94d9E02D115646DFC407ABDE75Fa45256D66E043')
        chain_id_entry.delete(0, END)
        chain_id_entry.insert(0, '1284')
    elif selected_network == 'Evmos':
        eth_node_url_entry.delete(0, END)
        eth_node_url_entry.insert(0, 'https://eth.bd.evmos.org:8545')
        contract_address_entry.delete(0, END)
        contract_address_entry.insert(0, '0x4c4CF206465AbFE5cECb3b581fa1b508Ec514692')
        chain_id_entry.delete(0, END)
        chain_id_entry.insert(0, '9001') 
    elif selected_network == 'Fantom':
        eth_node_url_entry.delete(0, END)
        eth_node_url_entry.insert(0, 'https://rpc.ankr.com/fantom')
        contract_address_entry.delete(0, END)
        contract_address_entry.insert(0, '0x94d9E02D115646DFC407ABDE75Fa45256D66E043')
        chain_id_entry.delete(0, END)
        chain_id_entry.insert(0, '250')   
      



def run_ui(root):
    root.mainloop()
    