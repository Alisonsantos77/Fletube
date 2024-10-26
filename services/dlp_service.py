import logging
from yt_dlp import YoutubeDL

# Configure logging para este módulo
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def download_with_ydl(ydl_opts, link):
    """
    Executa o download usando yt_dlp com as opções especificadas.

    Args:
        ydl_opts (dict): Opções para yt_dlp.
        link (str): A URL do vídeo a ser baixado.
    """
    logger.info("Iniciando download para link: %s", link)
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
    except Exception as e:
        logger.error("Ocorreu um erro durante o download para link %s: %s", link, e)
        raise e


def start_download(link, format, diretorio, progress_hook):
    """
    Configura as opções do yt_dlp com base no formato selecionado e inicia o download.

    Args:
        link (str): A URL do vídeo a ser baixado.
        format (str): O formato desejado para o download.
        directory (str): O diretório onde o download será salvo.
        progress_callback (callable): Uma função de callback para atualizar o progresso do download.
    """
    logger.info("Iniciando start_download")

    ydl_opts = {
        "format": f"bestvideo+bestaudio/best",
        "outtmpl": f"{diretorio}/%(title)s.%(ext)s",
        "progress_hooks": [progress_hook],
    }
    # Ajusta as opções de formato com base no formato selecionado
    if format in [
        "mp3",
        "wav",
        "m4a",
    ]:
        logger.info(f"Formatos de áudio selecionados: {format}")
        ydl_opts.update(
            {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": format,
                        "preferredquality": "192",
                    }
                ],
            }
        )
    elif format in [
        "mp4",
        "mkv",
        "webm",
    ]:
        logger.info(f"Formatos de vídeo selecionados: {format}")
        ydl_opts.update(
            {
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": format,
            }
        )
    else:
        logger.warning(f"Formato desconhecido, usando configuração padrão: {format}")
        ydl_opts.update({"format": "best"})

    logger.debug(f"ydl_opts configurados: {ydl_opts}")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
    except Exception as e:
        logger.error("Erro ao iniciar o download da playlist: %s", str(e))
        raise e
