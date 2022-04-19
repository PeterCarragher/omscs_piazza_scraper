# OMSCS scraper
For edstem.org, the REST API is used directly through pythons requests lib.
For Piazza, piazza-api is used.

## Setup
```
pip3 install networkx piazza-api
cd <download_dir>
python3 piazza_network_scraper.py
python3 EdTokenScript.py
python3 
```

Login with you Piazza credentials and specify the classes you would like to scrape.
When prompted to find the Piazza course code, visit the Piazza class and copy the last part of the URL (i.e for https://piazza.com/class/asdfghjkl, paste in \'asdfghjkl\').

For more information on piazza-api, theres a [tutorial on the repo](https://github.com/hfaran/piazza-api).

For more information on networkx, read [this great tutorial](https://programminghistorian.org/en/lessons/exploring-and-analyzing-network-data-with-python).

To visualise the network, open the .gexf export in [gephi](https://gephi.org/users/download/).


## Future work
Scrape from Slack API as well.

Integrate Piazza scraper into [GraphiPy](https://pypi.org/project/GraphiPy/).
