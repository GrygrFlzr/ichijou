"""
Build the static HTML file to stdout
"""
from typing import List
from os import environ
from datetime import datetime, timezone
from json import loads
from httpx import get
from markdown import markdown


class Group:
    """
    /groups data subset
    """

    def __init__(self, id: int, name: str, acronym: str, icon: str, shows):
        self.id = id
        self.name = name
        self.acronym = acronym
        self.icon_url = icon
        if isinstance(shows, list) and len(shows) > 0:
            if isinstance(shows[0], Show):
                self.shows: List[Show] = shows
            else:  # type == dict
                self.shows: List[Show] = []
                for show in shows:
                    self.shows.append(Show(**show))
        else:
            self.shows = []


class Show:
    """
    /groups/:id/shows subset
    """

    def __init__(
        self,
        id: int,
        name: str,
        status: str or None,
        progress: str,
        created_at: str,
        updated_at: str,
        poster: str,
        joint_groups,
        episodes,
    ):
        self.id = id
        self.name = name
        if status == "" or status is None:
            self.status = ""
        else:
            self.status = status
        self.complete = progress == "Complete"
        self.created_at = datetime.fromisoformat(created_at)
        self.updated_at = datetime.fromisoformat(updated_at)
        self.poster_url = poster

        if isinstance(episodes, list) and len(episodes) > 0:
            if isinstance(episodes[0], Episode):
                self.episodes: List[Episode] = episodes
            else:  # type == dict
                self.episodes: List[Episode] = []
                for show in episodes:
                    self.episodes.append(Episode(**show))
        else:
            self.episodes = []


class Episode:
    """
    /groups/:id/shows/:name/episodes
    """

    def __init__(
        self,
        id: int,
        number: float,
        released: bool,
        air_date: str,
        updated_at: str,
        season: str,
        staff,
    ):
        self.id = id
        self.number = number
        self.released = released
        self.air_date = datetime.fromisoformat(air_date)
        self.updated_at = datetime.fromisoformat(updated_at)
        self.season = season
        if isinstance(staff, list) and len(staff) > 0:
            if isinstance(staff[0], Staff):
                self.staff: List[Staff] = staff
            else:  # type == dict
                self.staff: List[Staff] = []
                for show in staff:
                    self.staff.append(Staff(**show))
        else:
            self.staff = []


class Staff:
    """
    /groups/:id/shows/:name/staff
    """

    def __init__(self, id: int, finished: bool, updated_at: str, position, member):
        self.id = id
        self.finished = finished
        self.updated_at = datetime.fromisoformat(updated_at)
        if isinstance(position, Position):
            self.position = position
        else:  # type == dict
            self.position = Position(**position)


class Position:
    """
    /groups/:id/shows/:name/staff (position)
    """

    def __init__(self, id: int, name: str, acronym: str):
        self.id = id
        self.name = name
        self.acronym = acronym


def build():
    """
    Get data from API and bake HTML file
    """
    token: str = environ["DESCHTIMES_TOKEN"]
    build_time = datetime.now(tz=timezone.utc)
    endpoint = f"https://deschtimes.com/api/v1/groups/{token}.json"
    response = get(endpoint)
    group = Group(**loads(response.text))
    markdown_buffer = ""
    markdown_buffer += f"# {group.name}\n"
    # filter for incomplete show
    incomplete_shows = filter(lambda show: not show.complete, group.shows)
    # sort by newest update date
    sorted_incomplete_shows = list(
        reversed(sorted(incomplete_shows, key=lambda show: show.updated_at))
    )
    for show in sorted_incomplete_shows:
        markdown_buffer += f"## {show.name}\n"
        markdown_buffer += (
            f'- Updated <time datetime="{show.updated_at}">{show.updated_at}</time>\n'
        )
        # filter for aired episode
        aired_episodes = list(
            filter(lambda ep: ep.air_date <= build_time, show.episodes)
        )
        # filter for unreleased episode
        unreleased_aired_episodes = filter(lambda ep: not ep.released, aired_episodes)
        for episode in unreleased_aired_episodes:
            markdown_buffer += f"- Episode {episode.number}\n"
            markdown_buffer += f'- Aired <time datetime="{episode.air_date}">{episode.air_date}</time>\n'
            unfinished_staff = list(filter(lambda stf: not stf.finished, episode.staff))
            unfinished_staff_acronyms = list(
                map(lambda stf: stf.position.acronym, unfinished_staff)
            )
            markdown_buffer += f"- @ `{'`, `'.join(unfinished_staff_acronyms)}`\n"
            markdown_buffer += "\n"
            break
    html = '<!doctype html>\n<html lang="en">\n'
    html += '<head>\n<meta charset="utf-8">\n'
    html += '<link media="all" rel="stylesheet" href="style.css" />'
    html += "</head>\n"
    html += (
        '<script defer="defer" type="application/javascript" src="script.js"></script>'
    )
    html += "<body>"
    html += markdown(markdown_buffer)
    html += "\n</body>\n</html>\n"
    print(html)


if __name__ == "__main__":
    build()
