# top10-imdb-sync

Description: This script logs into IMDb, scrapes the movies in your list, scrapes the Netflix Top 10 USA movies from FlixPatrol, retrieves the IMDb IDs through TMDB API, then updates your IMDb list by removing movies no longer in Top 10 list and adding Top 10 movies missing from your list.

Instructions: 
1. Install python if not installed, then install dependencies by running install-dependencies.bat
2. In the top10-imdb-sync.py fill the following or store in an .env file using python-dotenv:  
IMDB_USERNAME,
IMDB_PASSWORD,
IMDB_LIST_URL,
TMDB_API_KEY

