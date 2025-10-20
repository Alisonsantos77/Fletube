from loguru import logger
from yt_dlp import YoutubeDL


def download_with_ydl(ydl_opts, link):
    logger.info("Iniciando download para link: {}", link)
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            return info
    except Exception as e:
        logger.error("Ocorreu um erro durante o download para link {}: {}", link, e)
        raise e


def start_download(link, format, diretorio, progress_hook, is_playlist=False):
    ydl_opts = {
        "format": f"bestvideo+bestaudio/best",
        "outtmpl": f"{diretorio}/%(title)s.%(ext)s",
        "progress_hooks": [progress_hook],
        "noplaylist": not is_playlist,
        "ignoreerrors": True,
    }

    if format in ["mp3", "wav", "m4a"]:
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
    elif format in ["mp4", "mkv", "webm"]:
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
            info = ydl.extract_info(link, download=True)

            if info:
                # Para playlists, retorna info completa com entries
                if is_playlist and "entries" in info:
                    logger.info(
                        f"📋 Playlist detectada com {len(info['entries'])} vídeos"
                    )

                    # Processa cada entry para adicionar filepath
                    entries_with_filepath = []
                    for entry in info.get("entries", []):
                        if entry:
                            entry_data = {
                                "id": entry.get("id", ""),
                                "title": entry.get("title", "Título Indisponível"),
                                "thumbnail": entry.get("thumbnail", ""),
                                "filepath": ydl.prepare_filename(entry),
                            }
                            entries_with_filepath.append(entry_data)

                    return {
                        "entries": entries_with_filepath,
                        "title": info.get("title", "Playlist"),
                        "id": info.get("id", ""),
                    }

                # Para vídeos únicos
                else:
                    return {
                        "title": info.get("title", "Título Indisponível"),
                        "thumbnail": info.get("thumbnail", ""),
                        "filepath": ydl.prepare_filename(info),
                        "id": info.get("id", ""),
                    }

            return {}

    except Exception as e:
        logger.error("Erro ao iniciar o download: {}", str(e))
        raise e
