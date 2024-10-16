import logging
import yt_dlp

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
    logger.info(f"Iniciando download para link: {link}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        logger.info(f"Download concluído para link: {link}")
    except Exception as e:
        logger.error(f"Ocorreu um erro durante o download para link {link}: {e}")
        raise e


def start_download(link, format, directory, progress_callback):
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
        "outtmpl": f"{directory}/%(title)s.%(ext)s",
        "progress_hooks": [progress_callback],
        "verbose": True,
    }

    # Ajusta as opções de formato com base no formato selecionado
    if format in ["mp3", "aac", "wav", "m4a", "opus"]:
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
    elif format in ["mp4", "mkv", "flv", "webm", "avi"]:
        ydl_opts.update(
            {
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": format,
            }
        )
    else:
        ydl_opts.update({"format": "best"})

    logger.debug(f"ydl_opts configurados: {ydl_opts}")

    try:
        download_with_ydl(ydl_opts, link)
    except Exception as e:
        logger.error(f"Erro ao iniciar o download: {e}")
        #TODO: Criar mais exceptions
        raise
