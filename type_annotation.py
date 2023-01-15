from dataclasses import dataclass


@dataclass
class Upload_photo:
    photo: str
    server: str
    hash_wall: str

@dataclass
class Save_photo:
    owner_id: str
    media_id: str