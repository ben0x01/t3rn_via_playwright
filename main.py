import asyncio
import random
from web3 import Web3
from playwright.async_api import async_playwright, expect

EXTENSIONS_PATH = r"C:\Users\user\AppData\Local\Google\Chrome\User Data\Default\Extensions\nkbihfbeogaeaoehlefnkodbefgpgknn\12.4.1_0"
MM_PASSWORD = "B7601As5T78"

# Configuration for networks
NETWORK_CONFIG = {
    "Arbitrum Sepolia": {
        "RPC_URL": "https://arb-sepolia.g.alchemy.com/v2/tKHLQ21rwL-KSqVQMYeiLrIpEnlNL7_I"
    },
    "OP Sepolia": {
        "RPC_URL": "https://opt-sepolia.g.alchemy.com/v2/tKHLQ21rwL-KSqVQMYeiLrIpEnlNL7_I"
    },
    "Base Sepolia": {
        "RPC_URL": "https://base-sepolia.g.alchemy.com/v2/tKHLQ21rwL-KSqVQMYeiLrIpEnlNL7_I"
    }
}

# Список сетей для случайного выбора
NETWORKS = list(NETWORK_CONFIG.keys())


# Function to randomly choose a network key
def choose_random_network():
    return random.choice(NETWORKS)


# Function to choose a different network from the first selected network
def choose_different_network(exclude_network):
    other_networks = [network for network in NETWORKS if network != exclude_network]
    return random.choice(other_networks)


# Function to get the balance of your wallet on a chosen network and check if it's above 0.1 ETH
def get_wallet_balance(network_key, wallet_address):
    network = NETWORK_CONFIG[network_key]
    rpc_url = network["RPC_URL"]

    # Connect to Web3
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"Failed to connect to {network_key} RPC URL")
        return None

    # Get balance for your wallet address
    balance = w3.eth.get_balance(wallet_address)
    balance_in_ether = w3.from_wei(balance, 'ether')
    print(f"Balance of wallet {wallet_address} on {network_key}: {balance_in_ether} Ether")

    # Check if balance is greater than 0.1 ETH
    return balance_in_ether > 0.1


