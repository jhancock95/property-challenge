# Property Data Coding Challenge

### Approach

The approach taken took some simple steps:

* Define database classes
* Populate database
* Determine classes depending on database structure
* Determine methods necessary within classes to answer the questions provided

The classes are fairly sparse and some aspects written into them were unused in this project, but they lay the groundwork for building up an ORM system.

### Database Setup

All property data available is contained within the transactions file, so this is what will be worked from. Each transaction contains the PAON (primary ID), SAON (secondary ID) and postcode of a property.  While a primary ID combined with a postcode might isolate most properties, there’s still the issue of sub-addresses (e.g. blocks of flats). Combining the PAON, SAON and postcode alone ensures that each property is distinct without needing further data, allowing for the creation of a composite primary key in a seperate properties table (as seen in data_load_functions).

Using sqlite, a primary key is already inserted as rowid. However, in MSSQL it would be advantageous for the sake of simplicty and performance to include a seperate primary key (such as an autoincrementing integer) to avoid relying on a complex composite.

In a bigger project it may makes sense to normalise the database to third normal form. This would involve stripping out data from transactions irrelevant to the transaction itself (such as postcode) and putting these in the property table, replacing them with a single foreign key linking to the relevant property ID.

### Routes 

The following questions can be answered via use of API routes:

**Can you write a query that returns the transactions that took place in EC1A between 2018-04-01 and 2019-12-31?**

Dates will differ as only 2019-2020 data is used

> .../postcode_sales?postcode=EC1A&start_date=2019-04-01%end_date=2020-12-31

**Return the number of properties that have been sold in a postcode, and which transaction_ids refer to those.**

> .../postcode_sales?postcode=EC1A&id_only=yes

**Given a transaction_id, return which property it refers to**

>.../property_from_transaction_id?transaction_id={8F1B26BD-92BE-53DB-E053-6C04A8C03649}

**Which postcodes have seen the highest increase in transactions during the last 5 years?**

Only for 2019-2020

>.../transaction_amount_change

**Where is the ‘centre of gravity’ in terms of number of transactions of the population moving to every year?**

>.../migration?year=2020

**Can you plot the average transaction price of a postcode as a function of distance from EC1A?**

Average value of a property depending on what decile of distance they are from London

>.../distance_from_london

**Can you find any correlation between the average house prices and a CPI indicator?**

Note - this route relies on __cpi-inflation-index.csv__ and __Average-prices-2021-03.csv__ being in the data folder.

>.../inflation_measure

Can also be done with a custom inflation measure

>.../inflation_measure?measure=CPI wts: Unprocessed food GOODS

### Assumptions

As this is official government data, there is the assumption that it is accurate. This may not be the case with other data sources.


