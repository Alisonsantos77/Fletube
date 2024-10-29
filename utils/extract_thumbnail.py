import yt_dlp
import logging

logger = logging.getLogger(__name__)


def extract_thumbnail_url(video_url):
    """
    Extrai a URL da thumbnail de um vídeo ou do primeiro vídeo de uma playlist do YouTube.

    Args:
        video_url (str): URL do vídeo ou da playlist do YouTube.

    Returns:
        str: URL da thumbnail.

    Raises:
        ValueError: Se não for possível extrair a thumbnail.
    """
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "playlist_items": "1",  # Se for playlist, pega apenas o primeiro vídeo
        "noplaylist": False,  # Permite playlists
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(video_url, download=False)

            # Verifica se é uma playlist com entradas
            if "entries" in info_dict and info_dict["entries"]:
                first_video = info_dict["entries"][0]
            else:
                # Se não for uma playlist, usa o próprio info_dict
                first_video = info_dict

            thumbnail_url = first_video.get("thumbnail")

            if thumbnail_url:
                return thumbnail_url
            else:
                raise ValueError("Thumbnail não encontrada.")

        except Exception as e:
            logger.error(f"Erro ao extrair thumbnail: {e}")
            raise ValueError("Erro ao extrair thumbnail.")