async def main(seed_phrase, wallet_address):

    first_network = choose_random_network()
    if not get_wallet_balance(first_network, wallet_address):
        print(f"Insufficient balance on {first_network}. Exiting...")
        return

    second_network = choose_different_network(first_network)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            '',
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                f"--disable-extensions-except={EXTENSIONS_PATH}",
                f"--load-extension={EXTENSIONS_PATH}"
            ],
        )

        titles = [await page.title() for page in context.pages]
        while "MetaMask" not in titles:
            titles = [await page.title() for page in context.pages]

        mm_page = context.pages[1]
        await mm_page.wait_for_load_state()

        await asyncio.sleep(1)
        checkbox = mm_page.locator('//*[@id="onboarding__terms-checkbox"]')
        await mm_page.wait_for_load_state(state='domcontentloaded')
        await checkbox.click()

        import_wallet = mm_page.get_by_test_id(test_id="onboarding-import-wallet")
        await expect(import_wallet).to_be_enabled()
        await import_wallet.click()

        i_dont_agree = mm_page.get_by_test_id(test_id="metametrics-no-thanks")
        await expect(i_dont_agree).to_be_enabled()
        await i_dont_agree.click()

        for i in range(12):
            await mm_page.get_by_test_id(test_id=f'import-srp__srp-word-{i}').fill(seed_phrase[i])

        confirm_seed = mm_page.get_by_test_id(test_id="import-srp-confirm")
        await expect(confirm_seed).to_be_enabled()
        await confirm_seed.click()

        await mm_page.get_by_test_id(test_id='create-password-new').fill(MM_PASSWORD)
        await mm_page.get_by_test_id(test_id='create-password-confirm').fill(MM_PASSWORD)
        terms_button = mm_page.get_by_test_id(test_id="create-password-terms")
        await expect(terms_button).to_be_enabled()
        await terms_button.click()

        terms_button_2 = mm_page.get_by_test_id(test_id="create-password-import")
        await expect(terms_button_2).to_be_enabled()
        await terms_button_2.click()

        terms_button_3 = mm_page.get_by_test_id(test_id="onboarding-complete-done")
        await expect(terms_button_3).to_be_enabled()
        await terms_button_3.click()

        terms_button_5 = mm_page.get_by_test_id(test_id="pin-extension-next")
        await expect(terms_button_5).to_be_enabled()
        await terms_button_5.click()

        terms_button_6 = mm_page.get_by_test_id(test_id="pin-extension-done")
        await expect(terms_button_6).to_be_enabled()
        await terms_button_6.click()

        await asyncio.sleep(5)

        await mm_page.goto("https://bridge.t1rn.io/")
        await mm_page.wait_for_load_state(state='domcontentloaded')
        await asyncio.sleep(10)
        await mm_page.wait_for_load_state()

        await mm_page.locator("button:has-text('Confirm')").click()

        await asyncio.sleep(10)

        await mm_page.locator("xpath=//*[@id='radix-:r0:']/div").click()

        await asyncio.sleep(10)

        await mm_page.locator("xpath=//*[@id='radix-:r1:']/button").click()

        await asyncio.sleep(10)

        await mm_page.evaluate('''() => {
            document.querySelector('[data-testid="rk-wallet-option-io.metamask"]').click();
        }''')

        await asyncio.sleep(10)

        pages = context.pages
        mm_page = context.pages[-1]
        await mm_page.bring_to_front()
        await asyncio.sleep(5)

        terms_button_7 = mm_page.get_by_test_id(test_id="page-container-footer-next")
        await expect(terms_button_7).to_be_enabled()
        await terms_button_7.click()

        await asyncio.sleep(5)

        terms_button_8 = mm_page.get_by_test_id(test_id="page-container-footer-next")
        await expect(terms_button_8).to_be_enabled()
        await terms_button_8.click()
        await asyncio.sleep(3)

        terms_button = mm_page.get_by_test_id(test_id="confirmation-submit-button")
        await expect(terms_button).to_be_enabled()
        await terms_button.click()

        await asyncio.sleep(3)

        terms_button_1 = mm_page.get_by_test_id(test_id="confirmation-submit-button")
        await expect(terms_button_1).to_be_enabled()
        await terms_button_1.click()

        await asyncio.sleep(10)
        mm_page = context.pages[1]
        await mm_page.wait_for_load_state()
        print("Wallet connected and ready")

        # Открываем UI для выбора сети
        await mm_page.evaluate('''() => {
            document.querySelector('[data-testid="ui-select-network-and-asset"]').click();
        }''')
        await asyncio.sleep(5)

        # Клик по первой сети, используя `evaluate`
        await mm_page.evaluate(f'''(network) => {{
            const element = Array.from(document.querySelectorAll("span")).find(el => el.textContent.includes(network));
            if (element) {{
                const parentButton = element.closest("button");
                if (parentButton) {{
                    parentButton.scrollIntoView();
                    parentButton.click();
                }} else {{
                    console.log("Parent button not found for network:", network);
                }}
            }} else {{
                console.log("Network element not found:", network);
            }}
        }}''', first_network)
        print(f"Clicked on first network: {first_network}")
        await asyncio.sleep(10)

        # Клик по второй сети, используя `evaluate`
        await mm_page.evaluate('''() => {
            const xpath = "/html/body/div[1]/div/div/div/div/div/div[2]/div[2]/div/div/section/div[2]/form/div/div[1]/div[2]/div/div[1]/div[1]/button";
            const element = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;

            if (element) {
                element.scrollIntoView();
                element.click();
            } else {
                console.log("Element not found using XPath.");
            }
        }''')
        await asyncio.sleep(2)

        await mm_page.evaluate(f'''(network) => {{
            const spanElement = Array.from(document.querySelectorAll("span")).find(el => el.textContent.includes(network));
            if (spanElement) {{
                spanElement.scrollIntoView();
                spanElement.click();
            }} else {{
                console.log("Span with network text not found:", network);
            }}
        }}''', second_network)

        await asyncio.sleep(10)

        await mm_page.evaluate('''() => {
            const input = document.querySelector("input[data-testid='ui-max-reward-input']");
            if (input) {
                input.value = "0.1";  // Set the value to "0.1"
                input.dispatchEvent(new Event('input', { bubbles: true })); // Trigger input event
            } else {
                console.log("Input element not found.");
            }
        }''')

        await asyncio.sleep(10)

        await mm_page.evaluate(f'''(network) => {{
            const button = Array.from(document.querySelectorAll("button")).find(el => el.textContent.includes("Connect to " + network));
            if (button) {{
                button.scrollIntoView();
                button.click();
            }} else {{
                console.log("Button with text 'Connect to " + network + "' not found.");
            }}
        }}''', first_network)

        await asyncio.sleep(10)

        pages = context.pages
        mm_page = context.pages[-1]
        await mm_page.bring_to_front()
        await asyncio.sleep(5)

        terms_button_7 = mm_page.get_by_test_id(test_id="confirmation-submit-button")
        await expect(terms_button_7).to_be_enabled()
        await terms_button_7.click()

        terms_button_8 = mm_page.get_by_test_id(test_id="confirmation-submit-button")
        await expect(terms_button_8).to_be_enabled()
        await terms_button_8.click()

        await asyncio.sleep(10)
        mm_page = context.pages[1]
        await mm_page.wait_for_load_state()
        print("Wallet connected and ready")

        await mm_page.evaluate('''() => {
            const input = document.querySelector("input[data-testid='ui-max-reward-input']");
            if (input) {
                input.value = "0.1";  // Set the value to "0.1"
                input.dispatchEvent(new Event('input', { bubbles: true })); // Trigger input event
            } else {
                console.log("Input element not found.");
            }
        }''')

        await mm_page.reload()

        await asyncio.sleep(10)

        await mm_page.locator('input[type="text"][data-testid="ui-max-reward-input"]').click()

        await asyncio.sleep(10)

        input_selector = 'input[type="text"][data-testid="ui-max-reward-input"]'
        await mm_page.fill(input_selector, '0.1')

        await asyncio.sleep(10)

        await mm_page.locator("button:has-text('Confirm transaction')").click()

        await asyncio.sleep(10)

        pages = context.pages
        mm_page = context.pages[-1]
        await mm_page.bring_to_front()
        await asyncio.sleep(5)

        terms_button_7 = mm_page.get_by_test_id(test_id="confirm-footer-button")
        await expect(terms_button_7).to_be_enabled()
        await terms_button_7.click()

        await asyncio.sleep(10)

        await context.close()

if __name__ == "__main__":
    with open('seed.txt', 'r') as seed_file, open('wallets.txt', 'r') as wallet_file:
        seeds = [line.strip() for line in seed_file.readlines()]
        addresses = [line.strip() for line in wallet_file.readlines()]

    if len(seeds) != len(addresses):
        print("Количество сид фраз и адресов кошельков не совпадает.")
    else:
        for seed, address in zip(seeds, addresses):
            asyncio.run(main(seed, address))

