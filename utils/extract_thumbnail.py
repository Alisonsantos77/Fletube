import re


def extract_thumbnail_url(video_url):
    """
    Função que extrai o ID do vídeo da URL do YouTube e retorna a URL da thumbnail.

    Args:
        video_url (str): A URL do vídeo do YouTube.

    Returns:
        str: A URL da thumbnail.

    Raises:
        ValueError: Se a URL do vídeo for inválida e o ID não puder ser extraído.
    """
    video_id_pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(video_id_pattern, video_url)

    if match:
        video_id = match.group(1)
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        return thumbnail_url
    else:
        raise ValueError("URL de vídeo inválida. Não foi possível extrair o ID.")
