from dataclasses import dataclass
from typing import NamedTuple


class Assignment(NamedTuple):
    lecturer_id: str
    room_id: str
    slot_id: str


@dataclass(frozen=True)
class Lecturer:
    id: str
    name: str
    available_slots: frozenset
    preferred_slots: frozenset
    max_load: int                


@dataclass(frozen=True)
class Room:
    id: str
    name: str
    capacity: int


@dataclass(frozen=True)
class Slot:
    id: str
    day: str
    start: int
    end: int


@dataclass(frozen=True)
class Section:
    id: str
    course: str
    sks: int
    size: int 
    eligible_lecturers: tuple
    group: str = "" 
    course_code: str = "" 

@dataclass
class Problem:
    lecturers: dict
    rooms: dict  
    slots: dict  
    sections: dict 