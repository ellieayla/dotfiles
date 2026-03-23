#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
# ]
# ///

from datetime import datetime, timedelta
from random import choice
import subprocess
import typing
from dataclasses import dataclass, field

import json
from zoneinfo import ZoneInfo


Eastern = ZoneInfo("America/Toronto")


class ReminderFromJson(typing.TypedDict):
    dueDate: str
    externalId: str
    isCompleted: bool
    list: str
    notes: str
    priority: int
    title: str
    location: typing.Optional[str]
    locationTitle: typing.Optional[str]


@dataclass
class Location:
    lat: float
    lon: float
    name: typing.Optional[str]

    @classmethod
    def from_lat_lon(cls, lat_lon_str: str, name: typing.Optional[str]):
        lat, lon = lat_lon_str.split(", ")
        return cls(lat=float(lat), lon=float(lon), name=name)


def overdue(now: datetime, d: datetime) -> bool:
    start_today = now.replace(hour=0, minute=0, second=0)
    return d < start_today


def due_in_future(now: datetime, d: datetime) -> bool:
    end_today = now.replace(hour=23, minute=59)
    return d > end_today


def simple_due_date(d: typing.Optional[datetime]) -> str:
    if d is None:
        return "Someday"
    start_today = datetime.now(Eastern).astimezone().replace(hour=0, minute=0, second=0)
    end_today = start_today.replace(hour=23, minute=59)

    if start_today < d < end_today:
        return "Today"

    if start_today - timedelta(days=1) < d < start_today:
        return "Yesterday"

    if start_today + timedelta(days=1) < d < start_today + timedelta(days=2):
        return "Tomorrow"

    return d.strftime("%Y-%m-%d")


@dataclass(repr=False, order=True)
class Reminder:
    due: typing.Optional[datetime]
    title: str
    external_id: str
    completed: bool
    list: str
    notes: typing.Optional[str]
    location: typing.Optional[Location]

    @classmethod
    def from_json(cls, json_obj: ReminderFromJson):
        try:
            duedate_str = json_obj["dueDate"]
            if duedate_str.endswith("Z"):
                duedate_str = duedate_str[0:-1] + "+00:00"
            due = datetime.fromisoformat(duedate_str)
        except KeyError:
            due = None

        location: typing.Optional[Location] = None
        try:
            if json_obj["location"] is not None:
                location = Location.from_lat_lon(json_obj["location"], json_obj.get("locationTitle", None))
        except KeyError:
            location = None

        return cls(
            title=json_obj["title"],
            due=due,
            external_id=json_obj["externalId"],
            completed=json_obj["isCompleted"],
            list=json_obj["list"],
            notes=json_obj.get("notes", None),
            location=location,
        )

    def __repr__(self) -> str:
        link = repr(Hyperlink(url=reminder_url(self.external_id), text=simple_due_date(self.due)))
        first_chunk = f"{link} {self.title}"

        max_width = 120
        remaining_characters = max_width - len(first_chunk)

        everything_else = ""

        if self.list and self.list != "Reminders":
            everything_else += f" #{self.list}"
        if self.location:
            everything_else += f" @{self.location.name}"
        if self.notes:
            notes_without_newlines = self.notes.replace("\n\n", " ").replace("\n", "")
            everything_else += f" - {notes_without_newlines}"

        if remaining_characters > 20 and everything_else:
            # don't bother if it's tiny
            if len(everything_else) > remaining_characters:
                trailer = f"{everything_else[0: remaining_characters-4]} ..."  # +4
            else:
                trailer = everything_else
        else:
            trailer = ""

        return f"{first_chunk}{trailer}"


@dataclass(repr=False)
class Hyperlink:
    url: str
    text: str
    params: dict[str, str] = field(default_factory=dict)

    ESC = "\x1b"
    OSC_8 = f"{ESC}]8"
    ST = f"{ESC}\\"

    def __repr__(self) -> str:
        params = ":".join([f"{k}={v}" for (k, v) in self.params.items()])  # possibly (probably) empty string
        return f"{self.OSC_8};{params};{self.url}{self.ST}{self.text}{self.OSC_8};;{self.ST}"


def get_all_reminders() -> list[Reminder]:
    r = subprocess.check_output(["/opt/homebrew/bin/reminders", "show-all", "-f", "json"], text=True)
    obj: list[ReminderFromJson] = json.loads(r)

    return [Reminder.from_json(one_reminder_json) for one_reminder_json in obj]


def reminder_url(reminder_uuid: str) -> str:
    return f"x-apple-reminderkit://REMCDReminder/{reminder_uuid}"


def main() -> int:
    today = datetime.now(Eastern)

    a_r = get_all_reminders()

    if a_r:
        print("Reminders:")

    reminders_without_duedates = list([_ for _ in a_r if _.due is None])
    reminders_due_and_overdue = list([_ for _ in a_r if _.due is not None and not due_in_future(today, _.due)])

    for r in sorted(reminders_due_and_overdue):
        print(r)

    if len(reminders_due_and_overdue) < 5 and len(reminders_without_duedates) > 0:  # not too much to deal with
        print(choice(reminders_without_duedates))  # one random not-due item

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
