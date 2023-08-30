# Extração de e-mails e envio

Este repositório contém dois scripts Python que trabalham em conjunto para realizar a coleta de informações sobre vagas de emprego em um repositório GitHub, armazenar esses dados em um banco de dados MongoDB e, em seguida, enviar e-mails personalizados para as empresas.
*Atualmente somente issues com a label **Python** estão sendo buscadas.*

## Coletor de Informações de Vagas de Emprego (scraper.py)

O script "scraper.py" realiza a coleta de informações sobre vagas de emprego de um repositório GitHub. Ele utiliza a biblioteca "requests" para acessar as páginas do repositório, a biblioteca "BeautifulSoup" para fazer o parsing do conteúdo HTML e a biblioteca "pymongo" para interagir com o banco de dados MongoDB.

### Funcionalidades - Scraper

- Conecta-se a um banco de dados MongoDB para armazenar as informações coletadas.
- Realiza scraping das páginas do repositório para obter detalhes sobre as vagas de emprego.
- Armazena as informações relevantes, como número da vaga, status, título, data de atualização, etiquetas, autor, URL do autor, e-mail do autor e URL da vaga.
- Trata casos em que o e-mail não está disponível.
- Evita duplicações no banco de dados usando o número da vaga como chave única.

## Envio de E-mails para Candidatos (send.py)

O script "**send.py**" utiliza as informações armazenadas no banco de dados MongoDB para enviar e-mails personalizados para as empresas. Ele utiliza a biblioteca "**smtplib**" para enviar e-mails via SMTP e anexa um currículo em formato PDF ao e-mail.
> Atualmente estão sendo enviados 50 e-mails por vez, para evitar qualquer problema com o Gmail.

### Funcionalidades - Envio de e-mails

- Conecta-se a um banco de dados MongoDB para obter a lista de endereços de e-mail das empresas.
- Envia e-mails personalizados com o assunto e corpo definidos.
- Anexa um currículo em PDF ao e-mail.
- Atualiza o status de envio no banco de dados para evitar envios duplicados.

## Configuração

- Antes de usar os scripts, configure suas credenciais de e-mail e informações relacionadas no arquivo "**settings.py**".
- Certifique-se de ter as bibliotecas necessárias instaladas. Você pode instalá-las usando o seguinte comando:
`pip install -r requirements.txt`

## Uso

1. Execute o script "**scraper.py**" para coletar as informações das vagas de emprego e armazená-las no banco de dados MongoDB.
2. Adicione seu currículo a pasta "**cv**" com o nome "**curriculum.pdf**".
3. Em seguida, execute o script "**send.py**" para enviar e-mails personalizados para os candidatos interessados.

> Certifique-se de entender o funcionamento dos scripts e personalize-os conforme suas necessidades específicas. Lembre-se de respeitar as políticas de uso dos serviços utilizados, como GitHub e provedores de e-mail.
