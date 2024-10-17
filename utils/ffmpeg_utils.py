import os
import subprocess
import flet as ft


def check_ffmpeg_installed(page: ft.Page):
    """Verifica se o FFmpeg está funcionando corretamente usando o binário local no Windows"""
    platform = page.platform

    if platform == ft.PagePlatform.WINDOWS:
        ffmpeg_path = os.path.join(
            os.getcwd(), "bin", "ffmpeg.exe"
        ) 
        if ffmpeg_path:
            print("FFmpeg encontrado!")
        else:
            print("FFmpeg não encontrado!")
            
        if os.path.isfile(ffmpeg_path):
            try:
                # Tenta executar o binário local do FFmpeg
                subprocess.run(
                    [ffmpeg_path, "-version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )
                snack_bar = ft.SnackBar(ft.Text("FFmpeg está instalado e funcionando!"))
                page.overlay.append(snack_bar)  
                snack_bar.open = True
            except subprocess.CalledProcessError as e:
                snack_bar = ft.SnackBar(ft.Text(f"Erro ao executar FFmpeg: {e}"))
                page.overlay.append(snack_bar)  
                snack_bar.open = True
        else:
            # Caso o binário não seja encontrado
            show_ffmpeg_not_found_dialog(page)
    else:
        snack_bar = ft.SnackBar(
            ft.Text("Plataforma não suportada para instalação automática de FFmpeg.")
        )
        page.overlay.append(snack_bar)  
        snack_bar.open = True
    page.update()


def show_ffmpeg_not_found_dialog(page: ft.Page):
    """Exibe um Snackbar se o FFmpeg não estiver instalado"""
    snack_bar = ft.SnackBar(ft.Text("FFmpeg não encontrado."), action="Instalar")
    snack_bar.on_action = lambda _: install_ffmpeg(page)
    page.overlay.append(snack_bar)  
    snack_bar.open = True
    page.update()


def install_ffmpeg(page: ft.Page):
    """Exibe instruções para o usuário instalar o FFmpeg manualmente"""
    snack_bar = ft.SnackBar(
        ft.Text("Por favor, baixe e adicione o binário do FFmpeg ao diretório 'bin'.")
    )
    page.overlay.append(snack_bar)
    snack_bar.open = True
    page.update()
