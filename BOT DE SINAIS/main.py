import requests
import telebot
import time
from datetime import datetime
from fake_useragent import UserAgent

# Configurações iniciais
token = "7074825481:AAFmK2E3M1UzELTZKmLkO3D_7Jstf_rqDvU"  # Insira aqui o seu token do bot Telegram
chat_id = "-1002232201868"  # Insira aqui o chat_id do grupo ou usuário que receberá as mensagens
bot = telebot.TeleBot(token)
jogos_enviados = []


# Instância do UserAgent para simular um navegador
ua = UserAgent()


def obter_dados_api():
    url = "https://playscores.sportsat.app/gateway/api/v2/fixtures-svc/livescores?includes=league,stats,pressureStats&take=3000"
    headers = {
        "Accept": "application/json",
        "Origin": "https://www.playscores.com",
        "User-Agent": ua.random,
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("Erro ao obter dados da API:", e)
        return None

    def construir_mensagem(game, strategy):
        home_team = game["homeTeam"]["name"]
        away_team = game["awayTeam"]["name"]
        league = game["league"]["name"]
        home_score = game["scores"]["homeTeamScore"]
        away_score = game["scores"]["awayTeamScore"]
        minute = game["currentTime"]["minute"]
        convert_nome = home_team.replace(" ", "+")
        link_bet365 = f"https://www.bet365.com/#/AX/K%5E{convert_nome}/"

    # Detalhes estatísticos
    stats = {
        "home_exg": game["pressureStats"]["exg"]["home"],
        "away_exg": game["pressureStats"]["exg"]["away"],
        # Adicione mais estatísticas conforme necessário...
    }
    mensagem = f"""🔥 JOGO QUENTE 🔥

    🆚 <b>{home_team} x {away_team}</b>
    🏆 {league}
    ⏰ {minute}' minutos

    🚨 <b>{strategy}</b>

    📛 Odd recomendada: +1.50
    💰 Stake: 1% a 2%
    ⚠ Respeite sua meta diária!

    🔍 <b>Estatísticas(Casa - Fora):</b>
    📈 Placar: {home_score} - {away_score}
    ⛳ Escanteios: {game['stats']['corners']['home']} - {game['stats']['corners']['away']}

    📲 <a href="{link_bet365}">Bet365</a>"""

    return mensagem


def analisar_jogo(game):
    minute = game.get("currentTime", {}).get("minute")

    if minute is None or not isinstance(minute, int):
        return None

    home_score = game["scores"]["homeTeamScore"]
    away_score = game["scores"]["awayTeamScore"]
    score_difference = abs(home_score - away_score)

    if score_difference <= 1:

        pressure_stats = game.get("pressureStats")
        if pressure_stats is None:
            return None

        exg_home = pressure_stats.get("exg", {}).get("home", 0)
        exg_away = pressure_stats.get("exg", {}).get("away", 0)

        mh1_stats = pressure_stats.get("mh1", {})
        mh1_home = mh1_stats.get("home", 0)
        mh1_away = mh1_stats.get("away", 0)

        apm2_stats = pressure_stats.get("appm2", {})
        apm2_home = apm2_stats.get("home", 0)
        apm2_away = apm2_stats.get("away", 0)

        total_corners = game.get("stats", {}).get("corners", {})
        total_corners_home = total_corners.get("home", 0)
        total_corners_away = total_corners.get("away", 0)

        if exg_home > 1.5 and mh1_home > 50 and 50 <= minute <= 75:
            return "Over Gol Casa"

        if exg_away > 1.5 and mh1_away > 50 and 50 <= minute <= 75:
            return "Over Gol Fora"

        if apm2_home > 1 and total_corners_home < (minute / 10) and 30 <= minute <= 38:
            return "Over Cantos HT Casa"

        if apm2_away > 1 and total_corners_away < (minute / 10) and 30 <= minute <= 38:
            return "Over Cantos HT Fora"

        if apm2_home > 1 and total_corners_home < (minute / 10) and 80 <= minute <= 90:
            return "Over Cantos FT Casa"

        if apm2_away > 1 and total_corners_away < (minute / 10) and 80 <= minute <= 90:
            return "Over Cantos FT Fora"

    return None


def enviar_mensagem_telegram(mensagem, chat_id):
    try:
        bot.send_message(
            chat_id, mensagem, disable_web_page_preview=True, parse_mode="HTML"
        )
    except Exception as e:
        print("Erro ao enviar mensagem para o Telegram:", e)


def informar_ativacao(chat_id):
    mensagem = "Monitorando e realizando análises do Mercado."
    enviar_mensagem_telegram(mensagem, chat_id)


def verificar_dados_e_enviar(dados):
    if dados is None:
        return

    for game in dados["data"]:
        if game is None:
            continue
        fixture_id = game["fixtureId"]
        if fixture_id in jogos_enviados:
            continue

        strategy = analisar_jogo(game)
        if strategy:
            mensagem = construir_mensagem(game, strategy)
            enviar_mensagem_telegram(mensagem, chat_id)
            jogos_enviados.append(fixture_id)


def main():

    informar_ativacao(chat_id)
    while True:
        dados = obter_dados_api()
        verificar_dados_e_enviar(dados)
        time.sleep(180)  # Intervalo entre verificações


if __name__ == "__main__":
    main()
