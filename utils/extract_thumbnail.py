import yt_dlp
import logging

logger = logging.getLogger(__name__)


def extract_thumbnail_url(video_url):
    """
    Extrai a URL da thumbnail do primeiro vídeo em uma playlist do YouTube.

    Args:
        video_url (str): URL da playlist do YouTube.

    Returns:
        str: URL da thumbnail do primeiro vídeo na playlist.

    Raises:
        ValueError: Se não for possível extrair a thumbnail.
    """
    ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "playlist_items": "1",  
            "noplaylist": False,    
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(video_url, download=False)

            # Verifica se é uma playlist e tenta pegar a thumbnail do primeiro vídeo
            if "entries" in info_dict and info_dict["entries"]:
                first_video = info_dict["entries"][0]
                thumbnail_url = first_video.get("thumbnail")

                if thumbnail_url:
                    return thumbnail_url
                else:
                    # Se 'thumbnail' não estiver disponível, extraia informações detalhadas do primeiro vídeo
                    video_id = first_video.get('id')
                    if video_id:
                        video_info = ydl.extract_info(video_id, download=False)
                        thumbnail_url = video_info.get('thumbnail')
                        if thumbnail_url:
                            return thumbnail_url
                    raise ValueError("Thumbnail não encontrada para o primeiro vídeo da playlist.")
            else:
                raise ValueError("O link fornecido não é uma playlist ou não possui entradas.")
        except Exception as e:
            logger.error(f"Erro ao extrair thumbnail: {e}")
            raise ValueError("Erro ao extrair thumbnail.")