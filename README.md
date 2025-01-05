# Fletube 📥

**Fletube** é uma aplicação desenvolvida em **Flet Python** para realizar o download e gerenciamento de arquivos de áudio e vídeo de forma eficiente e intuitiva. O aplicativo permite configurar diretórios padrão, monitorar links na área de transferência e gerenciar o histórico de downloads.

## 🚀 Funcionalidades

1. **Downloads Personalizados**
   - Suporte para formatos como MP4, MP3, MKV, entre outros.
   - Configuração de diretório padrão para armazenar os arquivos baixados.
   - Monitoramento automático de links copiados para a área de transferência.

2. **Gerenciamento de Histórico**
   - Histórico completo com informações detalhadas dos downloads.
   - Opções para excluir itens individualmente ou limpar o histórico completo.
   - Função de desfazer exclusões recentes.

3. **Configurações Avançadas**
   - Personalização de tema (Claro/Escuro) e fontes.
   - Configuração de formato padrão de download.
   - Possibilidade de resetar as configurações para o estado inicial.

## 🖥️ Tecnologias Utilizadas

- **[Flet](https://flet.dev/)**: Framework principal para criar a interface gráfica.
- **Python 3.12**: Linguagem principal do projeto.
- **yt-dlp**: Biblioteca para gerenciar os downloads.
- **python-dotenv**: Gerenciamento de variáveis de ambiente.
- **cryptography**: Funções de encriptação e manipulação de dados.

## 🔧 Configuração do Ambiente

### Pré-requisitos

Certifique-se de ter o **Python 3.12** instalado em sua máquina.

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/Alisonsantos77/Fletube.git
   cd Fletube
   ```

2. Instale as dependências:
   ```bash
   pip install -q -U flet
   pip install -q -U yt-dlp
   pip install -q -U python-dotenv
   pip install -q -U cryptography
   ```

3. Configure o **FFmpeg** para suporte avançado de vídeo e áudio:

### ⚙️ Tutorial para Instalação do FFmpeg

#### **Windows**
1. Acesse o site oficial do FFmpeg e faça o download:
   [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html).

2. Escolha a versão para Windows e baixe o arquivo ZIP.

3. Após o download:
   - Extraia o conteúdo do arquivo ZIP para `C:\ffmpeg`.
   - Acesse as "Configurações do Sistema" e procure por **"Editar variáveis de ambiente do sistema"**.
   - Na seção **Variáveis de Ambiente**, localize a variável `Path` e clique em **Editar**.
   - Adicione `C:\ffmpeg\bin` como um novo caminho.

4. Verifique a instalação executando o comando:
   ```bash
   ffmpeg -version
   ```

Execute a aplicação com o seguinte comando:
```bash
flet run main.py
```

## 📚 Créditos e Autor

**Desenvolvido por:** Alison Santos  
Perfil do LinkedIn: [Alison Santos](https://www.linkedin.com/in/alisonsantosdev)  
GitHub: [Alisonsantos77](https://github.com/Alisonsantos77)

## 📜 Licença

Este projeto está licenciado sob a licença **MIT**. Consulte o arquivo `LICENSE` para mais detalhes.
