import yt_dlp
import logging

logger = logging.getLogger(__name__)


def extract_thumbnail_url(video_url):
    """
    Extrai a URL da thumbnail de um vídeo do YouTube.

    Args:
        video_url (str): URL do vídeo do YouTube.

    Returns:
        str: URL da thumbnail.

    Raises:
        ValueError: Se não for possível extrair a thumbnail.
    """
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "force_generic_extractor": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(video_url, download=False)
            thumbnail_url = info_dict.get("thumbnail")
            if thumbnail_url:
                return thumbnail_url
            else:
                raise ValueError("Thumbnail não encontrada.")
        except Exception as e:
            logger.error(f"Erro ao extrair thumbnail: {e}")
            raise ValueError("Erro ao extrair thumbnail.")
