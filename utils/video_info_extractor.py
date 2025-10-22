from dataclasses import dataclass
from typing import Any, Dict, Optional

import yt_dlp

from utils.logging_config import setup_logging

logger = setup_logging()


@dataclass
class VideoInfo:
    title: str
    thumbnail: str
    duration: int
    uploader: str
    view_count: int
    upload_date: Optional[str] = None
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VideoInfo":
        return cls(
            title=data.get("title", "Título Indisponível"),
            thumbnail=data.get("thumbnail", ""),
            duration=data.get("duration", 0),
            uploader=data.get("uploader", "Desconhecido"),
            view_count=data.get("view_count", 0),
            upload_date=data.get("upload_date"),
            description=data.get("description"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "thumbnail": self.thumbnail,
            "duration": self.duration,
            "uploader": self.uploader,
            "view_count": self.view_count,
            "upload_date": self.upload_date,
            "description": self.description,
        }


class VideoInfoExtractor:
    BASE_OPTS = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
        "extract_flat": False,
        "no_warnings": True,
        "ignoreerrors": False,
    }

    @classmethod
    def extract_info(cls, url: str) -> VideoInfo:
        with yt_dlp.YoutubeDL(cls.BASE_OPTS) as ydl:
            try:
                logger.info(f"Extraindo informações de: {url[:50]}...")

                info_dict = ydl.extract_info(url, download=False)

                if "entries" in info_dict:
                    logger.warning("Playlist detectada, usando primeiro vídeo")
                    if not info_dict["entries"]:
                        raise ValueError("Playlist vazia")
                    info_dict = info_dict["entries"][0]

                video_info = VideoInfo.from_dict(info_dict)

                logger.info(f"Informações extraídas: {video_info.title}")

                return video_info

            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e).lower()

                if "private" in error_msg or "members-only" in error_msg:
                    raise ValueError("Vídeo privado ou exclusivo para membros")
                elif "unavailable" in error_msg or "removed" in error_msg:
                    raise ValueError("Vídeo indisponível ou removido")
                elif "copyright" in error_msg:
                    raise ValueError("Vídeo bloqueado por direitos autorais")
                else:
                    logger.error(f"Erro do yt-dlp: {e}")
                    raise ValueError(f"Erro ao acessar vídeo: {e}")

            except KeyError as e:
                logger.error(f"Campo obrigatório ausente: {e}")
                raise ValueError(f"Informações incompletas do vídeo")

            except Exception as e:
                logger.error(f"Erro inesperado: {e}", exc_info=True)
                raise ValueError(f"Erro ao processar vídeo: {e}")

    @classmethod
    def extract_thumbnail(cls, url: str) -> str:
        info = cls.extract_info(url)

        if not info.thumbnail:
            raise ValueError("Thumbnail não disponível para este vídeo")

        logger.info(f"Thumbnail extraída: {info.thumbnail[:60]}...")

        return info.thumbnail

    @classmethod
    def extract_title(cls, url: str) -> str:
        info = cls.extract_info(url)

        if not info.title or info.title == "Título Indisponível":
            raise ValueError("Título não disponível para este vídeo")

        logger.info(f"Título extraído: {info.title}")

        return info.title

    @classmethod
    def validate_url(cls, url: str) -> bool:
        opts = {**cls.BASE_OPTS, "extract_flat": True}

        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                ydl.extract_info(url, download=False)
                return True
            except Exception as e:
                logger.warning(f"URL inválida ou inacessível: {e}")
                return False
