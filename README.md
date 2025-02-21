# top10-imdb-sync

Description: This script logs into IMDb, scrapes the movies in your list, scrapes the Netflix Top 10 USA movies from FlixPatrol, retrieves the IMDb IDs through TMDB API, then updates your IMDb list by removing movies no longer in Top 10 list and adding Top 10 movies missing from your list.

Instructions: Fill in or store the following in an .env file using python-dotenv:  
IMDB_USERNAME,
IMDB_PASSWORD,
IMDB_LIST_URL,
TMDB_API_KEY

