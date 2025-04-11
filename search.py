from update_leaderboards import leaderboard_cache
import logging

# Функция Форматирования в HTML
def format_leaderboard_html(leaderboard):
    message = '<b>Результаты поиска:</b>\n'
    message += '<pre><code>'
    message += 'Ранг | Никнейм      | Рейтинг \n'
    message += '-----|--------------|---------\n'
    for player in leaderboard:
        message += f"{player['rank']:>4} | {player['accountid']:<12} | {player['rating']:>6}\n"
    message += '</code></pre>'
    return message


# Функция поиска по никнейму
def search_nickname(selected_region, nickname):
    try:
        matching_players = [player for key, player in leaderboard_cache.items() if key[0] == selected_region and nickname.lower() in player['accountid'].lower()]
        if matching_players:
            formatted_message = format_leaderboard_html(matching_players[:20])
            return formatted_message
        else:
            return ('<b>Никнейм не найден.</b>\n'
                    'Попробуйте выполнить поиск по другой части никнейма')
    except Exception as e:
        logging.error(f"Error in search_nickname: {e}")
        return "<b>Ошибка при поиске.</b>"

# Функция поиска топ-20 игроков
def search_top20(selected_region):
    try:
        top_players = sorted([player for key, player in leaderboard_cache.items() if key[0] == selected_region], key=lambda x: x['rank'])[:20]
        formatted_message = format_leaderboard_html(top_players)
        return formatted_message
    except Exception as e:
        logging.error(f"Error in search_top20: {e}")
        return "<b>Ошибка при выводе топ-20 игроков.</b>"

