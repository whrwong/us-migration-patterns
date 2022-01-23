# US Migration Patterns

A common topic addressed is California's "Mass Exodus". 
In this project, we sought to answer questions such as:
How many people are moving out of and into California?
Where are they moving from and to?
How has this changed in recent pandemic years?
How can we best visualize this data?

## Process:
We first pulled data from the American Community Survey (ACS) Migration Flows API https://www.census.gov/data/developers/data-sets/acs-migration-flows.html that covers 5 years then created a database using PostgreSQL. We also manipulated the data to show relevent state information using Python before creating a Flask application to run our webpage application. D3 Javascript was used to design the final webpage and visualization. 

## End Result - Search Page and Visualization:
Our entire application consists of two parts. 
1. One page titled "The Great Migration" enables its user to type a year they want to see migration patterns and information from. 
2. Another page titled "US Immigration and Emigration" generates a map based on the census data. 
The size of the circles represent migrations to and from the corresponding state. Green circles indicate a positive net migration (more people moving to versus from the state). Red circles indicate a negative net migration (more people are moving from versus to the state). Users can hover their cursor over each state to view the raw numbers and click a state to view migration flows from that state to another state indicated by arrows. Green arrows indicate a net gain and red arrows indicate a net loss. The size of the arrow also represents the amount of people moving (thinner arrows mean less people moved, thicker arrows mean more people moved).
