import yt_dlp
import logging

logger = logging.getLogger(__name__)


def extract_title_from_url(video_url):
    """
    Extrai o título de um vídeo do YouTube.

    Args:
        video_url (str): URL do vídeo do YouTube.

    Returns:
        str: Título do vídeo.

    Raises:
        ValueError: Se não for possível extrair o título.
    """
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "force_generic_extractor": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(video_url, download=False)
            title = info_dict.get("title")
            if title:
                return title
            else:
                raise ValueError("Título não encontrado.")
        except Exception as e:
            logger.error(f"Erro ao extrair título: {e}")
            raise ValueError("Erro ao extrair título.")
