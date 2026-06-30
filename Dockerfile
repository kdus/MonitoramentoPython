# ********************************************************************************************************
# * Empresa        : SI Sistemas Inteligentes
# * Arquivo        : Dockerfile
# * Objetivo       : Imagem para rodar o Monitoramento VIAWEB (Python) em Linux/Docker 24/7
# ********************************************************************************************************

FROM python:3.11-slim

# Logs sem buffer (aparecem em tempo real no `docker logs`) e sem .pyc
# TZ define o fuso do relogio do container (afeta datetime.now()).
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=America/Sao_Paulo \
    APP_TIMEZONE=America/Sao_Paulo

# tzdata: necessario para o fuso horario local funcionar (datetime/zoneinfo)
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencias primeiro (melhor cache de build)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Codigo da aplicacao
COPY . .

# Garante a pasta de logs (sera sobreposta pelo volume em runtime)
RUN mkdir -p /app/logs

# Em Linux/Docker NAO usamos o iniciar.bat (que e Windows-only).
# O proprio main.py ja roda em loop continuo com auto-recovery.
CMD ["python", "-u", "main.py"]
