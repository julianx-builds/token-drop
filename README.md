# Token Dropper
## Description
Token drop is a tool for businesses operating on Cardano looking to finish off an ISPO or simply airdrop tokens. The tool is lightweight and can be used by users with very limited knowledge in the Cardano environment. The tool will automate:
* The collection of delegator data on the chain.
* The calculation of how many tokens will go to each delegator/address.
* The process of building TXs for a large amount of addresses.
* The sumbition of those TXs onto the cardano chain. Will require a cardano node running, unless I can find a way to submit them through an API :)

## Installation
`git clone https://github.com/julianx-builds/token-drop`

## Requirements
Python version is >=3.6

## Usage
### For people looking to finish off ISPOs:
Edit the USER VARIABLES found at .env including the poolID (in bech32), epoch_min, epoch_max and rate.

Run `python3 populateDB.py`

### For people looking to airdrop tokens (Requires a list of Cardano addresses):

## TODO
* Collect delegation payment tx to find address that payed for delegation
* Implement cardano-mass-payments repo to build TXs
* Automate submitting TXs to chain
