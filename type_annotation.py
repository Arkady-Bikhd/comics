from dataclasses import dataclass


@dataclass
class UploadPhoto:
    photo: str
    server: str
    hash_wall: str

@dataclass
class SavePhoto:
    owner_id: str
    media_id: str