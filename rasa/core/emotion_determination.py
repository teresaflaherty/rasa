import requests
import logging


def determine_bot_emotion(user_message, matrix_on):
    twinword_url = "https://twinword-emotion-analysis-v1.p.rapidapi.com/analyze/"
    twinword_payload = f"text={user_message}"
    twinword_headers = {
        "content-type": "application/x-www-form-urlencoded",
        "x-rapidapi-key": "PUT_KEY_HERE",
        "x-rapidapi-host": "twinword-emotion-analysis-v1.p.rapidapi.com",
        "useQueryString": "True"
    }
    try:
        response = requests.post(twinword_url, data=twinword_payload, headers=twinword_headers).json()
        user_emotion_scores = response['emotion_scores']
        emotions_detected = response['emotions_detected']

        # # Mock data for testing purposes, limited Twinword calls allowed with free subscription
        # response = {
        #     "author": "twinword inc.",
        #     "email": "help@twinword.com",
        #     "emotion_scores": {
        #         "anger": 0.823453423423,
        #         "disgust": 0,
        #         "fear": 0,
        #         "joy": 0.13447999002654,
        #         "sadness": 0.022660050917593,
        #         "surprise": 0.0087308825457527
        #     },
        #     "emotions_detected": ["anger", "joy"],
        #     "result_code": "200",
        #     "result_msg": "Success",
        #     "version": "7.0.0"
        # }

    except():
        logging.exception('Twinword API currently unreachable.')
        user_emotion_scores = {
            "anger": 0,
            "disgust": 0,
            "fear": 0,
            "joy": 0,
            "sadness": 0,
            "surprise": 0
        }
        emotions_detected = []

    logging.info(f"Twinword analysis results: {user_emotion_scores}")

    if len(emotions_detected) > 0:
        user_emotion = [emotions_detected[0]]
    else:
        user_emotion = []

    if matrix_on:  # If integration with Gabriel's matrix is selected
        provide_emotions_url = "http://127.0.0.1:5000/emotions"
        provide_emotions_payload = {
            "emotion_scores": user_emotion_scores
        }
        provide_emotions_headers = {
            "content-type": "application/json"
        }

        requests.post(provide_emotions_url, json=provide_emotions_payload, headers=provide_emotions_headers)

        retrieve_state_url = "http://127.0.0.1:5000/poll"

        response = requests.get(retrieve_state_url, data={}, headers={}).json()

        bot_emotion_scores = {}
        # Emotion pairs in matrix poll response: [negative, positive]
        combined_emotions = [['anger', 'fear'], ['sadness', 'joy'], ['disgust', 'surprise']]
        for i in range(3):
            score = float(response["own_emotion"][i])
            if score < 0.000:  # If pair is negative, put abs value for negative and 0 for positive
                bot_emotion_scores[combined_emotions[i][0]] = float(abs(score))
                bot_emotion_scores[combined_emotions[i][1]] = 0
            elif score > 0.000:  # If pair is positive, put value for positive and 0 for negative
                bot_emotion_scores[combined_emotions[i][0]] = 0
                bot_emotion_scores[combined_emotions[i][1]] = float(score)
            else:  # If paired score is 0, put 0 for both emotions
                bot_emotion_scores[combined_emotions[i][0]] = 0
                bot_emotion_scores[combined_emotions[i][1]] = 0

        logging.info(f"Bot emotional scores from Gabriel: {bot_emotion_scores}")

        bot_emotion_scored = sorted(bot_emotion_scores.items(), key=lambda x: x[1], reverse=True)[0]

        if float(bot_emotion_scored[1]) > 0:
            bot_emotion = [bot_emotion_scored[0]]
        else:
            bot_emotion = []

    else:  # If integration with Gabriel's matrix is not selected, uses input emotion as output emotion
        bot_emotion = user_emotion

    logging.info(f"Determined Bot Emotion: {bot_emotion}")
    return user_emotion, bot_emotion
