import requests


def determine_bot_emotion(user_message, matrix_on):
    twinword_url = "https://twinword-emotion-analysis-v1.p.rapidapi.com/analyze/"
    twinword_payload = f"text={user_message}"
    twinword_headers = {
        "content-type": "application/x-www-form-urlencoded",
        "x-rapidapi-key": "0263ca96c6msh75411dda7a319f6p163b4ejsn186017d93146",
        "x-rapidapi-host": "twinword-emotion-analysis-v1.p.rapidapi.com",
        "useQueryString": "True"
    }

    response = requests.post(twinword_url, data=twinword_payload, headers=twinword_headers).json()
    print(response)
    user_emotion_scores = response['emotion_scores']

    if matrix_on:  # If integration with Gabriel's matrix is selected
        provide_emotions_url = "https://gabeurl.com/emotions"
        provide_emotions_payload = user_emotion_scores

        requests.post(provide_emotions_url, data=provide_emotions_payload, headers={})

        retrieve_state_url = "https://gabeurl.com/poll"

        response = requests.get(retrieve_state_url, data={}, headers={})

        bot_emotion_scores = {}
        # Emotion pairs in matrix poll response: [negative, positive]
        combined_emotions = [['anger', 'fear'], ['sadness', 'joy'], ['disgust', 'surprise']]
        for i in range(3):
            if response.emotion_in[i] < 0:  # If pair is negative, put abs value for negative emotion and 0 for positive
                bot_emotion_scores[combined_emotions[i][0]] = abs(response.own_emotion[i])
                bot_emotion_scores[combined_emotions[i][1]] = 0
            elif response.emotion_in[i] > 0:  # If pair is positive, put value for positive emotion and 0 for negative
                bot_emotion_scores[combined_emotions[i][0]] = 0
                bot_emotion_scores[combined_emotions[i][1]] = response.own_emotion[i]
            else:  # If paired score is 0, put 0 for both emotions
                bot_emotion_scores[combined_emotions[i][0]] = 0
                bot_emotion_scores[combined_emotions[i][1]] = 0

        bot_emotion = sorted(bot_emotion_scores.items(), key=lambda x: x[1], reverse=True)[0]

    else:  # If integration with Gabriel's matrix is not selected, uses input emotion as output emotion
        bot_emotion = sorted(user_emotion_scores.items(), key=lambda x: x[1], reverse=True)[0]

    return bot_emotion
