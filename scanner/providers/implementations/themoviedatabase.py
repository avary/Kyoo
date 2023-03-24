import asyncio
from datetime import datetime
import logging
from aiohttp import ClientSession
from typing import Awaitable, Callable, Coroutine, Dict, Optional, Any, TypeVar

from ..provider import Provider
from ..types.movie import Movie, MovieTranslation, Status as MovieStatus
from ..types.season import Season, SeasonTranslation
from ..types.episode import Episode, PartialShow
from ..types.studio import Studio
from ..types.genre import Genre
from ..types.metadataid import MetadataID
from ..types.show import Show, ShowTranslation, Status as ShowStatus


class TheMovieDatabase(Provider):
	def __init__(self, client: ClientSession, api_key: str) -> None:
		super().__init__()
		self._client = client
		self.base = "https://api.themoviedb.org/3"
		self.api_key = api_key
		self.genre_map = {
			28: Genre.ACTION,
			12: Genre.ADVENTURE,
			16: Genre.ANIMATION,
			35: Genre.COMEDY,
			80: Genre.CRIME,
			99: Genre.DOCUMENTARY,
			18: Genre.DRAMA,
			10751: Genre.FAMILY,
			14: Genre.FANTASY,
			36: Genre.HISTORY,
			27: Genre.HORROR,
			10402: Genre.MUSIC,
			9648: Genre.MYSTERY,
			10749: Genre.ROMANCE,
			878: Genre.SCIENCE_FICTION,
			53: Genre.THRILLER,
			10752: Genre.WAR,
			37: Genre.WESTERN,
		}

	async def get(self, path: str, *, params: dict[str, Any] = {}):
		params = {k: v for k, v in params.items() if v is not None}
		async with self._client.get(
			f"{self.base}/{path}", params={"api_key": self.api_key, **params}
		) as r:
			r.raise_for_status()
			return await r.json()

	T = TypeVar("T")

	async def process_translations(
		self, for_language: Callable[[str], Awaitable[T]], languages: list[str]
	) -> T:
		tasks = map(lambda lng: for_language(lng), languages)
		items: list[Any] = await asyncio.gather(*tasks)
		item = items[0]
		item.translations = {k: v.translations[k] for k, v in zip(languages, items)}
		return item

	def get_image(self, images: list[Dict[str, Any]]) -> list[str]:
		return [
			f"https://image.tmdb.org/t/p/original{x['file_path']}"
			for x in images
			if x["file_path"]
		]

	def to_studio(self, company: dict[str, Any]) -> Studio:
		return Studio(
			name=company["name"],
			logos=[f"https://image.tmdb.org/t/p/original{company['logo_path']}"]
			if "logo_path" in company
			else [],
			external_id={
				"themoviedatabase": MetadataID(
					company["id"], f"https://www.themoviedb.org/company/{company['id']}"
				)
			},
		)

	async def identify_movie(
		self, name: str, year: Optional[int], *, language: list[str]
	) -> Movie:
		search = (await self.get("search/movie", params={"query": name, "year": year}))[
			"results"
		][0]
		movie_id = search["id"]
		if search["original_language"] not in language:
			language.append(search["original_language"])

		async def for_language(lng: str) -> Movie:
			movie = await self.get(
				f"/movie/{movie_id}",
				params={
					"language": lng,
					"append_to_response": "alternative_titles,videos,credits,keywords,images",
				},
			)
			logging.debug("TMDb responded: %s", movie)
			# TODO: Use collection data

			ret = Movie(
				original_language=movie["original_language"],
				aliases=[x["title"] for x in movie["alternative_titles"]["titles"]],
				release_date=datetime.strptime(
					movie["release_date"], "%Y-%m-%d"
				).date(),
				status=MovieStatus.FINISHED
				if movie["status"] == "Released"
				else MovieStatus.PLANNED,
				studios=[self.to_studio(x) for x in movie["production_companies"]],
				genres=[
					self.genre_map[x["id"]]
					for x in movie["genres"]
					if x["id"] in self.genre_map
				],
				external_id={
					"themoviedatabase": MetadataID(
						movie["id"], f"https://www.themoviedb.org/movie/{movie['id']}"
					),
					"imdb": MetadataID(
						movie["imdb_id"],
						f"https://www.imdb.com/title/{movie['imdb_id']}",
					),
				}
				# TODO: Add cast information
			)
			translation = MovieTranslation(
				name=movie["title"],
				tagline=movie["tagline"],
				keywords=list(map(lambda x: x["name"], movie["keywords"]["keywords"])),
				overview=movie["overview"],
				posters=self.get_image(movie["images"]["posters"]),
				logos=self.get_image(movie["images"]["logos"]),
				thumbnails=self.get_image(movie["images"]["backdrops"]),
				trailers=[
					f"https://www.youtube.com/watch?v{x['key']}"
					for x in movie["videos"]["results"]
					if x["type"] == "Trailer" and x["site"] == "YouTube"
				],
			)
			ret.translations = {lng: translation}
			return ret

		return await self.process_translations(for_language, language)

	async def identify_show(
		self,
		show: PartialShow,
		*,
		language: list[str],
	) -> Show:
		show_id = show.external_id["themoviedatabase"].id
		if show.original_language not in language:
			language.append(show.original_language)

		async def for_language(lng: str) -> Show:
			show = await self.get(
				f"/tv/{show_id}",
				params={
					"language": lng,
					"append_to_response": "alternative_titles,videos,credits,keywords,images",
				},
			)
			logging.debug("TMDb responded: %s", show)
			# TODO: Use collection data

			ret = Show(
				original_language=show["original_language"],
				aliases=[x["title"] for x in show["alternative_titles"]["titles"]],
				start_air=datetime.strptime(show["first_air_date"], "%Y-%m-%d").date(),
				end_air=datetime.strptime(show["last_air_date"], "%Y-%m-%d").date(),
				status=ShowStatus.FINISHED
				if show["status"] == "Released"
				else ShowStatus.AIRING
				if show["in_production"]
				else ShowStatus.FINISHED,
				studios=[self.to_studio(x) for x in show["production_companies"]],
				genres=[
					self.genre_map[x["id"]]
					for x in show["genres"]
					if x["id"] in self.genre_map
				],
				external_id={
					"themoviedatabase": MetadataID(
						show["id"], f"https://www.themoviedb.org/tv/{show['id']}"
					),
					"imdb": MetadataID(
						show["imdb_id"],
						f"https://www.imdb.com/title/{show['imdb_id']}",
					),
				},
				seasons=[
					self.to_season(x, language=lng, show_id=show["id"])
					for x in show["seasons"]
				],
				# TODO: Add cast information
			)
			translation = ShowTranslation(
				name=show["name"],
				tagline=show["tagline"],
				keywords=list(map(lambda x: x["name"], show["keywords"]["keywords"])),
				overview=show["overview"],
				posters=self.get_image(show["images"]["posters"]),
				logos=self.get_image(show["images"]["logos"]),
				thumbnails=self.get_image(show["images"]["backdrops"]),
				trailers=[
					f"https://www.youtube.com/watch?v{x['key']}"
					for x in show["videos"]["results"]
					if x["type"] == "Trailer" and x["site"] == "YouTube"
				],
			)
			ret.translations = {lng: translation}
			return ret

		ret = await self.process_translations(for_language, language)
		return ret

	def to_season(
		self, season: dict[str, Any], *, language: str, show_id: str
	) -> Season:
		return Season(
			season_number=season["season_number"],
			start_date=datetime.strptime(season["air_date"], "%Y-%m-%d").date(),
			end_date=None,
			external_id={
				"themoviedatabase": MetadataID(
					season["id"],
					f"https://www.themoviedb.org/tv/{show_id}/season/{season['season_number']}",
				)
			},
			translations={
				language: SeasonTranslation(
					name=season["name"],
					overview=season["overview"],
					poster=[
						f"https://image.tmdb.org/t/p/original{season['poster_path']}"
					]
					if "poster_path" in season
					else [],
					thumbnails=[],
				)
			},
		)

	async def identify_episode(
		self,
		name: str,
		season: Optional[int],
		episode: Optional[int],
		absolute: Optional[int],
		*,
		language: list[str],
	) -> Episode:
		search = (await self.get("search/tv", params={"query": name}))["results"][0]
		show_id = search["id"]
		if search["original_language"] not in language:
			language.append(search["original_language"])

		async def for_language(lng: str) -> Episode:
			movie = await self.get(
				f"/movie/{show_id}",
				params={
					"language": lng,
					"append_to_response": "alternative_titles,videos,credits,keywords,images",
				},
			)
			logging.debug("TMDb responded: %s", movie)
			# TODO: Use collection data

			ret = Movie(
				original_language=movie["original_language"],
				aliases=[x["title"] for x in movie["alternative_titles"]["titles"]],
				release_date=datetime.strptime(
					movie["release_date"], "%Y-%m-%d"
				).date(),
				status=MovieStatus.FINISHED
				if movie["status"] == "Released"
				else MovieStatus.PLANNED,
				studios=[self.to_studio(x) for x in movie["production_companies"]],
				genres=[
					self.genre_map[x["id"]]
					for x in movie["genres"]
					if x["id"] in self.genre_map
				],
				external_id={
					"themoviedatabase": MetadataID(
						movie["id"], f"https://www.themoviedb.org/movie/{movie['id']}"
					),
					"imdb": MetadataID(
						movie["imdb_id"],
						f"https://www.imdb.com/title/{movie['imdb_id']}",
					),
				}
				# TODO: Add cast information
			)
			translation = MovieTranslation(
				name=movie["title"],
				tagline=movie["tagline"],
				keywords=list(map(lambda x: x["name"], movie["keywords"]["keywords"])),
				overview=movie["overview"],
				posters=self.get_image(movie["images"]["posters"]),
				logos=self.get_image(movie["images"]["logos"]),
				thumbnails=self.get_image(movie["images"]["backdrops"]),
				trailers=[
					f"https://www.youtube.com/watch?v{x['key']}"
					for x in movie["videos"]["results"]
					if x["type"] == "Trailer" and x["site"] == "YouTube"
				],
			)
			ret.translations = {lng: translation}
			return ret

		return self.process_translations(for_language, language)